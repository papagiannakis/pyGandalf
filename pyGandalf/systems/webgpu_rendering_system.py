from pyGandalf.systems.system import System, SystemState
from pyGandalf.scene.entity import Entity
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer, RenderPipelineDescription, RenderPassDescription, ColorAttachmentDescription
from pyGandalf.scene.components import Component, TransformComponent
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialInstance, CPUBuffer
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

import glm
import numpy as np

import hashlib

class WebGPUStaticMeshRenderingSystem(System):
    """
    The system responsible for rendering static meshes on WebGPU.
    """
    def __init__(self, filters: list[type]):
        super().__init__(filters)
        self.batches: dict[str, dict[str, list]] = {}

    def calculate_hash(self, attributes, indices, primitive):
        # Convert numpy arrays to their string representations
        attributes_str = ",".join([np.array2string(arr) for arr in attributes])
        indices_str = None if indices is None else np.array2string(indices)
        primitive_str = str(primitive)

        # Concatenate string representations
        combined_str = f"{attributes_str}_{indices_str}_{primitive_str}"

        # Compute hash value
        hash_value = hashlib.sha256(combined_str.encode()).hexdigest()

        return hash_value

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        mesh, material, transform = components

        # Retrieve and set the material instance
        material.instance = WebGPUMaterialLib().get(material.name)

        # Retrieve mesh data if loading from a model
        if mesh.attributes is None:
            mesh_instance = OpenGLMeshLib().get(mesh.name)
            mesh.attributes = [mesh_instance.vertices, mesh_instance.normals, mesh_instance.texcoords]
            mesh.indices = mesh_instance.indices

        # if there is nothing to render, return
        if len(mesh.attributes) == 0:
            return
        
        # Create render pipeline and buffers
        render_pipeline_desc = RenderPipelineDescription()
        render_pipeline_desc.render_data = mesh
        render_pipeline_desc.material_instance = material.instance
        WebGPURenderer().create_render_pipeline(render_pipeline_desc)
        WebGPURenderer().create_buffers(mesh)

        # Calculate mesh hash
        mesh.hash = self.calculate_hash(mesh.attributes, mesh.indices, mesh.primitive)

        # Categorize meshes based on material and then on mesh hash
        if material.name not in self.batches.keys():
            self.batches[material.name] = {}
        if mesh.hash not in self.batches[material.name].keys():
            self.batches[material.name][mesh.hash] = []
        
        self.batches[material.name][mesh.hash].append(components)

    def on_update_system(self, ts):
        base_pass_desc: RenderPassDescription = RenderPassDescription()
        color_attachment: ColorAttachmentDescription = ColorAttachmentDescription()
        color_attachment.view = WebGPURenderer().get_current_texture().create_view()
        color_attachment.clear_value = (WebGPURenderer().clear_color.r, WebGPURenderer().clear_color.g, WebGPURenderer().clear_color.b, WebGPURenderer().clear_color.a)
        base_pass_desc.depth_stencil_attachment=True
        base_pass_desc.depth_texture_view = WebGPURenderer().get_depth_texture_view()
        base_pass_desc.color_attachments.append(color_attachment)

        WebGPURenderer().begin_render_pass(base_pass_desc)
        for material in self.batches.keys():
            current_batch = self.batches[material]
            material_instance = WebGPUMaterialLib().get(material)
            # WebGPURenderer().set_pipeline(material_instance)

            self.set_uniforms(material_instance, current_batch.values())

            first_instance = 0

            for mesh_hash in current_batch.keys():
                current_mesh_group = current_batch[mesh_hash]

                mesh_group_size = len(current_mesh_group)

                mesh, material, _ = current_mesh_group[0]

                WebGPURenderer().set_pipeline(mesh)
                WebGPURenderer().set_buffers(mesh)
                WebGPURenderer().set_bind_groups(material)

                if mesh_group_size == 1:
                    if (mesh.indices is None):
                        WebGPURenderer().draw(mesh, 1, first_instance)
                    else:
                        WebGPURenderer().draw_indexed(mesh, 1, first_instance)
                    first_instance += 1
                else:
                    if (mesh.indices is None):
                        WebGPURenderer().draw(mesh, mesh_group_size)
                    else:
                        WebGPURenderer().draw_indexed(mesh, mesh_group_size)
                    first_instance = 0
        WebGPURenderer().end_render_pass()
    
    def set_uniforms(self, material_instance: MaterialInstance, meshes):
        if material_instance.has_uniform('u_UniformData'):
            uniform_data = material_instance.get_cpu_buffer_type('u_UniformData')

            from pyGandalf.scene.scene_manager import SceneManager
            camera = SceneManager().get_main_camera()
            if camera != None:
                if uniform_data.has_member("viewMatrix"):
                    uniform_data["viewMatrix"] = np.asarray(glm.transpose(camera.view))
                if uniform_data.has_member("projectionMatrix"):
                    uniform_data["projectionMatrix"] = np.asarray(glm.transpose(glm.perspectiveLH(glm.radians(camera.fov), camera.aspect_ratio, camera.near, camera.far)))
                if uniform_data.has_member("viewProjection"):
                    uniform_data["viewProjection"] = np.asarray(glm.transpose(glm.perspectiveLH(glm.radians(camera.fov), camera.aspect_ratio, camera.near, camera.far) * glm.mat4(glm.mat3(camera.view))))
            else:
                if uniform_data.has_member("viewMatrix"):
                    uniform_data["viewMatrix"] = np.identity(4)
                if uniform_data.has_member("projectionMatrix"):
                    uniform_data["projectionMatrix"] = np.identity(4)
                if uniform_data.has_member("viewProjection"):
                    uniform_data["viewProjection"] = np.identity(4)

            if uniform_data.has_member("objectColor"):
                uniform_data["objectColor"] = np.asarray(glm.vec4(1.0, 1.0, 1.0, 1.0))

            if uniform_data.has_member("viewPosition"):
                camera_entity = SceneManager().get_main_camera_entity()
                if camera_entity != None:
                    camera_transform = SceneManager().get_active_scene().get_component(camera_entity, TransformComponent)
                    if camera_transform != None:
                        uniform_data["viewPosition"] = np.asarray(glm.vec4(camera_transform.get_world_position(), 1.0))

            light_system: LightSystem = SceneManager().get_active_scene().get_system(LightSystem)

            light_positions: list[glm.vec4] = []
            light_colors: list[glm.vec4] = []
            light_intensities: list[glm.vec4] = []
            
            if light_system is not None:
                if light_system.get_state() != SystemState.PAUSE:
                    for components in light_system.get_filtered_components():
                        light, transform = components
                        light_colors.append(glm.vec4(light.color, 1.0))
                        light_positions.append(glm.vec4(transform.get_world_position(), 1.0))
                        light_intensities.append(glm.vec4(light.intensity, 1.0, 1.0, 1.0))

            count = len(light_positions)

            if count != 0:
                if uniform_data.has_member("lightPositions"):
                    uniform_data["lightPositions"] = np.ascontiguousarray(light_positions)
                if uniform_data.has_member("lightColors"):
                    uniform_data["lightColors"] = np.ascontiguousarray(light_colors)
                if uniform_data.has_member("lightIntensities"):
                    uniform_data["lightIntensities"] = np.ascontiguousarray(light_intensities)
                if uniform_data.has_member("lightCount"):
                    uniform_data["lightCount"] = np.float32(count)

            material_instance.set_uniform_buffer('u_UniformData', uniform_data)

        storage_data = material_instance.get_cpu_buffer_type('u_ModelData')

        if storage_data != None:
            if storage_data.has_member('modelMatrix'):
                object_data = np.zeros((512, 4, 4))

                i = 0
                for mesh in meshes:
                    for components in mesh:
                        _, _, transform = components
                        object_data[i] = glm.transpose(transform.world_matrix)
                        i += 1

                storage_data["modelMatrix"] = np.ascontiguousarray(object_data)

            if storage_data.has_member('inverseModelMatrix'):
                object_data = np.zeros((512, 4, 4))

                i = 0
                for mesh in meshes:
                    for components in mesh:
                        _, _, transform = components
                        object_data[i] = glm.transpose(glm.inverse(transform.world_matrix))
                        i += 1

                storage_data["inverseModelMatrix"] = np.ascontiguousarray(object_data)

            material_instance.set_storage_buffer('u_ModelData', storage_data)

        if material_instance.has_uniform('u_Texture'):
            material_instance.set_uniform('u_Texture')
