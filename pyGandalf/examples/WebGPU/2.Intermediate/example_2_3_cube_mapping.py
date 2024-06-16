from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow

from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData, MaterialDescriptor
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData, TextureDescriptor
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.mesh_lib import MeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import wgpu
import numpy as np

"""
Showcase of a skybox using cube mapping.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Cube Mapping - Skybox', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('Cube Mapping - Skybox')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    bunny = scene.enroll_entity()
    light = scene.enroll_entity()
    skybox = scene.enroll_entity()

    # Array that holds all the skybox textures
    skybox_textures = [
        TEXTURES_PATH / 'skybox' / 'sea' / 'right.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'left.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'top.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'bottom.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'front.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'back.jpg'
    ]

    # Vertices for the cube
    vertices = np.array([
        [-1.0, -1.0, -1.0], [-1.0, -1.0,  1.0], [-1.0,  1.0,  1.0], [ 1.0,  1.0, -1.0],
        [-1.0, -1.0, -1.0], [-1.0,  1.0, -1.0], [1.0, -1.0,  1.0], [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0], [ 1.0,  1.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0],

        [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0,  1.0, -1.0], [ 1.0, -1.0,  1.0],
        [-1.0, -1.0,  1.0], [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0], [1.0,  1.0,  1.0], [1.0, -1.0, -1.0], [1.0,  1.0, -1.0],

        [1.0, -1.0, -1.0], [1.0,  1.0,  1.0], [1.0, -1.0,  1.0], [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0], [-1.0,  1.0, -1.0], [1.0,  1.0,  1.0], [-1.0,  1.0, -1.0],
        [-1.0,  1.0,  1.0], [1.0,  1.0,  1.0], [-1.0,  1.0,  1.0], [1.0, -1.0,  1.0]
    ], dtype=np.float32)

    # Build textures
    WebGPUTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    WebGPUTextureLib().build('cube_map', TextureData(path=skybox_textures), descriptor=TextureDescriptor(flip=True, view_dimention=wgpu.TextureViewDimension.cube, array_layer_count=6))

    # Build shaders
    WebGPUShaderLib().build('default_mesh', SHADERS_PATH / 'webgpu' / 'lit_blinn_phong.wgsl')
    WebGPUShaderLib().build('skybox', SHADERS_PATH / 'webgpu' / 'skybox.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_Bunny', MaterialData('default_mesh', ['white_texture']))
    WebGPUMaterialLib().build('M_Skybox', MaterialData('skybox', ['cube_map']), MaterialDescriptor(cull_mode=wgpu.CullMode.back))

    # Load models
    MeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to skybox
    scene.add_component(skybox, InfoComponent("skybox"))
    scene.add_component(skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(skybox, LinkComponent(None))
    scene.add_component(skybox, WebGPUStaticMeshComponent('skybox', [vertices]))
    scene.add_component(skybox, WebGPUMaterialComponent('M_Skybox'))

    # Register components to bunny
    scene.add_component(bunny, InfoComponent("bunny"))
    scene.add_component(bunny, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(bunny, LinkComponent(root))
    scene.add_component(bunny, WebGPUStaticMeshComponent('bunny_mesh'))
    scene.add_component(bunny, WebGPUMaterialComponent('M_Bunny'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-0.25, 1.0, -4), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()