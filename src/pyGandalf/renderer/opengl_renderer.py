from pyGandalf.renderer.base_renderer import BaseRenderer
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib

from pyGandalf.scene.components import TransformComponent
from pyGandalf.scene.scene_manager import SceneManager

import OpenGL.GL as gl

import ctypes
import numpy as np

class OpenGLRenderer(BaseRenderer):    
    def initialize(cls):
        # Initialize OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)

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
        material.instance.set_uniform("u_Textures", np.array(samplers, dtype=np.int32))

        return 0

    def begin_frame(cls):
        gl.glClearColor(0.8, 0.5, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def end_frame(cls):
        pass
    
    def draw(cls, model, render_data, material):
        # Bind shader program
        gl.glUseProgram(material.instance.shader_program)
        
        # Bind textures
        OpenGLTextureLib().bind_textures()

        # Set Uniforms
        camera = SceneManager().get_main_camera()
        material.instance.set_uniform('u_Projection', camera.projection)
        material.instance.set_uniform('u_View', camera.view)
        material.instance.set_uniform('u_Model', model)

        camera_entity = SceneManager().get_main_camera_entity()
        if camera_entity != None:
            # TODO: update to get world position
            material.instance.set_uniform('u_ViewPosition', SceneManager().get_active_scene().get_component(camera_entity, TransformComponent).translation)

        if len(material.instance.textures) > 0:
            material.instance.set_uniform('u_TextureId', OpenGLTextureLib().get_slot(material.instance.textures[0]))
        
        # Bind vao
        gl.glBindVertexArray(render_data.vao)

        # Bind vertex buffer and their layout
        for index, attribute in enumerate(render_data.attributes):
            # Vertex Buffer Object (VBO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_data.vbo[index])

            # Set vertex buffer layout
            gl.glEnableVertexAttribArray(index)
            gl.glVertexAttribPointer(index, len(attribute[0]), gl.GL_FLOAT, gl.GL_FALSE, len(attribute[0]) * 4, ctypes.c_void_p(0))

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(render_data.attributes[0]) * 3)

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
        camera = SceneManager().get_main_camera()
        material.instance.set_uniform('u_Projection', camera.projection)
        material.instance.set_uniform('u_View', camera.view)
        material.instance.set_uniform('u_Model', model)

        camera_entity = SceneManager().get_main_camera_entity()
        if camera_entity != None:
            # TODO: update to get world position
            material.instance.set_uniform('u_ViewPosition', SceneManager().get_active_scene().get_component(camera_entity, TransformComponent).translation)

        if len(material.instance.textures) > 0:
            material.instance.set_uniform('u_TextureId', OpenGLTextureLib().get_slot(material.instance.textures[0]))

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

        gl.glDrawElements(gl.GL_TRIANGLES, len(render_data.indices) * 3, gl.GL_UNSIGNED_INT, None)

        # Unbind vao
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        # Unbind textures
        OpenGLTextureLib().unbind_textures()

        # Unbind shader program
        gl.glUseProgram(0)

    def clean(cls):
        pass

