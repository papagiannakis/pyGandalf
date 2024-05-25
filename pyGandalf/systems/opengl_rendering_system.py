from pyGandalf.scene.components import Component, TransformComponent, MaterialComponent
from pyGandalf.systems.system import System, SystemState
from pyGandalf.systems.light_system import LightSystem
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.entity import Entity

import glm
import numpy as np

class OpenGLStaticMeshRenderingSystem(System):
    """
    The system responsible for rendering.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        mesh, material, transform = components

        mesh.vao = 0
        mesh.ebo = 0
        mesh.vbo.clear()

        material.instance = OpenGLMaterialLib().get(material.name)

        if mesh.load_from_file == True:
            mesh_instance = OpenGLMeshLib().get(mesh.name)
            mesh.attributes = [mesh_instance.vertices, mesh_instance.normals, mesh_instance.texcoords]
            mesh.indices = mesh_instance.indices

        if len(mesh.attributes) == 0:
            return
        
        mesh.batch = OpenGLRenderer().add_batch(mesh, material)

    def on_update_system(self, ts: float):
        
        for components in self.get_filtered_components():
            mesh, material, transform = components

            # Bind vao
            OpenGLRenderer().set_pipeline(mesh)
            # Bind vbo(s) and ebo
            OpenGLRenderer().set_buffers(mesh)
            # Bind shader program and set material properties
            OpenGLRenderer().set_bind_groups(material)

            self.update_uniforms(transform.world_matrix, material)

            if (mesh.indices is None):
                OpenGLRenderer().draw(mesh, material)
            else:
                OpenGLRenderer().draw_indexed(mesh, material)

    def update_uniforms(self, model, material: MaterialComponent):
        light_system: LightSystem = SceneManager().get_active_scene().get_system(LightSystem)

        light_positions: list[glm.vec3] = []
        light_colors: list[glm.vec3] = []
        light_intensities: list[np.float32] = []
        
        if light_system is not None:
            if light_system.get_state() != SystemState.PAUSE:
                for components in light_system.get_filtered_components():
                    light, transform = components
                    light_colors.append(light.color)
                    light_positions.append(transform.get_world_position())
                    light_intensities.append(light.intensity)

        count = len(light_positions)

        if count != 0:
            if material.instance.has_uniform('u_LightPositions'):
                material.instance.set_uniform('u_LightPositions', glm.array(light_positions))
            if material.instance.has_uniform('u_LightColors'):
                material.instance.set_uniform('u_LightColors', glm.array(light_colors))
            if material.instance.has_uniform('u_LightIntensities'):
                material.instance.set_uniform('u_LightIntensities', np.asarray(light_intensities, dtype=np.float32))
            if material.instance.has_uniform('u_LightCount'):
                material.instance.set_uniform('u_LightCount', count)
            if material.instance.has_uniform('u_Glossiness'):
                material.instance.set_uniform('u_Glossiness', material.glossiness)
        elif light_system is not None:
            if material.instance.has_uniform('u_LightCount'):
                material.instance.set_uniform('u_LightCount', 0)

        camera = SceneManager().get_main_camera()
        if camera != None:
            if material.instance.has_uniform('u_ModelViewProjection'):
                material.instance.set_uniform('u_ModelViewProjection', camera.projection * camera.view * model)
            if material.instance.has_uniform('u_Model'):
                material.instance.set_uniform('u_Model', model)
            if material.instance.has_uniform('u_View'):
                material.instance.set_uniform('u_View', camera.view)
            if material.instance.has_uniform('u_Projection'):
                material.instance.set_uniform('u_Projection', camera.projection)
            if material.instance.has_uniform('u_ViewProjection'):
                material.instance.set_uniform('u_ViewProjection', camera.projection * glm.mat4(glm.mat3(camera.view)))
        else:
            if material.instance.has_uniform('u_ModelViewProjection'):
                material.instance.set_uniform('u_ModelViewProjection', glm.mat4(1.0))
            if material.instance.has_uniform('u_Model'):
                material.instance.set_uniform('u_Model', glm.mat4(1.0))
            if material.instance.has_uniform('u_View'):
                material.instance.set_uniform('u_View', glm.mat4(1.0))
            if material.instance.has_uniform('u_Projection'):
                material.instance.set_uniform('u_Projection', glm.mat4(1.0))
            if material.instance.has_uniform('u_ViewProjection'):
                material.instance.set_uniform('u_ViewProjection', glm.mat4(1.0))

        if material.instance.has_uniform('u_ViewPosition'):
            camera_entity = SceneManager().get_main_camera_entity()
            if camera_entity != None:
                camera_transform = SceneManager().get_active_scene().get_component(camera_entity, TransformComponent)
                if camera_transform != None and not camera_transform.static:
                    material.instance.set_uniform('u_ViewPosition', camera_transform.get_world_position())

        if material.instance.has_uniform('u_Color'):
            material.instance.set_uniform('u_Color', material.color)