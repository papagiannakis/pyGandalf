from pyGandalf.renderer.base_renderer import BaseRenderer
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib

from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import TransformComponent

from pyGandalf.systems.system import SystemState
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.utilities.logger import logger

import OpenGL.GL as gl
import numpy as np
import glm

import ctypes

class OpenGLRenderer(BaseRenderer):    
    def initialize(cls, *kargs):
        # Initialize OpenGL
        # gl.glEnable(gl.GL_BLEND);
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);
        # gl.glBlendEquation(gl.GL_FUNC_ADD);

        # gl.glEnable(gl.GL_CULL_FACE);
        # gl.glCullFace(gl.GL_BACK);
        # gl.glFrontFace(gl.GL_CCW);

        gl.glEnable(gl.GL_DEPTH_TEST);
        gl.glDepthFunc(gl.GL_LESS);

        cls.instance.use_framebuffer = kargs[0]
        cls.instance.framebuffer_id = 0
        cls.instance.color_attachment = 0
        cls.instance.depth_attachment = 0
        cls.instance.framebuffer_width = 0
        cls.instance.framebuffer_height = 0

        if cls.instance.use_framebuffer:
            cls.instance.invalidate_framebuffer(1280, 720)

    def resize(cls, width, height):
        gl.glViewport(0, 0, width, height)

    def add_batch(cls, render_data, material):
        # Vertex Array Object (VAO)
        render_data.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(render_data.vao)

        # Filter out None from attributes
        render_data.attributes = list(filter(lambda x: x is not None, render_data.attributes))

        for index, attribute in enumerate(render_data.attributes):
            # Get a pointer to the NumPy array data
            attribute_pointer = attribute.ctypes.data_as(ctypes.POINTER(gl.GLfloat))

            # Vertex Buffer Object (VBO)
            render_data.vbo.append(gl.glGenBuffers(1))
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_data.vbo[-1])
            gl.glBufferData(gl.GL_ARRAY_BUFFER, len(attribute) * len(attribute[0]) * 4, attribute_pointer, gl.GL_STATIC_DRAW)

            gl.glEnableVertexAttribArray(0)
            gl.glVertexAttribPointer(index, len(attribute[0]), gl.GL_FLOAT, gl.GL_FALSE, len(attribute[0]) * 4, ctypes.c_void_p(0))

        if render_data.indices is not None:
            # Get a pointer to the NumPy array data
            indices_pointer = render_data.indices.ctypes.data_as(ctypes.POINTER(gl.GLuint))
            
            # Element Buffer Object (EBO)
            render_data.ebo = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, render_data.ebo)
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(render_data.indices) * 3 * 4, indices_pointer, gl.GL_STATIC_DRAW)

        # Use the shader program
        gl.glUseProgram(material.instance.shader_program)

        # Create samplers if texture is in use
        samplers = []
        for i in range(0, 16):
            samplers.append(i)
        material.instance.set_uniform("u_Textures", np.asarray(samplers, dtype=np.int32))

        return 0

    def begin_frame(cls):
        if cls.instance.use_framebuffer:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, cls.instance.framebuffer_id)
            gl.glViewport(0, 0, int(cls.instance.framebuffer_width), int(cls.instance.framebuffer_height))

        gl.glClearColor(0.8, 0.5, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def end_frame(cls):
        if cls.instance.use_framebuffer:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def update_uniforms(cls, model, material):
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
            material.instance.set_uniform('u_LightPositions', glm.array(light_positions))
            material.instance.set_uniform('u_LightColors', glm.array(light_colors))
            material.instance.set_uniform('u_LightIntensities', np.asarray(light_intensities, dtype=np.float32))
            material.instance.set_uniform('u_LightCount', count)
            material.instance.set_uniform('u_Glossiness', material.glossiness)
        elif light_system is not None:
            material.instance.set_uniform('u_LightCount', 0)

        camera = SceneManager().get_main_camera()
        if camera != None:
            material.instance.set_uniform('u_Projection', camera.projection)
            material.instance.set_uniform('u_View', camera.view)
            material.instance.set_uniform('u_Model', model)
        else:
            material.instance.set_uniform('u_Projection', glm.mat4(1.0))
            material.instance.set_uniform('u_View', glm.mat4(1.0))
            material.instance.set_uniform('u_Model', glm.mat4(1.0))

        if material.instance.has_uniform('u_ViewPosition'):
            camera_entity = SceneManager().get_main_camera_entity()
            if camera_entity != None:
                camera_transform = SceneManager().get_active_scene().get_component(camera_entity, TransformComponent)
                if camera_transform != None:
                    material.instance.set_uniform('u_ViewPosition', camera_transform.get_world_position())

        if len(material.instance.textures) > 0:
            material.instance.set_uniform('u_TextureId', OpenGLTextureLib().get_slot(material.instance.textures[0]))

        if material.instance.has_uniform('u_Color'):
            material.instance.set_uniform('u_Color', material.color)
    
    def draw(cls, model, render_data, material):
        # Bind shader program
        gl.glUseProgram(material.instance.shader_program)
        
        # Bind textures
        OpenGLTextureLib().bind_textures()

        # Set Uniforms
        cls.instance.update_uniforms(model, material)
        
        # Bind vao
        gl.glBindVertexArray(render_data.vao)

        # Bind vertex buffer and their layout
        for index, attribute in enumerate(render_data.attributes):
            # Vertex Buffer Object (VBO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_data.vbo[index])

            # Set vertex buffer layout
            gl.glEnableVertexAttribArray(index)
            gl.glVertexAttribPointer(index, len(attribute[0]), gl.GL_FLOAT, gl.GL_FALSE, len(attribute[0]) * 4, ctypes.c_void_p(0))

        primitive = render_data.primitive if render_data.primitive != None else gl.GL_TRIANGLES

        gl.glDrawArrays(primitive, 0, len(render_data.attributes[0]) * 3)

        # Unbind vao
        gl.glBindVertexArray(0)

        # Unbind textures
        OpenGLTextureLib().unbind_textures()

        # Unbind shader program
        gl.glUseProgram(0)

    def draw_indexed(cls, model, render_data, material):
        # Bind shader program
        gl.glUseProgram(material.instance.shader_program)
        
        # Bind textures
        OpenGLTextureLib().bind_textures()

        # Set Uniforms
        cls.instance.update_uniforms(model, material)

        # Bind vao
        gl.glBindVertexArray(render_data.vao)

        # Bind ebo
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, render_data.ebo)

        # Bind vertex buffer and their layout
        for index, attribute in enumerate(render_data.attributes):
            # Vertex Buffer Object (VBO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_data.vbo[index])

            # Set vertex buffer layout
            gl.glEnableVertexAttribArray(index)
            gl.glVertexAttribPointer(index, len(attribute[0]), gl.GL_FLOAT, gl.GL_FALSE, len(attribute[0]) * 4, ctypes.c_void_p(0))

        primitive = render_data.primitive if render_data.primitive != None else gl.GL_TRIANGLES

        gl.glDrawElements(primitive, len(render_data.indices) * 3, gl.GL_UNSIGNED_INT, None)

        # Unbind vao
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        # Unbind textures
        OpenGLTextureLib().unbind_textures()

        # Unbind shader program
        gl.glUseProgram(0)

    def clean(cls):
        pass

    def invalidate_framebuffer(cls, width, height):
        cls.instance.framebuffer_width = width
        cls.instance.framebuffer_height = height

        if cls.instance.framebuffer_id:
            gl.glDeleteFramebuffers(1, np.array(cls.instance.framebuffer_id, dtype=np.uint))
            if cls.instance.color_attachment > -1:
                gl.glDeleteTextures(1, np.array(cls.instance.color_attachment, dtype=np.uint))
            if cls.instance.depth_attachment > -1:
                gl.glDeleteTextures(1, np.array(cls.instance.depth_attachment, dtype=np.uint))

        # Build the texture that will serve as the color attachment for the framebuffer.
        cls.instance.color_attachment = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cls.instance.color_attachment)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, int(width), int(height), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Build the texture that will serve as the depth attachment for the framebuffer.
        cls.instance.depth_attachment = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cls.instance.depth_attachment)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_DEPTH_COMPONENT24, int(width), int(height), 0, gl.GL_DEPTH_COMPONENT, gl.GL_UNSIGNED_INT, None)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Build the framebuffer.
        cls.instance.framebuffer_id = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, cls.instance.framebuffer_id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, cls.instance.color_attachment, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_TEXTURE_2D, cls.instance.depth_attachment, 0)

        status: gl.GLenum = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            logger.error(status)
            assert(False);

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def get_color_attachment(cls):
        return cls.instance.color_attachment
    
    def set_fill_mode(cls, mode):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, mode)
