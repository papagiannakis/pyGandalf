from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.definitions import SHADERS_PATH

import wgpu

import os
import re
from pathlib import Path

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

        uniform_buffers, storage_buffers, read_only_storage_buffers, other = cls.instance.parse(shader_source)

        # Create the wgpu binding objects
        bind_groups_layout_entries = [[]]
        for buffer_name in uniform_buffers.keys():
            if len(bind_groups_layout_entries) <= uniform_buffers[buffer_name]['group']:
                bind_groups_layout_entries.append([])

            bind_groups_layout_entries[uniform_buffers[buffer_name]['group']].append({
                "binding": uniform_buffers[buffer_name]['binding'],
                "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
                "buffer": {
                    "type": wgpu.BufferBindingType.uniform
                },
            })

        for buffer_name in storage_buffers.keys():
            if len(bind_groups_layout_entries) <= storage_buffers[buffer_name]['group']:
                bind_groups_layout_entries.append([])

            bind_groups_layout_entries[storage_buffers[buffer_name]['group']].append({
                "binding": storage_buffers[buffer_name]['binding'],
                "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.COMPUTE, # TODO: Fix this visibility properly
                "buffer": {
                    "type": wgpu.BufferBindingType.storage
                },
            })
        
        for buffer_name in read_only_storage_buffers.keys():
            if len(bind_groups_layout_entries) <= read_only_storage_buffers[buffer_name]['group']:
                bind_groups_layout_entries.append([])

            bind_groups_layout_entries[read_only_storage_buffers[buffer_name]['group']].append({
                "binding": read_only_storage_buffers[buffer_name]['binding'],
                "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.COMPUTE, # TODO: Fix this visibility properly
                "buffer": {
                    "type": wgpu.BufferBindingType.read_only_storage
                },
            })

        for uniform_name in other.keys():
            if len(bind_groups_layout_entries) <= other[uniform_name]['group']:
                bind_groups_layout_entries.append([])

            match other[uniform_name]['type']['name']:
                case 'texture_2d<f32>':
                    bind_groups_layout_entries[other[uniform_name]['group']].append({
                        "binding": other[uniform_name]['binding'],
                        "visibility": wgpu.ShaderStage.FRAGMENT,
                        "texture": {  
                            "sample_type": wgpu.TextureSampleType.float,
                            "view_dimension": wgpu.TextureViewDimension.d2,
                        }
                    })
                case 'texture_depth_2d':
                    bind_groups_layout_entries[other[uniform_name]['group']].append({
                        "binding": other[uniform_name]['binding'],
                        "visibility": wgpu.ShaderStage.FRAGMENT,
                        "texture": {
                            "sample_type": wgpu.TextureSampleType.depth,
                            "view_dimension": wgpu.TextureViewDimension.d2,
                        }
                    })
                case 'texture_cube<f32>':
                    bind_groups_layout_entries[other[uniform_name]['group']].append({
                        "binding": other[uniform_name]['binding'],
                        "visibility": wgpu.ShaderStage.FRAGMENT,
                        "texture": {  
                            "sample_type": wgpu.TextureSampleType.float,
                            "view_dimension": wgpu.TextureViewDimension.cube,
                        }
                    })
                case 'sampler':
                    bind_groups_layout_entries[other[uniform_name]['group']].append({
                        "binding": other[uniform_name]['binding'],
                        "visibility": wgpu.ShaderStage.FRAGMENT,
                        "sampler": {
                            "type": wgpu.SamplerBindingType.filtering
                        },
                    })
                case 'sampler_comparison':
                    bind_groups_layout_entries[other[uniform_name]['group']].append({
                        "binding": other[uniform_name]['binding'],
                        "visibility": wgpu.ShaderStage.FRAGMENT,
                        "sampler": {
                            "type": wgpu.SamplerBindingType.comparison
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
            int: The shader module
        """
        if cls.instance.shaders.get(name) != None:
            return cls.instance.shaders[name].shader_module
        
        shader_source = cls.instance.load_from_file(shader_path)

        shader_rel_path = Path(os.path.relpath(shader_path, SHADERS_PATH))

        shader_module, pipeline_layout, bind_group_layouts = cls.instance.create_shader_module(shader_source)
        cls.instance.shaders[name] = ShaderData(name, shader_module, pipeline_layout, bind_group_layouts, shader_rel_path, shader_source)

        return shader_module
    
    def parse(cls, shader_code: str) -> dict:
        """Parses the provided shader code and identifies all the uniforms along with their types.

        Args:
            shader_code (str): The source code of the shader to parse.

        Returns:
            dict: A dictionary holding the uniform name as a key and the uniform type as a value
        """
        def parse_buffer(buffer_type: str):
            pattern = re.compile(r"@group\((\d+)\) @binding\((\d+)\) var" + re.escape(buffer_type) + r" (\w+):\s*(\w+(?:\<.*?\>)?);")
            matches = pattern.findall(shader_code)

            buffers = {}
            buffer_members = {}
            for match in matches:
                group, binding, name, type = match
                print(f"Buffer: {name}")
                print(f" Group: {group}")
                print(f" Binding: {binding}")
                print(f" Type: {type}")
                struct_pattern = r"struct " + re.escape(type) + r"\s*\{([^}]*)\}"
                struct_match = re.search(struct_pattern, shader_code)
                if struct_match:
                    buffer_members.clear()
                    struct_body = struct_match.group(1)
                    member_pattern = r"(\w+)\s*:\s*(<?[\w\s,<>]+>?),"
                    members = re.findall(member_pattern, struct_body)
                    print(f" Members:")
                    for member in members:
                        print(f" {member[0]}: {member[1]}")
                        buffer_members[member[0]] = member[1]

                buffers[name] = {
                    'group': int(group),
                    'binding': int(binding),
                    'type': {
                        'name': type,
                        'members': buffer_members
                    },
                }

            return buffers
        
        uniform_buffers = parse_buffer('<uniform>')
        storage_buffers = parse_buffer('<storage>')
        read_write_storage_buffers = parse_buffer('<storage, read_write>')
        read_only_storage_buffers = parse_buffer('<storage, read>')
        other = parse_buffer('')

        return uniform_buffers, storage_buffers | read_write_storage_buffers, read_only_storage_buffers, other  

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