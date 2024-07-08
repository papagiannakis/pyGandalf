from pyGandalf.scene.components import WebGPUComputeComponent
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.utilities.webgpu_material_lib import CPUBuffer

from pyGandalf.utilities.logger import logger

import wgpu
import numpy as np

class ComputeUtilities(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ComputeUtilities, cls).__new__(cls)
        return cls.instance
    
    def get_cpu_buffer(cls, compute: WebGPUComputeComponent, buffer_name: str) -> CPUBuffer | None:
        """Get a CPUBuffer with the given name from the given compute component.

        Args:
            compute (WebGPUComputeComponent): The compute component to retrieve the buffer from.
            buffer_name (str): The name of the buffer.

        Returns:
            CPUBuffer | None: A CPUBuffer instance with the given name from the given compute component.
        """
        if buffer_name in compute.buffer_types.keys():
            return compute.buffer_types[buffer_name]
        return None
    
    def set_uniform_buffer(cls, compute: WebGPUComputeComponent, uniform_name: str, uniform_data: CPUBuffer):
        """Sets the uniform buffer with the provided name (if valid), with the provided data.

        Args:
            compute (WebGPUComputeComponent): The compute component to retrieve the buffer from.
            uniform_name (str): The name of the uniform buffer to set.
            uniform_data (CPUBuffer): The new data for the uniform buffer.
        """
        uniform_buffer = compute.uniform_buffers[uniform_name]
        WebGPURenderer().write_buffer(uniform_buffer, uniform_data.mem)
    
    def set_storage_buffer(cls, compute: WebGPUComputeComponent, storage_name: str, storage_data: CPUBuffer):
        """Stores the given data to the gpu storage buffer with the given name.

        Args:
            compute (WebGPUComputeComponent): The compute component to retrieve the buffer from.
            storage_name (str): The name of the storage buffer to store the data.
            storage_data (CPUBuffer): A CPUBuffer containg the data to store.
        """
        storage_buffer = compute.input_storage_buffers[storage_name]

        temporary_buffer: wgpu.GPUBuffer = WebGPURenderer().get_device().create_buffer_with_data(
            data=storage_data.mem, usage=wgpu.BufferUsage.COPY_SRC
        )

        if compute.encoder == None:
            compute.encoder = WebGPURenderer().get_device().create_command_encoder()

        compute.encoder.copy_buffer_to_buffer(
            temporary_buffer, 0, storage_buffer, 0, storage_data.mem.nbytes
        )

        temporary_buffer.destroy()
    
    def bytearray_to_cpu_buffer(cls, bytearray_data, buffer_structure) -> CPUBuffer | None:
        """Convert a bytearray to a CPUBuffer.

        Args:
            bytearray_data (bytearray): The input bytearray to convert.
            buffer_structure (lis[tuple[str, dtype, shape]]): The structure of the CPUBuffer as a list of tuples (name, dtype, shape).

        Returns:
            CPUBuffer | None: A CPUBuffer instance containing the data from the bytearray.
        """
        # Create an instance of CPUBuffer with the specified structure
        cpu_buffer = CPUBuffer(*buffer_structure)
        
        # Ensure the size of the bytearray matches the expected size
        expected_size = cpu_buffer.nbytes
        if len(bytearray_data) != expected_size:
            logger.error(f"Size of bytearray ({len(bytearray_data)}) does not match expected size ({expected_size})")
            return None

        # Load the data from the bytearray into the CPUBuffer
        np_array = np.frombuffer(bytearray_data, dtype=cpu_buffer.dtype)
        cpu_buffer.data[:] = np_array

        return cpu_buffer