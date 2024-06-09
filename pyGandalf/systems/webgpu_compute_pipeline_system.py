from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import Component, WebGPUComputeComponent
from pyGandalf.systems.system import System

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData, TextureDescriptor, TextureInstance
from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, CPUBuffer

import wgpu
import numpy as np

import asyncio

class WebGPUComputePipelineSystem(System):
    """
    The system responsible for compute pipeline invocations.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        compute = components
        
        # Retrieve shader data
        compute_shader = WebGPUShaderLib().get(compute.shader)

        # Parse shader params
        uniform_buffers_data, storage_buffers_data, read_only_storage_buffers_data, other = WebGPUShaderLib().parse(compute_shader.shader_code)

        bind_groups_entries = [[]]

        for buffer_name in uniform_buffers_data.keys():
            uniform_buffer_data = uniform_buffers_data[buffer_name]

            if len(bind_groups_entries) <= uniform_buffer_data['group']:
                bind_groups_entries.append([])

            # Find uniform buffer layout and fields from shader reflection.
            fields = []
            for member_name in uniform_buffer_data['type']['members']:
                member_type = uniform_buffer_data['type']['members'][member_name]
                fields.append(WebGPUMaterialLib().compute_field_layout(member_type, member_name))

            # Instantiate a struct for the uniform buffer data with the given fields
            uniform_data = CPUBuffer(*fields)
            compute.buffer_types[buffer_name] = uniform_data

            # Create a uniform buffer
            uniform_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=uniform_data.nbytes, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
            )

            # Append uniform buffer to dictionary holding all uniform buffers
            compute.uniform_buffers[buffer_name] = uniform_buffer

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

            if len(bind_groups_entries) <= storage_buffer_data['group']:
                bind_groups_entries.append([])

            # Find storage buffer layout and fields from shader reflection.
            fields = []
            for member_name in storage_buffer_data['type']['members']:
                member_type = storage_buffer_data['type']['members'][member_name]
                fields.append(WebGPUMaterialLib().compute_field_layout(member_type, member_name))

            # Instantiate a struct for the uniform buffer data with the given fields
            storage_data = CPUBuffer(*fields)

            compute.buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.COPY_SRC
            )

            compute.map_buffers.append(WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes,
                usage=wgpu.BufferUsage.MAP_READ | wgpu.BufferUsage.COPY_DST
            ))

            # Append storage buffer to dictionary holding all storage buffers
            compute.output_storage_buffers[buffer_name] = storage_buffer

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
                fields.append(WebGPUMaterialLib().compute_field_layout(member_type, member_name))

            # Instantiate a struct for the uniform buffer data with the given fields
            storage_data = CPUBuffer(*fields)

            compute.buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
            )

            # Append storage buffer to dictionary holding all storage buffers
            compute.input_storage_buffers[buffer_name] = storage_buffer
            bind_groups_entries[read_only_storage_buffer_data['group']].append({
                "binding": read_only_storage_buffer_data['binding'],
                "resource": {
                    "buffer": storage_buffer,
                    "offset": 0,
                    "size": storage_buffer.size,
                },
            })

        texture_index = 0

        for uniform_name in other.keys():
            other_data = other[uniform_name]

            if len(bind_groups_entries) <= other_data['group']:
                bind_groups_entries.append([])

            match other_data['type']['name']:
                case 'texture_2d<f32>':
                    # Retrieve texture.
                    texture_inst: TextureInstance = WebGPUTextureLib().get_instance(compute.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    compute.other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.view
                    })
                    texture_index += 1
                case 'texture_depth_2d':
                    # Retrieve texture.
                    texture_inst: TextureInstance = WebGPUTextureLib().get_instance(compute.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    compute.other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.view
                    })
                    texture_index += 1
                case 'texture_cube<f32>':
                    # Retrieve texture.
                    texture_inst = WebGPUTextureLib().get_instance(compute.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    compute.other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.view
                    })
                    texture_index += 1
                case 'texture_storage_2d<rgba8unorm, write>':
                    # Retrieve texture.
                    texture_inst = WebGPUTextureLib().get_instance(compute.textures[texture_index])

                    # Append uniform buffer to dictionary holding all uniform buffers
                    compute.other_uniforms[uniform_name] = texture_inst

                    # Create a bind group entry for the uniform buffer
                    bind_groups_entries[other_data['group']].append({
                        "binding": other_data['binding'],
                        "resource": texture_inst.view
                    })
                    texture_index += 1

        # Create compute shader bind groups
        for index, bind_group_entry in enumerate(bind_groups_entries):
            compute.bind_groups.append(WebGPURenderer().get_device().create_bind_group(
                layout=compute_shader.bind_group_layouts[index],
                entries=bind_group_entry
            ))

        # Create compute shader pipeline
        compute.pipeline = WebGPURenderer().get_device().create_compute_pipeline(
            layout=compute_shader.pipeline_layout,
            compute={
                "module": compute_shader.shader_module,
                "entry_point": compute.entry_point,
            }
        )

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        compute = components
        
        def dispatch():
            # Create the encoder is it is None
            if compute.encoder == None:
                compute.encoder = WebGPURenderer().get_device().create_command_encoder()

            # Begin the compute pass
            compute_pass: wgpu.GPUComputePassEncoder = compute.encoder.begin_compute_pass()

            # Use compute pass
            compute_pass.set_pipeline(compute.pipeline)

            # Set the pass bind groups
            for index, bind_group in enumerate(compute.bind_groups):
                compute_pass.set_bind_group(index, bind_group, [], 0, 1)

            # Calculate the workgroup count.
            workgroup_count_x = int(np.ceil((compute.invocation_count_x + compute.work_group - 1) / compute.work_group))
            workgroup_count_y = int(np.ceil((compute.invocation_count_y + compute.work_group - 1) / compute.work_group))
            workgroup_count_z = int(np.ceil((compute.invocation_count_z + compute.work_group - 1) / compute.work_group))

            # Dispatch the work groups
            compute_pass.dispatch_workgroups(workgroup_count_x, workgroup_count_y, workgroup_count_z)

            # Finalize compute pass
            compute_pass.end()

            # Before submiting commands copy the output buffers to the mapped buffers. (Thats because storage buffers cant be marked as MAP_READ)
            for i, output_buffer in enumerate(compute.output_storage_buffers.values()):
                compute.encoder.copy_buffer_to_buffer(output_buffer, 0, compute.map_buffers[i], 0, output_buffer.size)

            # Submit the compute commands to the gpu
            WebGPURenderer().get_device().queue.submit([compute.encoder.finish()])

            # Retrieve the output buffer data asynchronously from the gpu
            asyncio.run(self.retrieve_output(compute))

        if compute.dispatch:
            dispatch()
    
    async def retrieve_output(self, compute: WebGPUComputeComponent):
        compute.output.clear()
        compute.output_ready = False

        for i, output_buffer in enumerate(compute.output_storage_buffers.values()): 
            await compute.map_buffers[i].map_async(mode=wgpu.MapMode.READ, size=output_buffer.size)
            output = compute.map_buffers[i].read_mapped(buffer_offset=0, size=output_buffer.size, copy=True)
            compute.output.append(output)
            compute.map_buffers[i].unmap()

        compute.dispatch = False
        compute.output_ready = True
        compute.encoder = None
