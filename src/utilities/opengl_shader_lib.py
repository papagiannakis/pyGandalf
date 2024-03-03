import OpenGL.GL as gl
import os

class OpenGLShaderLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLShaderLib, cls).__new__(cls)
            cls.instance.shaders = {}
        return cls.instance
    
    def compile_shader(cls, source, shader_type):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)

        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            raise RuntimeError(gl.glGetShaderInfoLog(shader).decode('utf-8'))

        return shader

    def create_shader_program(cls, vertex_shader_code, fragment_shader_code):
        vertex_shader = cls.instance.compile_shader(vertex_shader_code, gl.GL_VERTEX_SHADER)
        fragment_shader = cls.instance.compile_shader(fragment_shader_code, gl.GL_FRAGMENT_SHADER)

        shader_program = gl.glCreateProgram()
        gl.glAttachShader(shader_program, vertex_shader)
        gl.glAttachShader(shader_program, fragment_shader)
        gl.glLinkProgram(shader_program)

        if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
            raise RuntimeError(gl.glGetProgramInfoLog(shader_program).decode('utf-8'))

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        return shader_program
    
    def build(cls, name: str, vertex_shader_code: str, fragment_shader_code: str):
        if cls.instance.shaders.get(name) != None:
            return cls.instance.shaders.get(name)

        shader_program = cls.instance.create_shader_program(vertex_shader_code, fragment_shader_code)
        cls.instance.shaders[name] = shader_program
        
        return shader_program

    def get(cls, name: str):
        return cls.instance.shaders.get(name)
    
    def load_from_file(cls, source):
        """
        Returns the file contents as a string.
        """
        path = os.path.join(os.getcwd(), source)

        with open(path) as file:
            return file.read()