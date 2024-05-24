from pyGandalf.utilities.definitions import SHADERS_PATH

import OpenGL.GL as gl

import os
import re
from pathlib import Path

class ShaderData:
    def __init__(self, shader_program, name: str, vs_path: Path, fs_path: Path, tcs_path: Path, tes_path: Path, vs_code: str, fs_code: str, tcs_code: str, tes_code: str):
        self.name = name
        self.vs_path = vs_path
        self.fs_path = fs_path
        self.tcs_path = tcs_path
        self.tes_path = tes_path
        self.shader_program = shader_program
        self.vs_code = vs_code
        self.fs_code = fs_code
        self.tcs_code = tcs_code
        self.tes_code = tes_code

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

    def create_shader_program(cls, vertex_shader_code, fragment_shader_code, tessellation_control_shader_code=None, tessellation_evaluation_shader_code=None):
        vertex_shader = cls.instance.compile_shader(vertex_shader_code, gl.GL_VERTEX_SHADER)
        fragment_shader = cls.instance.compile_shader(fragment_shader_code, gl.GL_FRAGMENT_SHADER)

        if tessellation_control_shader_code != None:
            tessellation_control_shader = cls.instance.compile_shader(tessellation_control_shader_code, gl.GL_TESS_CONTROL_SHADER)
        if tessellation_evaluation_shader_code != None:
            tessellation_evaluation_shader = cls.instance.compile_shader(tessellation_evaluation_shader_code, gl.GL_TESS_EVALUATION_SHADER)

        shader_program = gl.glCreateProgram()
        gl.glAttachShader(shader_program, vertex_shader)
        gl.glAttachShader(shader_program, fragment_shader)
        if tessellation_control_shader_code != None:
            gl.glAttachShader(shader_program, tessellation_control_shader)
        if tessellation_evaluation_shader_code != None:
            gl.glAttachShader(shader_program, tessellation_evaluation_shader)
        gl.glLinkProgram(shader_program)

        if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
            raise RuntimeError(gl.glGetProgramInfoLog(shader_program).decode('utf-8'))

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)
        if tessellation_control_shader_code != None:
            gl.glDeleteShader(tessellation_control_shader)
        if tessellation_evaluation_shader_code != None:
            gl.glDeleteShader(tessellation_evaluation_shader)

        return shader_program
    
    def build(cls, name: str, vs_path: Path, fs_path: Path, tcs_path: Path=None, tes_path: Path=None) -> int:
        """Builds a new shader (if one does not already exists with that name) and returns its shader program.

        Args:
            name (str): The name of the shader
            vs_path (Path): The path to the vertex shader code
            fs_path (Path): The path to the fragment shader code

        Returns:
            int: The shader program
        """
        if cls.instance.shaders.get(name) != None:
            return cls.instance.shaders.get(name).shader_program
        
        vs_code = cls.instance.load_from_file(vs_path)
        fs_code = cls.instance.load_from_file(fs_path)
        tcs_code = None
        tes_code = None

        if tcs_path != None:
            tcs_code = cls.instance.load_from_file(tcs_path)
        if tes_path != None:
            tes_code = cls.instance.load_from_file(tes_path)

        vs_rel_path = Path(os.path.relpath(vs_path, SHADERS_PATH))
        fs_rel_path = Path(os.path.relpath(fs_path, SHADERS_PATH))
        tcs_rel_path = None
        tes_rel_path = None

        if tcs_path != None:
            tcs_rel_path = Path(os.path.relpath(tcs_path, SHADERS_PATH))
        if tcs_path != None:
            tes_rel_path = Path(os.path.relpath(tes_path, SHADERS_PATH))

        shader_program = cls.instance.create_shader_program(vs_code, fs_code, tcs_code, tes_code)
        cls.instance.shaders[name] = ShaderData(shader_program, name, vs_rel_path, fs_rel_path, tcs_rel_path, tes_rel_path, vs_code, fs_code, tcs_code, tes_code)
        
        return shader_program
    
    def parse(cls, shader_code: str) -> dict:
        """Parses the provided shader code and identifies all the uniforms along with their types.

        Args:
            shader_code (str): The source code of the shader to parse.

        Returns:
            dict: A dictionary holding the uniform name as a key and the uniform type as a value
        """
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


    def get(cls, name: str) -> ShaderData:
        """Gets the shader data of the given shader name.

        Args:
            name (str): The name of the shader to get its data.

        Returns:
            ShaderData: the shader data of the given shader name.
        """
        return cls.instance.shaders.get(name)
    
    def get_shaders(cls) -> dict[str, ShaderData]:
        """Returns the dictionary that holds all the shader data

        Returns:
            dict[str, ShaderData]: the dictionary that holds all the shader data
        """
        return cls.instance.shaders
    
    def load_from_file(cls, path_to_source):
        """
        Returns the file contents as a string.
        """
        with open(path_to_source) as file:
            return file.read()
        
    def clean(cls):
        cls.instance.shaders.clear()