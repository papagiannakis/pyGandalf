from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.logger import logger

import glm
import numpy as np
import OpenGL.GL as gl

import re
from dataclasses import dataclass

class MaterialInstance:
    def __init__(self, name, data, descriptor, shader_program, shader_params = []):
        self.name = name
        self.data = data
        self.descriptor = descriptor
        self.shader_program = shader_program
        self.shader_params = shader_params

    def has_uniform(self, uniform_name: str) -> bool:
        """Returns True if the material has the uniform with the given name, otherwise False.

        Args:
            uniform_name (str): The name of the uniform.

        Returns:
            bool: True if the material has the uniform with the given name, otherwise False.
        """
        return gl.glGetUniformLocation(self.shader_program, uniform_name) != -1

    def set_uniform(self, uniform_name: str, uniform_data):
        """Stes the uniform with the provided name (if valid), with the provided data.

        Args:
            uniform_name (str): The name of the uniform to set.
            uniform_data (Any): The new data for the unform.
        """
        uniform_location = gl.glGetUniformLocation(self.shader_program, uniform_name)
        if uniform_location != -1:
            self.update_uniform(uniform_location, uniform_name, uniform_data)
        else:
            self.uniform_not_found(uniform_name)

    def update_uniform(self, uniform_location: int, uniform_name: str, uniform_data):
        """Updates the uniform at specfied location and the given name with the given data.

        Args:
            uniform_location (int): The uniform location.
            uniform_name (str): The uniform name.
            uniform_data (Any): The new uniform data.
        """
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
            case 'samplerCube':
                assert isinstance(uniform_data, int), f"Uniform type with name: {uniform_name} is not an integer number"
                gl.glUniform1i(uniform_location, uniform_data)
                return
            case 'vec2':
                assert isinstance(uniform_data, glm.vec2), f"Uniform type with name: {uniform_name} is not a 2x1 glm array of float32 type"
                gl.glUniform2f(uniform_location, uniform_data.x, uniform_data.y)
                return
            case 'vec3':
                assert isinstance(uniform_data, glm.vec3), f"Uniform type with name: {uniform_name} is not a 3x1 glm array of float32 type"
                gl.glUniform3f(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z)
                return
            case 'vec4':
                assert isinstance(uniform_data, glm.vec4), f"Uniform type with name: {uniform_name} is not a 4x1 glm array of float32 type"
                gl.glUniform4f(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z, uniform_data.w)
                return
            case 'ivec2':
                assert isinstance(uniform_data, glm.ivec2), f"Uniform type with name: {uniform_name} is not a 2x1 glm array of int32 type"
                gl.glUniform2i(uniform_location, uniform_data.x, uniform_data.y)
                return
            case 'ivec3':
                assert isinstance(uniform_data, glm.ivec3), f"Uniform type with name: {uniform_name} is not a 3x1 glm array of int32 type"
                gl.glUniform3i(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z)
                return
            case 'ivec4':
                assert isinstance(uniform_data, glm.ivec4), f"Uniform type with name: {uniform_name} is not a 4x1 glm array of int32 type"
                gl.glUniform4ui(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z, uniform_data.w)
                return
            case 'uvec2':
                assert isinstance(uniform_data, glm.uvec2), f"Uniform type with name: {uniform_name} is not a 2x1 glm array of uint32 type"
                gl.glUniform2ui(uniform_location, uniform_data.x, uniform_data.y)
                return
            case 'uvec3':
                assert isinstance(uniform_data, glm.uvec3), f"Uniform type with name: {uniform_name} is not a 3x1 glm array of uint32 type"
                gl.glUniform3ui(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z)
                return
            case 'uvec4':
                assert isinstance(uniform_data, glm.uvec4), f"Uniform type with name: {uniform_name} is not a 4x1 glm array of uint32 type"
                gl.glUniform4ui(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z, uniform_data.w)
                return
            case 'dvec2':
                assert isinstance(uniform_data, glm.dvec2), f"Uniform type with name: {uniform_name} is not a 2x1 glm array of double type"
                gl.glUniform2d(uniform_location, uniform_data.x, uniform_data.y)
                return
            case 'dvec3':
                assert isinstance(uniform_data, glm.dvec3), f"Uniform type with name: {uniform_name} is not a 3x1 glm array of double type"
                gl.glUniform3d(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z)
                return
            case 'dvec4':
                assert isinstance(uniform_data, glm.dvec4), f"Uniform type with name: {uniform_name} is not a 4x1 glm array of double type"
                gl.glUniform4d(uniform_location, uniform_data.x, uniform_data.y, uniform_data.z, uniform_data.w)
                return
            case 'mat2':
                assert isinstance(uniform_data, glm.mat2), f"Uniform type with name: {uniform_name} is not a 2x2 glm matrix type"
                gl.glUniformMatrix2fv(uniform_location, 1, gl.GL_FALSE, glm.value_ptr(uniform_data))
                return
            case 'mat3':
                assert isinstance(uniform_data, glm.mat3), f"Uniform type with name: {uniform_name} is not a 3x3 glm matrix type"
                gl.glUniformMatrix3fv(uniform_location, 1, gl.GL_FALSE, glm.value_ptr(uniform_data))
                return
            case 'mat4':
                assert isinstance(uniform_data, glm.mat4), f"Uniform type with name: {uniform_name} is not a 4x4 glm matrix type"
                gl.glUniformMatrix4fv(uniform_location, 1, gl.GL_FALSE, glm.value_ptr(uniform_data))
                return

        if 'int[' in uniform_type or 'sampler2D[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], np.int32), f"Uniform type with name: {uniform_name} is not a NumPy array of {count} integers"
                gl.glUniform1iv(uniform_location, len(uniform_data), uniform_data)
        elif 'float[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], np.float32), f"Uniform type with name: {uniform_name} is not a NumPy array of {count} floats"
                gl.glUniform1fv(uniform_location, len(uniform_data), uniform_data)
        elif 'mat2[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.mat2), f"Uniform type with name: {uniform_name} is not a NumPy array of {count} 2x2 glm matrices"
                gl.glUniformMatrix2fv(uniform_location, len(uniform_data), gl.GL_FALSE, uniform_data.ptr)
        elif 'mat3[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.mat3), f"Uniform type with name: {uniform_name} is not an array of {count} 3x3 glm matrices"
                gl.glUniformMatrix3fv(uniform_location, len(uniform_data), gl.GL_FALSE, uniform_data.ptr)
        elif 'mat4[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.mat4), f"Uniform type with name: {uniform_name} is not an array of {count} 4x4 glm matrices"
                gl.glUniformMatrix4fv(uniform_location, len(uniform_data), gl.GL_FALSE, uniform_data.ptr)
        elif 'vec2[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.vec2), f"Uniform type with name: {uniform_name} is not an array of {count} 2x1 glm array of float"
                gl.glUniform2fv(uniform_location, len(uniform_data), uniform_data.ptr)
        elif 'vec3[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.vec3), f"Uniform type with name: {uniform_name} is not an array of {count} 3x1 glm array of float"
                gl.glUniform3fv(uniform_location, len(uniform_data), uniform_data.ptr)
        elif 'vec4[' in uniform_type:
            number_pattern = re.compile(r'\[(\d+)\]')
            match = number_pattern.search(uniform_type)
            if match:
                count = int(match.group(1))
                assert len(uniform_data) <= count and isinstance(uniform_data[0], glm.vec4), f"Uniform type with name: {uniform_name} is not an array of {count} 4x1 glm array of float"
                gl.glUniform4fv(uniform_location, len(uniform_data), uniform_data.ptr)

    def uniform_not_found(self, uniform_name: str):
        """Prints a message stating that the uniform with the provided name was not found.

        Args:
            uniform_name (str): The name of the uniform that was not found.
        """
        logger.debug(f'Could not find {uniform_name} uniform for material: {self.name}!\n These are the available uniforms for shader with id {self.shader_program}:\n {self.shader_params}')
    
    def print_available_uniforms(self):
        """Prints a message with all the available uniforms of the material.
        """
        logger.log(f'Available uniforms for material: {self.name} and shader id {self.shader_program}:\n {self.shader_params}')

@dataclass
class MaterialDescriptor:
    primitive: gl.Constant = gl.GL_TRIANGLES
    cast_shadows = True
    cull_enabled: bool = True
    cull_face: gl.Constant = gl.GL_BACK
    patch_resolution: int = 20
    vertices_per_patch: int = 20
    depth_enabled: bool = True
    depth_func: gl.Constant = gl.GL_LEQUAL
    depth_mask: gl.Constant = gl.GL_TRUE
    blend_enabled: bool = True
    blend_func_source: gl.Constant = gl.GL_SRC_ALPHA
    blend_func_destination: gl.Constant = gl.GL_ONE_MINUS_SRC_ALPHA
    blend_equation: gl.Constant = gl.GL_FUNC_ADD

class MaterialData:
    def __init__(self, base_template: str, textures: list[str], color: glm.vec4 = glm.vec4(1.0, 1.0, 1.0, 1.0), glossiness = 3.0):
        self.base_template = base_template
        self.color = color
        self.textures = textures
        self.glossiness = glossiness

    def __eq__(self, other):
        if self.base_template != other.base_template:
            return False
        if self.color != other.color:
            return False
        if self.glossiness != other.glossiness:
            return False
        if len(self.textures) != len(other.textures):
            return False
        for i in range(len(self.textures)):
            if (self.textures[i] != other.textures[i]):
                return False
        return True
    
    def __hash__(self):
        return hash((self.base_template, self.color.r, self.color.g, self.color.b, self.color.a, len(self.textures), tuple(texture for texture in self.textures)))

class OpenGLMaterialLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLMaterialLib, cls).__new__(cls)
            cls.instance.cached_materials: dict[MaterialData, MaterialInstance] = {} # type: ignore
            cls.instance.materials: dict[str, MaterialInstance] = {} # type: ignore
        return cls.instance
    
    def build(cls, name: str, data: MaterialData, descriptor: MaterialDescriptor=MaterialDescriptor()) -> MaterialInstance:
        """Builds a new material (if one does not already exists with that data) and returns its instance.

        Args:
            name (str): The name of the material.
            data (MaterialData): The data of the material.
            descriptor (MaterialDescriptor, optional): The description of the material, which consists of various options and flags.

        Returns:
            MaterialInstance: The material instance.
        """
        if cls.instance.cached_materials.get(data) != None:
            material = cls.instance.cached_materials[data]
            cls.instance.materials[name] = material
            return material

        shader_data = OpenGLShaderLib().get(data.base_template)

        shader_program = shader_data.shader_program
        shader_params_vertex = OpenGLShaderLib().parse(shader_data.vs_code)
        shader_params_fragment = OpenGLShaderLib().parse(shader_data.fs_code)
        shader_params_tess_control = {}
        shader_params_tess_eval = {}
        
        if shader_data.tcs_code != None:
            shader_params_tess_control = OpenGLShaderLib().parse(shader_data.tcs_code)
        if shader_data.tes_code != None:
            shader_params_tess_eval = OpenGLShaderLib().parse(shader_data.tes_code)

        cls.instance.cached_materials[data] = MaterialInstance(name, data, descriptor, shader_program, shader_params_vertex | shader_params_fragment | shader_params_tess_control | shader_params_tess_eval)
        cls.instance.materials[name] = MaterialInstance(name, data, descriptor, shader_program, shader_params_vertex | shader_params_fragment | shader_params_tess_control | shader_params_tess_eval)

        return cls.instance.materials[name]

    def get(cls, name: str) -> MaterialInstance:
        """Returns the material instance with the given name.

        Args:
            name (str): The name of the material instance to get.

        Returns:
            MaterialInstance: The material instance with the given name.
        """
        return cls.instance.materials.get(name)
    
    def get_textures(cls, name: str):
        mat: MaterialInstance = cls.instance.materials[name]

        textures = []
        for uniform_name in mat.shader_params.keys():
            uniform_type = mat.shader_params[uniform_name]
            if 'sampler' in uniform_type:
                textures.append(uniform_name)
        
        return textures
    
    def get_materials(cls) -> dict[str, MaterialInstance]:
        """Returns a dictionary the holds all the material instances. As the key is the name of the material, as the value is the material instance.

        Returns:
            dict[str, MaterialInstance]: A dictionary the holds all the material instances.
        """
        return cls.instance.materials