from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import Component, WebGPUComputeComponent
from pyGandalf.systems.system import System

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, CPUBuffer

import glm
import wgpu
import numpy as np

import asyncio
import struct

class WebGPUComputePipelineSystem(System):
    """
    The system responsible for compute pipeline invocations.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        compute = components
        
        # Retrieve shader data
        compute_shader = WebGPUShaderLib().get(compute.shader)

        # Parse shader params
        _, storage_buffers_data, read_only_storage_buffers_data, _ = WebGPUShaderLib().parse(compute_shader.shader_code)

        bind_groups_entries = [[]]

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

            compute.storage_buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.COPY_SRC
            )

            # Append storage buffer to dictionary holding all storage buffers
            compute.storage_buffers[buffer_name] = storage_buffer

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

            compute.storage_buffer_types[buffer_name] = storage_data

            # Create storage buffer - data is uploaded each frame
            storage_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer(
                size=storage_data.nbytes, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
            )

            # Append storage buffer to dictionary holding all storage buffers
            compute.storage_buffers[buffer_name] = storage_buffer
            bind_groups_entries[read_only_storage_buffer_data['group']].append({
                "binding": read_only_storage_buffer_data['binding'],
                "resource": {
                    "buffer": storage_buffer,
                    "offset": 0,
                    "size": storage_buffer.size,
                },
            })

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
                "entry_point": "computeStuff",
            }
        )

        compute.map_buffer = WebGPURenderer().get_device().create_buffer(
            size=storage_data.nbytes,
            usage=wgpu.BufferUsage.MAP_READ | wgpu.BufferUsage.COPY_DST
        )

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        compute = components

        if not compute.enabled:
            return

        compute_encoder: wgpu.GPUCommandEncoder = WebGPURenderer().get_device().create_command_encoder()

        invocation_count = int(compute.storage_buffers['inputBuffer'].size / 4.0)

        input_storage_data = self.get_cpu_buffer_type(compute, 'inputBuffer')

        if input_storage_data != None:
            input_data = np.zeros((invocation_count, 1, 1))

            for i in range(invocation_count):
                input_data[i] = 0.1 * i

            input_storage_data["data"] = np.ascontiguousarray(input_data)

            self.set_storage_buffer(compute, compute_encoder, 'inputBuffer', input_storage_data)

        compute_pass: wgpu.GPUComputePassEncoder = compute_encoder.begin_compute_pass()

        # Use compute pass
        compute_pass.set_pipeline(compute.pipeline)

        # Set the pass bind groups
        for index, bind_group in enumerate(compute.bind_groups):
            compute_pass.set_bind_group(index, bind_group, [], 0, 1)

        workgroup_size = 32
        workgroup_count = int(np.ceil((invocation_count + workgroup_size - 1) / workgroup_size))

        compute_pass.dispatch_workgroups(workgroup_count, 1, 1)

        # Finalize compute pass
        compute_pass.end()

        # Before encoder.finish
        compute_encoder.copy_buffer_to_buffer(compute.storage_buffers['outputBuffer'], 0, compute.map_buffer, 0, compute.storage_buffers['inputBuffer'].size)

        WebGPURenderer().get_device().queue.submit([compute_encoder.finish()])

        self.show_results(compute)

    def get_cpu_buffer_type(self, compute, buffer_name: str) -> CPUBuffer | None:
        if buffer_name in compute.storage_buffer_types.keys():
            return compute.storage_buffer_types[buffer_name]
        return None
    
    def set_storage_buffer(self, compute: WebGPUComputeComponent, encoder: wgpu.GPUCommandEncoder, storage_name: str, storage_data: CPUBuffer):
        storage_buffer = compute.storage_buffers[storage_name]

        temporary_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer_with_data(
            data=storage_data.mem, usage=wgpu.BufferUsage.COPY_SRC
        )

        encoder.copy_buffer_to_buffer(
            temporary_buffer, 0, storage_buffer, 0, storage_data.mem.nbytes
        )

        temporary_buffer.destroy()
    
    def show_results(self, compute: WebGPUComputeComponent):
        compute.map_buffer.map(mode=wgpu.MapMode.READ, size=compute.storage_buffers['inputBuffer'].size)
        output = compute.map_buffer.read_mapped(buffer_offset=0, size=compute.storage_buffers['inputBuffer'].size, copy=False)

        print(len(output) / 4.0)

        # Iterate over the byte array in chunks of 4 bytes
        float_list = []
        for i in range(0, len(output), 4):
            # Extract 4 bytes
            four_bytes = output[i:i+4]
            # Unpack bytes as float (assuming little-endian format)
            float_value = struct.unpack('<f', four_bytes)[0]
            float_list.append(float_value)

        input_storage_data = self.get_cpu_buffer_type(compute, 'inputBuffer')

        # Print the resulting float values
        for i, f in enumerate(float_list):
            print(f"({i}) input: {input_storage_data['data'][0][i][0]} -> output: {f}")
                
        compute.map_buffer.unmap()

        compute.enabled = False
