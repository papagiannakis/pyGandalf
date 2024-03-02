from utilities.texture_lib import TextureLib
from utilities.logger import logger

import OpenGL.GL as gl

import ctypes
import numpy as np

class OpenGLRenderer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLRenderer, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance
    
    def set_initialized(cls, initialised):
        cls.instance.initialized = initialised

    def is_initialized(cls):
        return cls.instance.initialized
    
    def initialize(cls):
        # Initialize OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)

    def add_batch(cls, render_data, material):
        # Vertex Array Object (VAO)
        render_data.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(render_data.vao)

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
        texture_uniform_location = gl.glGetUniformLocation(material.instance.shader_program, "u_Textures")
        if texture_uniform_location != -1:
            samplers = []
            for i in range(0, 32):
                samplers.append(i)

            gl.glUniform1iv(texture_uniform_location, 32, np.array(samplers, dtype=np.int32))
        else:
            logger.warning(f'Could find u_Textures uniform for material: {material.name}!')

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
        TextureLib().bind_textures()

        # Set Uniforms
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(material.instance.shader_program, "model"), 1, gl.GL_FALSE, model)
        gl.glUniform4f(gl.glGetUniformLocation(material.instance.shader_program, "u_Color"), 1.0, 0.0, 0.0, 1.0)

        if len(material.instance.textures) > 0:
            texture_id_uniform_location = gl.glGetUniformLocation(material.instance.shader_program, "u_TextureId")
            if texture_id_uniform_location != -1:
                gl.glUniform1f(texture_id_uniform_location, TextureLib().get_slot(material.instance.textures[0]))
            else:
                logger.warning(f'Could find u_TextureId uniform for material: {material.name}!')

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
        TextureLib().unbind_textures()

        # Unbind shader program
        gl.glUseProgram(0)

    def draw_indexed(cls, model, render_data, material):
        # Bind shader program
        gl.glUseProgram(material.instance.shader_program)
        
        # Bind textures
        TextureLib().bind_textures()

        # Set Uniforms
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(material.instance.shader_program, "model"), 1, gl.GL_FALSE, model)
        gl.glUniform4f(gl.glGetUniformLocation(material.instance.shader_program, "u_Color"), 1.0, 0.0, 0.0, 1.0)

        if len(material.instance.textures) > 0:
            texture_id_uniform_location = gl.glGetUniformLocation(material.instance.shader_program, "u_TextureId")
            if texture_id_uniform_location != -1:
                gl.glUniform1f(texture_id_uniform_location, TextureLib().get_slot(material.instance.textures[0]))
            else:
                logger.warning(f'Could find u_TextureId uniform for material: {material.name}!')

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, render_data.ebo)

        # Bind vao
        gl.glBindVertexArray(render_data.vao)

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
        TextureLib().unbind_textures()

        # Unbind shader program
        gl.glUseProgram(0)

    def clean(cls):
        pass

