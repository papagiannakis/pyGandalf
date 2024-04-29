from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.definitions import SHADERS_PATH

import wgpu

import os
import re
from pathlib import Path
import ctypes

class UniformArray:
    """Convenience class to create a uniform array.

    Maybe we can make it a public util at some point.
    Ensure that the order matches structs in the shader code.
    See https://www.w3.org/TR/WGSL/#alignment-and-size for reference on alignment.
    """

    def __init__(self, *args):
        # Analyse incoming fields
        fields = []
        byte_offset = 0
        for name, format, n in args:
            assert format in ("f", "i", "I")
            field = name, format, byte_offset, byte_offset + n * 4
            fields.append(field)
            byte_offset += n * 4
        # Get padding
        nbytes = byte_offset
        while nbytes % 16:
            nbytes += 1
        # Construct memoryview object and a view for each field
        self._mem = memoryview((ctypes.c_uint8 * nbytes)()).cast("B")
        self._views = {}
        for name, format, i1, i2 in fields:
            self._views[name] = self._mem[i1:i2].cast(format)

    @property
    def mem(self):
        return self._mem

    @property
    def nbytes(self):
        return self._mem.nbytes

    def __getitem__(self, key):
        v = self._views[key].tolist()
        return v[0] if len(v) == 1 else v

    def __setitem__(self, key, val):
        m = self._views[key]
        n = m.shape[0]
        if n == 1:
            assert isinstance(val, (float, int))
            m[0] = val
        else:
            assert isinstance(val, (tuple, list))
            for i in range(n):
                m[i] = val[i]

class ShaderData:
    def __init__(self, name: str, shader_module, pipeline_layout, bind_group_layouts, shader_path: Path, shader_code: str):
        self.name = name
        self.shader_module = shader_module
        self.pipeline_layout = pipeline_layout
        self.bind_group_layouts: list = bind_group_layouts
        self.shader_path = shader_path
        self.shader_code = shader_code

class WebGPUShaderLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebGPUShaderLib, cls).__new__(cls)
            cls.instance.shaders : dict[str, ShaderData] = {} # type: ignore
        return cls.instance

    def create_shader_module(cls, shader_source):
        shader_module: wgpu.GPUShaderModule = WebGPURenderer().get_device().create_shader_module(code=shader_source)

        uniform_buffers, storage_buffers = cls.instance.parse(shader_source)

        # TODO: Handle bind groups.
        # Create the wgpu binding objects
        bind_groups_layout_entries = [[]]
        for index, name in enumerate(uniform_buffers.keys()):
            bind_groups_layout_entries[index].append({
                "binding": uniform_buffers[name]['binding'],
                "visibility": wgpu.ShaderStage.VERTEX,
                "buffer": {
                    "type": wgpu.BufferBindingType.uniform
                },
            })
        
        for index, name in enumerate(storage_buffers.keys()):
            bind_groups_layout_entries[index].append({
                "binding": storage_buffers[name]['binding'],
                "visibility": wgpu.ShaderStage.VERTEX,
                "buffer": {
                    "type": wgpu.BufferBindingType.read_only_storage
                },
            })

        # Create the wgou binding objects
        bind_group_layouts = []

        for layout_entries in bind_groups_layout_entries:
            bind_group_layouts.append(WebGPURenderer().get_device().create_bind_group_layout(entries=layout_entries))

        # No bind group and layout, we should not create empty ones.
        pipeline_layout : wgpu.GPUPipelineLayout = WebGPURenderer().get_device().create_pipeline_layout(bind_group_layouts=bind_group_layouts)

        return shader_module, pipeline_layout, bind_group_layouts
    
    def build(cls, name: str, shader_path: Path) -> int:
        """Builds a new shader (if one does not already exists with that name) and returns its shader program.

        Args:
            name (str): The name of the shader
            vs_path (Path): The path to the vertex shader code
            fs_path (Path): The path to the fragment shader code

        Returns:
            int: The shader program
        """
        if cls.instance.shaders.get(name) != None:
            return
        
        shader_source = cls.instance.load_from_file(shader_path)

        shader_rel_path = Path(os.path.relpath(shader_path, SHADERS_PATH))

        shader_module, pipeline_layout, bind_group_layouts = cls.instance.create_shader_module(shader_source)
        cls.instance.shaders[name] = ShaderData(name, shader_module, pipeline_layout, bind_group_layouts, shader_rel_path, shader_source)
    
    def parse(cls, shader_code: str) -> dict:
        """Parses the provided shader code and identifies all the uniforms along with their types.

        Args:
            shader_code (str): The source code of the shader to parse.

        Returns:
            dict: A dictionary holding the uniform name as a key and the uniform type as a value
        """
        uniform_pattern = re.compile(r"@group\((\d+)\) @binding\((\d+)\) var<uniform> (\w+): (\w+);")
        uniform_matches = uniform_pattern.findall(shader_code)

        uniform_buffers = {}
        uniform_buffer_members = {}
        for match in uniform_matches:
            group, binding, uniform_name, uniform_type = match
            print(f"Uniform: {uniform_name}")
            print(f" Group: {group}")
            print(f" Binding: {binding}")
            print(f" Type: {uniform_type}")
            struct_pattern = r"struct " + re.escape(uniform_type) + r" \{([^}]*)\}"
            struct_match = re.search(struct_pattern, shader_code)
            if struct_match:
                uniform_buffer_members.clear()
                struct_body = struct_match.group(1)
                member_pattern = r"(\w+): (\w+)"
                members = re.findall(member_pattern, struct_body)
                print(f" Members:")
                for member in members:
                    print(f" {member[0]}: {member[1]}")
                    uniform_buffer_members[member[0]] = member[1]

            uniform_buffers[uniform_name] = {
                'group': group,
                'binding': binding,
                'type': {
                    'name': uniform_type,
                    'members': uniform_buffer_members
                },
            }

        storage_pattern = re.compile(r"@group\((\d+)\) @binding\((\d+)\) var<storage, read> (\w+): (\w+);")
        storage_matches = storage_pattern.findall(shader_code)

        storage_buffers = {}
        storage_buffer_members = {}
        for match in storage_matches:
            group, binding, storage_name, storage_type = match
            print(f"Storage: {storage_name}")
            print(f" Group: {group}")
            print(f" Binding: {binding}")
            print(f" Type: {storage_type}")
            struct_pattern = r"struct " + re.escape(storage_type) + r" \{([^}]*)\}"
            struct_match = re.search(struct_pattern, shader_code)
            if struct_match:
                storage_buffer_members.clear()
                struct_body = struct_match.group(1)
                member_pattern = r"(\w+): (\w+)"
                members = re.findall(member_pattern, struct_body)
                print(f" Members:")
                for member in members:
                    print(f" {member[0]}: {member[1]}")
                    storage_buffer_members[member[0]] = member[1]

            storage_buffers[storage_name] = {
                'group': group,
                'binding': binding,
                'type': {
                    'name': storage_type,
                    'members': storage_buffer_members
                },
            }

        return uniform_buffers, storage_buffers

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