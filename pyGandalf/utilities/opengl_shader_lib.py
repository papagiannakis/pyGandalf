import OpenGL.GL as gl

import re

class ShaderData:
    def __init__(self, shader_program, vertex_shader_code: str, fragment_shader_code: str):
        self.shader_program = shader_program
        self.vertex_shader_code = vertex_shader_code
        self.fragment_shader_code = fragment_shader_code

class OpenGLShaderLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLShaderLib, cls).__new__(cls)
            cls.instance.shaders : dict[str, ShaderData] = {} # type: ignore
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
            return cls.instance.shaders.get(name).shader_program

        shader_program = cls.instance.create_shader_program(vertex_shader_code, fragment_shader_code)
        cls.instance.shaders[name] = ShaderData(shader_program, vertex_shader_code, fragment_shader_code)
        
        return shader_program
    
    def parse(cls, shader_code):
        uniform_pattern = re.compile(r'uniform\s+(\w+)\s+(\w+)\s*')
        uniform_buffer_pattern = re.compile(r'layout\s*\(\s*std140\s*\)\s*uniform\s+(\w+)\s*{([^}]*)\s*};')
        uniform_array_pattern = re.compile(r'uniform\s+(\w+)\s+(\w+)\s*\[\s*(\d+)\s*\]\s*')

        uniforms = {}
        matches = uniform_pattern.findall(shader_code)
        for match in matches:
            uniforms[match[1]] = match[0]

        array_matches = uniform_array_pattern.findall(shader_code)
        for match in array_matches:
            array_type = match[0]
            array_name = match[1]
            array_size = int(match[2])
            uniforms[array_name] = f'{array_type}[{array_size}]'

        matches = uniform_buffer_pattern.findall(shader_code)
        for match in matches:
            buffer_name = match[0]
            buffer_content = match[1]
            buffer_uniforms = {}
            buffer_matches = uniform_pattern.findall(buffer_content)
            for buffer_match in buffer_matches:
                buffer_uniforms[buffer_match[1]] = buffer_match[0]
            uniforms[buffer_name] = buffer_uniforms
        
        return uniforms


    def get(cls, name: str):
        return cls.instance.shaders.get(name)
    
    def load_from_file(cls, path_to_source):
        """
        Returns the file contents as a string.
        """
        with open(path_to_source) as file:
            return file.read()