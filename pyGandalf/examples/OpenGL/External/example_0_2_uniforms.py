import glfw
import OpenGL.GL as gl

import ctypes
import platform

import glm
import numpy as np

from pyGandalf.utilities.definitions import SHADERS_PATH

# Vertices of the triangle
vertices = np.array([
    [-0.5, -0.5, 0.0], # 0 - Bottom left
    [ 0.5, -0.5, 0.0], # 1 - Bottom right
    [ 0.0,  0.5, 0.0], # 2 - Top middle
], dtype=np.float32)

def load_from_file(path_to_source):
    with open(path_to_source) as file:
        return file.read()

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)

    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(shader).decode('utf-8'))

    return shader

def on_create():
    # Vertex Array Object (VAO)
    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    # Get a pointer to the NumPy array data
    vertices_pointer = vertices.ctypes.data_as(ctypes.POINTER(gl.GLfloat))

    # Vertex Buffer Object (VBO)
    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices) * len(vertices[0]) * 4, vertices_pointer, gl.GL_STATIC_DRAW)

    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, len(vertices[0]), gl.GL_FLOAT, gl.GL_FALSE, len(vertices[0]) * 4, ctypes.c_void_p(0))

    # Read shaders
    vertex_shader_code = load_from_file(SHADERS_PATH / 'opengl' / 'unlit_simple.vs')
    fragment_shader_code = load_from_file(SHADERS_PATH / 'opengl' / 'unlit_simple.fs')

    # Compile shaders
    vertex_shader = compile_shader(vertex_shader_code, gl.GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_code, gl.GL_FRAGMENT_SHADER)

    # Attach shaders and link program
    shader_program = gl.glCreateProgram()
    gl.glAttachShader(shader_program, vertex_shader)
    gl.glAttachShader(shader_program, fragment_shader)
    gl.glLinkProgram(shader_program)

    if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(shader_program).decode('utf-8'))

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)

    return vao, vbo, shader_program

def on_update(vao, vbo, shader_program, t):
    # Bind vao
    gl.glBindVertexArray(vao)

    # Vertex Buffer Object (VBO)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

    # Set vertex buffer layout
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, len(vertices[0]), gl.GL_FLOAT, gl.GL_FALSE, len(vertices[0]) * 4, ctypes.c_void_p(0))

    # Bind shader program
    gl.glUseProgram(shader_program)

    # Set model, view and projection uniform
    uniform_location = gl.glGetUniformLocation(shader_program, 'u_ModelViewProjection')
    if uniform_location != -1:
        T = glm.translate(glm.mat4(1.0), glm.vec3(t, 0, 0))
        R = glm.quat(glm.vec3(glm.radians(0.0), glm.radians(0.0), glm.radians(0.0)))
        S = glm.scale(glm.mat4(1.0), glm.vec3(1, 1, 1))
        
        model = T * glm.mat4(R) * S
        view = glm.translate(glm.mat4(1.0), glm.vec3(0, 0, -3))
        projection = glm.perspective(glm.radians(40), 1.778, 0.1, 1000)
        mvp = projection * view * model
        gl.glUniformMatrix4fv(uniform_location, 1, gl.GL_FALSE, glm.value_ptr(mvp))

    # Draw triangle
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertices.size)

    # Unbind vao
    gl.glBindVertexArray(0)

    # Unbind shader program
    gl.glUseProgram(0)



def main():
    # Initialize GLFW
    if not glfw.init():
        print("GLFW could not be initialized!")
        exit(-1)

    # Set GLFW window hints
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    if platform.system() == "Darwin":
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE);

    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE);

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1280, 720, 'Triangle', None, None)
    if not window:
        print("OpenGL Window could not be created!")
        glfw.terminate()
        exit(-1)

    # Make the window's context current
    glfw.make_context_current(window)

    # Set vsync mode
    glfw.swap_interval(1)

    vao, vbo, shader_program = on_create()

    t = -1

    while not glfw.window_should_close(window):
        glfw.poll_events()
        gl.glClearColor(0.25, 0.25, 0.25, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)        
        t += 0.01
        on_update(vao, vbo, shader_program, t)
        glfw.swap_buffers(window)

    # Terminate GLFW
    glfw.terminate()

if __name__ == "__main__":
    main()