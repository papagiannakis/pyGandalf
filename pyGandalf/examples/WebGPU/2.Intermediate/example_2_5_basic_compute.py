from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.core.input_manager import InputManager

from pyGandalf.scene.components import Component
from pyGandalf.scene.entity import Entity
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem
from pyGandalf.systems.webgpu_compute_pipeline_system import WebGPUComputePipelineSystem
from pyGandalf.systems.system import System

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.compute_utilities import ComputeUtilities

from pyGandalf.utilities.definitions import SHADERS_PATH
from pyGandalf.utilities.logger import logger

import glfw
import numpy as np

"""
Showcase of a basic compute pipeline example.
We have a buffer of 64 floats from 0.0 to 6.3, we use a compute shader to multiply them by 10 and we get back the numbers from 0.0 to 63.0
To dispatch the compute shader press the SPACE button.
"""

class ComputeShowcaseComponent(Component):
    def __init__(self) -> None:
        self.output_requested = False

class ComputeShowcaseSystem(System):
    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        showcase, compute = components
        compute.work_group = 32
        compute.invocation_count_x = 64

    def on_update_entity(self, ts: float, entity: Entity, components: Component | tuple[Component]):
        showcase, compute = components

        if InputManager().get_key_press(glfw.KEY_SPACE):
            input_storage_data = ComputeUtilities().get_cpu_buffer(compute, 'inputBuffer')

            if input_storage_data != None:
                input_data = np.zeros((compute.invocation_count_x, 1, 1))

                for i in range(compute.invocation_count_x):
                    input_data[i] = 0.1 * i

                input_storage_data["data"] = np.ascontiguousarray(input_data)

                ComputeUtilities().set_storage_buffer(compute, 'inputBuffer', input_storage_data)

                compute.dispatch = True
                showcase.output_requested = True

                print('Input data:')
                print(input_storage_data.data)

        if compute.output_ready and showcase.output_requested:
            print('Output data:')
            for output in compute.output:
                cpu_buffer = ComputeUtilities().bytearray_to_cpu_buffer(output, [('number', np.float32, (64, 1, 1))])
                print(cpu_buffer.data)
            showcase.output_requested = False

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Blinn-Phong Model', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('Blinn-Phong Model')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    compute = scene.enroll_entity()

    # Build shaders
    WebGPUShaderLib().build('simple_compute', SHADERS_PATH / 'webgpu' / 'simple_compute.wgsl')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to compute
    scene.add_component(compute, InfoComponent("compute"))
    scene.add_component(compute, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(compute, LinkComponent(root))
    scene.add_component(compute, WebGPUComputeComponent('simple_compute', [], 'computeStuff'))
    scene.add_component(compute, ComputeShowcaseComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(WebGPUComputePipelineSystem([WebGPUComputeComponent]))
    scene.register_system(ComputeShowcaseSystem([ComputeShowcaseComponent, WebGPUComputeComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()