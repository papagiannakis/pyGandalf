from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.core.input_manager import InputManager

from pyGandalf.scene.components import Component
from pyGandalf.scene.entity import Entity
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem
from pyGandalf.systems.webgpu_compute_pipeline_system import WebGPUComputePipelineSystem
from pyGandalf.systems.system import System

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData, TextureDescriptor
from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.compute_utilities import ComputeUtilities

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH
from pyGandalf.utilities.logger import logger

import glfw
import numpy as np

"""
Showcase of a more advanced compute pipeline example.
We have an input image and through a compute shader we apply a filter to it
To dispatch the compute shader press the SPACE button.
You can select to show (in the next dispatch) a white image or the filtered image by pressing R.
"""

class ComputeShowcaseComponent(Component):
    def __init__(self) -> None:
        self.output_requested = False
        self.reset = False

class ComputeShowcaseSystem(System):
    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        showcase, compute = components

        input_texture_inst = WebGPUTextureLib().get_instance('butterfly')

        compute.work_group = 8
        compute.invocation_count_x = input_texture_inst.data.width
        compute.invocation_count_y = input_texture_inst.data.height

    def on_update_entity(self, ts: float, entity: Entity, components: Component | tuple[Component]):
        showcase, compute = components

        if InputManager().get_key_press(glfw.KEY_R):
            showcase.reset = not showcase.reset

        if InputManager().get_key_press(glfw.KEY_SPACE):
            uniform_data = ComputeUtilities().get_cpu_buffer(compute, 'u_Uniforms')
            if uniform_data != None:
                uniform_data["reset"] = np.float32(1.0 if showcase.reset else 0.0)
                ComputeUtilities().set_uniform_buffer(compute, 'u_Uniforms', uniform_data)

            compute.dispatch = True
            showcase.output_requested = True

        if compute.output_ready and showcase.output_requested:
            print('Compute Finished!')
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
    input = scene.enroll_entity()
    compute = scene.enroll_entity()
    camera = scene.enroll_entity()

    # Build textures
    WebGPUTextureLib().build('butterfly', TextureData(path=TEXTURES_PATH / 'input.jpg'), TextureDescriptor(flip=True, view_format=wgpu.TextureFormat.rgba8unorm, usage=wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING))
    input_texture_inst = WebGPUTextureLib().get_instance('butterfly')
    WebGPUTextureLib().build('output_texture', TextureData(width=input_texture_inst.data.width, height=input_texture_inst.data.height), TextureDescriptor(view_format=wgpu.TextureFormat.rgba8unorm, usage=wgpu.TextureUsage.COPY_SRC | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.STORAGE_BINDING))
    
    # Build shaders
    WebGPUShaderLib().build('convolution_filter_compute', SHADERS_PATH / 'webgpu' / 'convolution_filter_compute.wgsl')
    WebGPUShaderLib().build('textured_shader', SHADERS_PATH / 'webgpu' / 'unlit_textured.wgsl')

    # Build materials
    WebGPUMaterialLib().build('M_InputTexture', MaterialData('textured_shader', ['butterfly']))
    WebGPUMaterialLib().build('M_OutputTexture', MaterialData('textured_shader', ['output_texture']))

    # Vertices of the quad
    vertices = np.array([
        [-0.5, -0.5, 0.0], # 0 - Bottom left
        [ 0.5, -0.5, 0.0], # 1 - Bottom right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [-0.5,  0.5, 0.0], # 3 - Top left
        [-0.5, -0.5, 0.0]  # 0 - Bottom left
    ], dtype=np.float32)

    # Texture coordinates of the quad
    texture_coords = np.array([
        [0.0, 1.0], # 0
        [1.0, 1.0], # 1
        [1.0, 0.0], # 2
        [1.0, 0.0], # 2
        [0.0, 0.0], # 3
        [0.0, 1.0]  # 0
    ], dtype=np.float32)

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to input
    scene.add_component(input, InfoComponent("input"))
    scene.add_component(input, TransformComponent(glm.vec3(-2, 0, 0), glm.vec3(0, 180, 0), glm.vec3(2, 2, 2)))
    scene.add_component(input, LinkComponent(root))
    scene.add_component(input, WebGPUStaticMeshComponent('input_texture', [vertices, texture_coords]))
    scene.add_component(input, WebGPUMaterialComponent('M_InputTexture'))

    # Register components to compute
    scene.add_component(compute, InfoComponent("compute"))
    scene.add_component(compute, TransformComponent(glm.vec3(2, 0, 0), glm.vec3(0, 180, 0), glm.vec3(2, 2, 2)))
    scene.add_component(compute, LinkComponent(root))
    scene.add_component(compute, WebGPUStaticMeshComponent('output_texture', [vertices, texture_coords]))
    scene.add_component(compute, WebGPUMaterialComponent('M_OutputTexture'))
    scene.add_component(compute, WebGPUComputeComponent('convolution_filter_compute', ['butterfly', 'output_texture'], 'computeSobelX'))
    scene.add_component(compute, ComputeShowcaseComponent())

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, -5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))
    scene.register_system(WebGPUComputePipelineSystem([WebGPUComputeComponent]))
    scene.register_system(ComputeShowcaseSystem([ComputeShowcaseComponent, WebGPUComputeComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()