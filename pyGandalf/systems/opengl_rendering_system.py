from pyGandalf.core.application import Application
from pyGandalf.scene.components import Component, TransformComponent, MaterialComponent
from pyGandalf.systems.system import System, SystemState
from pyGandalf.systems.light_system import LightSystem
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureDescriptor
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.entity import Entity

import glm
import numpy as np
import OpenGL.GL as gl

class OpenGLStaticMeshRenderingSystem(System):
    """
    The system responsible for rendering.
    """

    def __init__(self, filters: list[type]):
        super().__init__(filters)
        self.pre_pass_material = None

    def on_create_system(self):
        self.SHADOW_WIDTH = 1024
        self.SHADOW_HEIGHT = 1024

        self.framebuffer_id = gl.glGenFramebuffers(1)

        depth_texture_descriptor = TextureDescriptor()
        depth_texture_descriptor.width=self.SHADOW_WIDTH
        depth_texture_descriptor.height=self.SHADOW_HEIGHT
        depth_texture_descriptor.internal_format=gl.GL_DEPTH_COMPONENT
        depth_texture_descriptor.format=gl.GL_DEPTH_COMPONENT
        depth_texture_descriptor.type=gl.GL_FLOAT
        depth_texture_descriptor.wrap_s=gl.GL_CLAMP_TO_BORDER
        depth_texture_descriptor.wrap_t=gl.GL_CLAMP_TO_BORDER
        depth_texture_descriptor.min_filter=gl.GL_NEAREST
        depth_texture_descriptor.max_filter=gl.GL_NEAREST

        # Create depth texture
        OpenGLTextureLib().build('depth_texture', img_data=None, descriptor=depth_texture_descriptor)
        depth_texture_id = OpenGLTextureLib().get_id('depth_texture')

        gl.glBindTexture(gl.GL_TEXTURE_2D, depth_texture_id)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_TEXTURE_2D, depth_texture_id, 0)
        gl.glDrawBuffer(gl.GL_NONE)
        gl.glReadBuffer(gl.GL_NONE)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

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
        if OpenGLRenderer().get_shadows_enabled():
            # Create the depth only pre-pass material is not already created
            if self.pre_pass_material == None:
                self.pre_pass_material = MaterialComponent('M_DepthPrePass')
                self.pre_pass_material.instance = OpenGLMaterialLib().get('M_DepthPrePass')

            OpenGLRenderer().resize(self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

            # Depth only pre-pass
            for components in self.get_filtered_components():
                mesh, entity_material, transform = components

                if entity_material.instance.descriptor.cast_shadows == False:
                    continue

                # Bind vao
                OpenGLRenderer().set_pipeline(mesh)
                # Bind vbo(s) and ebo
                OpenGLRenderer().set_buffers(mesh)
                # Bind shader program and set material properties
                OpenGLRenderer().set_bind_groups(self.pre_pass_material)

                self.update_prepass_uniforms(transform.world_matrix, self.pre_pass_material)

                if (mesh.indices is None):
                    OpenGLRenderer().draw(mesh, self.pre_pass_material)
                else:
                    OpenGLRenderer().draw_indexed(mesh, self.pre_pass_material)

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            if OpenGLRenderer().use_framebuffer:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, OpenGLRenderer().framebuffer_id)
                OpenGLRenderer().resize(int(OpenGLRenderer().framebuffer_width), int(OpenGLRenderer().framebuffer_height))
            else:
                OpenGLRenderer().resize(Application().get_window().width, Application().get_window().height)

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Color pass
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

    def update_prepass_uniforms(self, model, material: MaterialComponent):
        light_system: LightSystem = SceneManager().get_active_scene().get_system(LightSystem)
        
        if light_system is not None:
            if light_system.get_state() != SystemState.PAUSE:
                for components in light_system.get_filtered_components():
                    light, transform = components

                    if material.instance.has_uniform('u_LightSpaceMatrix'):
                        light_projection = SceneManager().get_main_camera().projection
                        light_view = glm.lookAt(transform.get_world_position(), glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
                        material.instance.set_uniform('u_LightSpaceMatrix', light_projection * light_view)

                    break

        if material.instance.has_uniform('u_Model'):
            material.instance.set_uniform('u_Model', model)

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

                    # NOTE: Only works with one light, adding more will keep the last.
                    if material.instance.has_uniform('u_LightSpaceMatrix'):
                        light_projection = SceneManager().get_main_camera().projection
                        light_view = glm.lookAt(transform.get_world_position(), glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
                        material.instance.set_uniform('u_LightSpaceMatrix', light_projection * light_view)

        count = len(light_positions)

        assert count <= 16, f"Maximum supported lights for WebGPU backend are 16, but {count} are defined"

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
                material.instance.set_uniform('u_Glossiness', material.instance.data.glossiness)
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
            material.instance.set_uniform('u_Color', material.instance.data.color.rgb)