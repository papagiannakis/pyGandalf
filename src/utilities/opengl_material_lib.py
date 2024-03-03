from utilities.opengl_shader_lib import OpenGLShaderLib
from utilities.logger import logger

import OpenGL.GL as gl

import re
import numpy as np

class MaterialInstance:
    def __init__(self, name, shader_program, textures, shader_params = []):
        self.name = name
        self.shader_program = shader_program
        self.textures = textures
        self.shader_params = shader_params

    def set_uniform(self, uniform_name, uniform_data):
        uniform_location = gl.glGetUniformLocation(self.shader_program, uniform_name)
        if uniform_location != -1:
            self.update_uniform(uniform_location, uniform_name, uniform_data)
        else:
            self.uniform_not_found(uniform_name)

    def update_uniform(self, uniform_location, uniform_name, uniform_data):
        uniform_type = self.shader_params[uniform_name]
        match uniform_type:
            case 'float':
                assert isinstance(uniform_data, float), f"Uniform type with name: {uniform_name} is not a floating point number"
                gl.glUniform1f(uniform_location, uniform_data)
                return
            case 'int':
                assert isinstance(uniform_data, int), f"Uniform type with name: {uniform_name} is not an integer number"
                gl.glUniform1i(uniform_location, uniform_data)
                return
            case 'sampler2D':
                assert isinstance(uniform_data, int), f"Uniform type with name: {uniform_name} is not an integer number"
                gl.glUniform1i(uniform_location, uniform_data)
                return
            case 'vec2':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (2,), f"Uniform type with name: {uniform_name} is not a 2x1 NumPy Array of float32 type"
                gl.glUniform2f(uniform_location, uniform_data[0], uniform_data[1])
                return
            case 'vec3':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (3,), f"Uniform type with name: {uniform_name} is not a 3x1 NumPy Array of float32 type"
                gl.glUniform3f(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2])
                return
            case 'vec4':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (4,), f"Uniform type with name: {uniform_name} is not a 4x1 NumPy Array of float32 type"
                gl.glUniform4f(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2], uniform_data[3])
                return
            case 'ivec2':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (2,), f"Uniform type with name: {uniform_name} is not a 2x1 NumPy Array of int32 type"
                gl.glUniform2i(uniform_location, uniform_data[0], uniform_data[1])
                return
            case 'ivec3':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (3,), f"Uniform type with name: {uniform_name} is not a 3x1 NumPy Array of int32 type"
                gl.glUniform3i(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2])
                return
            case 'ivec4':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (4,), f"Uniform type with name: {uniform_name} is not a 4x1 NumPy Array of int32 type"
                gl.glUniform4ui(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2], uniform_data[3])
                return
            case 'uvec2':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (2,), f"Uniform type with name: {uniform_name} is not a 2x1 NumPy Array of uint32 type"
                gl.glUniform2ui(uniform_location, uniform_data[0], uniform_data[1])
                return
            case 'uvec3':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (3,), f"Uniform type with name: {uniform_name} is not a 3x1 NumPy Array of uint32 type"
                gl.glUniform3ui(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2])
                return
            case 'uvec4':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (4,), f"Uniform type with name: {uniform_name} is not a 4x1 NumPy Array of uint32 type"
                gl.glUniform4ui(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2], uniform_data[3])
                return
            case 'dvec2':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (2,), f"Uniform type with name: {uniform_name} is not a 2x1 NumPy Array of double type"
                gl.glUniform2d(uniform_location, uniform_data[0], uniform_data[1])
                return
            case 'dvec3':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (3,), f"Uniform type with name: {uniform_name} is not a 3x1 NumPy Array of double type"
                gl.glUniform3d(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2])
                return
            case 'dvec4':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (4,), f"Uniform type with name: {uniform_name} is not a 4x1 NumPy Array of double type"
                gl.glUniform4d(uniform_location, uniform_data[0], uniform_data[1], uniform_data[2], uniform_data[3])
                return
            case 'mat2':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (2,2), f"Uniform type with name: {uniform_name} is not a 2x2 NumPy Matrix type"
                gl.glUniformMatrix2fv(uniform_location, 1, gl.GL_FALSE, uniform_data)
                return
            case 'mat3':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (3,3), f"Uniform type with name: {uniform_name} is not a 3x3 NumPy Matrix type"
                gl.glUniformMatrix3fv(uniform_location, 1, gl.GL_FALSE, uniform_data)
                return
            case 'mat4':
                assert isinstance(uniform_data, np.ndarray) and uniform_data.shape == (4,4), f"Uniform type with name: {uniform_name} is not a 4x4 NumPy Matrix type"
                gl.glUniformMatrix4fv(uniform_location, 1, gl.GL_FALSE, uniform_data)
                return

        if 'int[' in uniform_type or 'sampler2D[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) == count and isinstance(uniform_data[0], np.int32), f"Uniform type with name: {uniform_name} is not an array of {count} integers"
                gl.glUniform1iv(uniform_location, count, uniform_data)
        elif 'float[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) == count and isinstance(uniform_data[0], np.float32), f"Uniform type with name: {uniform_name} is not an array of {count} floats"
                gl.glUniform1fv(uniform_location, count, uniform_data)
        elif 'mat2[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) == count and isinstance(uniform_data[0], np.ndarray) and uniform_data.shape == (2,2), f"Uniform type with name: {uniform_name} is not an array of {count} 2x2 NumPy Matrices"
                gl.glUniformMatrix2fv(uniform_location, count, gl.GL_FALSE, uniform_data)
        elif 'mat3[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) == count and isinstance(uniform_data[0], np.ndarray) and uniform_data.shape == (3,3), f"Uniform type with name: {uniform_name} is not an array of {count} 3x3 NumPy Matrices"
                gl.glUniformMatrix3fv(uniform_location, count, gl.GL_FALSE, uniform_data)
        elif 'mat4[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) == count and isinstance(uniform_data[0], np.ndarray) and uniform_data.shape == (4,4), f"Uniform type with name: {uniform_name} is not an array of {count} 4x4 NumPy Matrices"
                gl.glUniformMatrix4fv(uniform_location, count, gl.GL_FALSE, uniform_data)

    def uniform_not_found(self, uniform_name):
        logger.debug(f'Could find {uniform_name} uniform for material: {self.name}!\n These are the available uniforms for shader with id {self.shader_program}:\n {self.shader_params}')
    
    def print_available_uniforms(self):
        logger.log(f'Available uniforms for material: {self.name} and shader id {self.shader_program}:\n {self.shader_params}')

class MaterialData:
    def __init__(self, base_template, textures):
        self.base_template = base_template
        self.textures = textures

    def __eq__(self, other):
        if self.base_template != other.base_template:
            return False
        if len(self.textures) != len(other.textures):
            return False
        for i in range(len(self.textures)):
            if (self.textures[i] != other.textures[i]):
                return False
        return True
    
    def __hash__(self):
        return hash((self.base_template, len(self.textures), tuple(texture for texture in self.textures)))

class OpenGLMaterialLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLMaterialLib, cls).__new__(cls)
            cls.instance.cached_materials: dict[MaterialData, MaterialInstance] = {} # type: ignore
            cls.instance.materials: dict[str, MaterialInstance] = {} # type: ignore
        return cls.instance
    
    def build(cls, name: str, data: MaterialData):
        if cls.instance.cached_materials.get(data) != None:
            material = cls.instance.cached_materials[data]
            cls.instance.materials[name] = material
            return material

        shader_data = OpenGLShaderLib().get(data.base_template)

        shader_program = shader_data.shader_program
        shader_params_vertex = OpenGLShaderLib().parse(shader_data.vertex_shader_code)
        shader_params_fragment = OpenGLShaderLib().parse(shader_data.fragment_shader_code)

        cls.instance.cached_materials[data] = MaterialInstance(name, shader_program, data.textures, shader_params_vertex | shader_params_fragment)
        cls.instance.materials[name] = MaterialInstance(name, shader_program, data.textures, shader_params_vertex | shader_params_fragment)

        return cls.instance.materials[name]

    def get(cls, name):
        return cls.instance.materials.get(name)