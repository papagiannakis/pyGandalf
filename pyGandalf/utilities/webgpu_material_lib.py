from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureInstance
from pyGandalf.utilities.logger import logger

import wgpu
import numpy as np

import re

class CPUBuffer:
    def __init__(self, *args):
        fields = []
        current_offset = 0

        # Use this to double check the padding: https://eliemichel.github.io/WebGPU-AutoLayout/
        def add_padding():
            nonlocal current_offset
            if current_offset % 16 != 0:
                padding = 16 - (current_offset % 16)
                pad_field_name = f'__pad{len(fields)}'
                fields.append((pad_field_name, np.float32, ((padding // 4),)))
                current_offset += padding

        for name, dtype, shape in args:
            # Ensure shape is a tuple even for single elements
            if not isinstance(shape, tuple):
                shape = (shape,)

            # Calculate the size in bytes of the current field
            field_size = np.dtype(dtype).itemsize * np.prod(shape)

            # Append field and increase the offset
            fields.append((name, dtype, shape))
            current_offset += field_size

            # Align current field to 16 bytes
            add_padding()

        self.type = np.dtype(fields)
        self.data = np.empty((1,), self.type)

    @property
    def nbytes(self):
        return self.data.nbytes
    
    @property
    def mem(self):
        return self.data
    
    @property
    def dtype(self):
        return self.type

    def has_member(self, member):
        return member in self.data.dtype.names
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, val):
        self.data[key] = val


class MaterialInstance:
    def __init__(self, name, base_template, shader_module, pipeline_layout, bind_groups, uniform_buffers, uniform_buffer_types, storage_buffers, storage_buffer_types, other_uniforms, textures, shader_params = []):
        self.name = name
        self.base_template = base_template
        self.shader_module = shader_module
        self.pipeline_layout = pipeline_layout
        self.bind_groups = bind_groups
        self.uniform_buffers = uniform_buffers
        self.uniform_buffer_types = uniform_buffer_types
        self.storage_buffers = storage_buffers
        self.storage_buffer_types = storage_buffer_types
        self.other_uniforms = other_uniforms
        self.textures = textures
        self.shader_params = shader_params

    def has_uniform(self, uniform_name: str) -> bool:
        """Returns True if the material has the uniform with the given name, otherwise False.

        Args:
            uniform_name (str): The name of the uniform.

        Returns:
            bool: True if the material has the uniform with the given name, otherwise False.
        """
        return uniform_name in self.uniform_buffers.keys()

    def set_uniform(self, uniform_name: str):
        """Sets the uniform buffer with the provided name (if valid), with the provided data.

        Args:
            uniform_name (str): The name of the uniform buffer to set.
        """
        uniform = self.other_uniforms[uniform_name]

        if isinstance(uniform, TextureInstance):
            WebGPURenderer().write_texture(uniform)

    def set_uniform_buffer(self, uniform_name: str, uniform_data: CPUBuffer):
        """Sets the uniform buffer with the provided name (if valid), with the provided data.

        Args:
            uniform_name (str): The name of the uniform buffer to set.
            uniform_data (CPUBuffer): The new data for the uniform buffer.
        """
        uniform_buffer = self.uniform_buffers[uniform_name]
        WebGPURenderer().write_buffer(uniform_buffer, uniform_data.mem)

    def set_storage_buffer(self, storage_name: str, storage_data: CPUBuffer):
        """Sets the storage buffer with the provided name (if valid), with the provided data.

        Args:
            uniform_name (str): The name of the storage buffer to set.
            uniform_data (Any): The new data for the storage buffer.
        """
        storage_buffer = self.storage_buffers[storage_name]

        temporary_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer_with_data(
            data=storage_data.mem, usage=wgpu.BufferUsage.COPY_SRC
        )

        WebGPURenderer().get_command_encoder().copy_buffer_to_buffer(
            temporary_buffer, 0, storage_buffer, 0, storage_data.mem.nbytes
        )

        temporary_buffer.destroy()

    def get_cpu_buffer_type(self, buffer_name: str) -> CPUBuffer | None:
        if buffer_name in self.uniform_buffer_types.keys():
            return self.uniform_buffer_types[buffer_name]
        if buffer_name in self.storage_buffer_types.keys():
            return self.storage_buffer_types[buffer_name]
        return None

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

class WebGPUMaterialLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebGPUMaterialLib, cls).__new__(cls)
            cls.instance.cached_materials: dict[MaterialData, MaterialInstance] = {} # type: ignore
            cls.instance.materials: dict[str, MaterialInstance] = {} # type: ignore
        return cls.instance
    
    def build(cls, name: str, data: MaterialData) -> MaterialInstance:
        """Builds a new material (if one does not already exists with that data) and returns its instance.

        Args:
            name (str): The name of the material.
            data (MaterialData): The data of the material.

        Returns:
            MaterialInstance: The material instance.
        """
        if cls.instance.cached_materials.get(data) != None:
            material = cls.instance.cached_materials[data]
            cls.instance.materials[name] = material
            return material

        shader_data = WebGPUShaderLib().get(data.base_template)

        # Parse shader params
        uniform_buffers_data, storage_buffers_data, read_only_storage_buffers_data, other = WebGPUShaderLib().parse(shader_data.shader_code)

        uniform_buffers = {}
        uniform_buffer_types = {}
        storage_buffers = {}
        storage_buffer_types = {}
        other_uniforms = {}

        bind_groups_entries = [[]]
        for buffer_name in uniform_buffers_data.keys():
            uniform_buffer_data = uniform_buffers_data[buffer_name]

            if len(bind_groups_entries) <= uniform_buffer_data['group']:
                bind_groups_entries.append([])

            # Find uniform buffer layout and fields from shader reflection.
            fields = []
            for member_name in uniform_buffer_data['type']['members']:
                member_type = uniform_buffer_data['type']['members'][member_name]
                match member_type:
                    case 'f32':
                        fields.append((member_name, np.float32, (1,)))
                    case 'vec2f':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec2<f32>':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec3f':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec3<f32>':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec4f':
                        fields.append((member_name, np.float32, (4,)))
                    case 'vec4<f32>':
                        fields.append((member_name, np.float32, (4,)))
                    case 'mat4x4f':
                        fields.append((member_name, np.float32, (4, 4)))
                    case 'array<mat4x4f>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<mat4x4f, 512>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<vec4f, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<vec4<f32>, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<f32, 16>':
                        fields.append((member_name, np.float32, (16, 1)))

            # Instantiate a struct for the uniform buffer data with the given fields
            uniform_data = CPUBuffer(*fields)
            uniform_buffer_types[buffer_name] = uniform_data

            # Create a uniform buffer
            uniform_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=uniform_data.nbytes, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
            )

            # Append uniform buffer to dictionary holding all uniform buffers
            uniform_buffers[buffer_name] = uniform_buffer

            # Create a bind group entry for the uniform buffer
            bind_groups_entries[uniform_buffers_data[buffer_name]['group']].append({
                "binding": uniform_buffers_data[buffer_name]['binding'],
                "resource": {
                    "buffer": uniform_buffer,
                    "offset": 0,
                    "size": uniform_buffer.size,
                },
            })

        for buffer_name in storage_buffers_data.keys():
            storage_buffer_data = storage_buffers_data[buffer_name]

            if len(bind_groups_entries) <= storage_buffers_data['group']:
                bind_groups_entries.append([])

            # Find storage buffer layout and fields from shader reflection.
            fields = []
            for member_name in storage_buffer_data['type']['members']:
                member_type = storage_buffer_data['type']['members'][member_name]
                match member_type:
                    case 'f32':
                        fields.append((member_name, np.float32, (1,)))
                    case 'vec2f':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec2<f32>':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec3f':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec3<f32>':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec4f':
                        fields.append((member_name, np.float32, (4,)))
                    case 'vec4<f32>':
                        fields.append((member_name, np.float32, (4,)))
                    case 'mat4x4f':
                        fields.append((member_name, np.float32, (4, 4)))
                    case 'array<mat4x4f>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<mat4x4f, 512>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<vec4f, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<vec4<f32>, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<f32, 16>':
                        fields.append((member_name, np.float32, (16, 1)))

            # Instantiate a struct for the uniform buffer data with the given fields
            storage_data = CPUBuffer(*fields)

            storage_buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes * 512, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
            )

            # Append storage buffer to dictionary holding all storage buffers
            storage_buffers[buffer_name] = storage_buffer

            bind_groups_entries[storage_buffer_data['group']].append({
                "binding": storage_buffer_data['binding'],
                "resource": {
                    "buffer": storage_buffer,
                    "offset": 0,
                    "size": storage_buffer.size,
                },
            })
        
        for buffer_name in read_only_storage_buffers_data.keys():
            read_only_storage_buffer_data = read_only_storage_buffers_data[buffer_name]

            if len(bind_groups_entries) <= read_only_storage_buffer_data['group']:
                bind_groups_entries.append([])

            # Find storage buffer layout and fields from shader reflection.
            fields = []
            for member_name in read_only_storage_buffer_data['type']['members']:
                member_type = read_only_storage_buffer_data['type']['members'][member_name]
                match member_type:
                    case 'f32':
                        fields.append((member_name, np.float32, (1,)))
                    case 'vec2f':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec2<f32>':
                        fields.append((member_name, np.float32, (2,)))
                    case 'vec3f':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec3<f32>':
                        fields.append((member_name, np.float32, (3,)))
                    case 'vec4f':
                        fields.append((member_name, np.float32, (4,)))
                    case 'vec4<f32>':
                        fields.append((member_name, np.float32, (4,)))
                    case 'mat4x4f':
                        fields.append((member_name, np.float32, (4, 4)))
                    case 'array<mat4x4f>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<mat4x4f, 512>':
                        fields.append((member_name, np.float32, (512, 4, 4)))
                    case 'array<vec4f, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<vec4<f32>, 16>':
                        fields.append((member_name, np.float32, (16, 4)))
                    case 'array<f32, 16>':
                        fields.append((member_name, np.float32, (16, 1)))

            # Instantiate a struct for the uniform buffer data with the given fields
            storage_data = CPUBuffer(*fields)

            storage_buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes * 512, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
            )

            # Append storage buffer to dictionary holding all storage buffers
            storage_buffers[buffer_name] = storage_buffer
            bind_groups_entries[read_only_storage_buffer_data['group']].append({
                "binding": read_only_storage_buffer_data['binding'],
                "resource": {
                    "buffer": storage_buffer,
                    "offset": 0,
                    "size": storage_buffer.size,
                },
            })

        texture_index = 0
        texture_index_use_count = 0

        for uniform_name in other.keys():
            other_data = other[uniform_name]

            if len(bind_groups_entries) <= other_data['group']:
                bind_groups_entries.append([])

            match other_data['type']['name']:
                case 'texture_2d<f32>':
                    # Retrieve texture.
                    texture_inst: TextureInstance = WebGPUTextureLib().get_instance(data.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.view
                    })
                    texture_index_use_count += 1

                case 'sampler':
                    # Retrieve texture.
                    texture_inst: TextureInstance = WebGPUTextureLib().get_instance(data.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.sampler
                    })
                    texture_index_use_count += 1
            
            if texture_index_use_count == 2:
                texture_index_use_count = 0
                texture_index += 1

        bind_groups: list[wgpu.GPUBindGroup] = []
        for index, bind_group_entry in enumerate(bind_groups_entries):
            bind_groups.append(WebGPURenderer().get_device().create_bind_group(
                layout=shader_data.bind_group_layouts[index],
                entries=bind_group_entry
            ))

        cls.instance.cached_materials[data] = MaterialInstance(name, data.base_template, shader_data.shader_module, shader_data.pipeline_layout, bind_groups, uniform_buffers, uniform_buffer_types, storage_buffers, storage_buffer_types, other_uniforms, data.textures, [])
        cls.instance.materials[name] = MaterialInstance(name, data.base_template, shader_data.shader_module, shader_data.pipeline_layout, bind_groups, uniform_buffers, uniform_buffer_types, storage_buffers, storage_buffer_types, other_uniforms, data.textures, [])

        return cls.instance.materials[name]

    def get(cls, name: str) -> MaterialInstance:
        """Returns the material instance with the given name.

        Args:
            name (str): The name of the material instance to get.

        Returns:
            MaterialInstance: The material instance with the given name.
        """
        return cls.instance.materials.get(name)
    
    def get_materials(cls) -> dict[str, MaterialInstance]:
        """Returns a dictionary the holds all the material instances. As the key is the name of the material, as the value is the material instance.

        Returns:
            dict[str, MaterialInstance]: A dictionary the holds all the material instances.
        """
        return cls.instance.materials
    
    def extract_array_size(declaration: str) -> int:
        # Define the regular expression pattern to match the array declaration
        pattern = r'array<[^,]+, (\d+)>'
        
        # Use re.search to find the match
        match = re.search(pattern, declaration)
        
        if match:
            # Extract the number from the match group and convert it to an integer
            return int(match.group(1))
        else:
            raise ValueError(f"Invalid declaration format: {declaration}")