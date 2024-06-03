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
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import wgpu
import numpy as np

"""
Showcase of reflection and refraction materials when using a skybox.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Environment Mapping - Reflection and Refraction', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('Environment Mapping - Reflection and Refraction')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    reflection_bunny = scene.enroll_entity()
    refraction_bunny = scene.enroll_entity()
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
    WebGPUShaderLib().build('skybox', SHADERS_PATH / 'webgpu' / 'skybox.wgsl')
    WebGPUShaderLib().build('cubemap_reflection', SHADERS_PATH / 'webgpu' / 'cubemap_reflection.wgsl')
    WebGPUShaderLib().build('cubemap_refraction', SHADERS_PATH / 'webgpu' / 'cubemap_refraction.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_Skybox', MaterialData('skybox', ['cube_map']), MaterialDescriptor(cull_mode=wgpu.CullMode.back))
    WebGPUMaterialLib().build('M_EnvironmentReflection', MaterialData('cubemap_reflection', ['cube_map']))
    WebGPUMaterialLib().build('M_EnvironmentRefraction', MaterialData('cubemap_refraction', ['cube_map']))

    # Load models
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

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

    # Register components to reflection bunny - acts like its a bunny made from a mirror
    scene.add_component(reflection_bunny, InfoComponent("reflection_bunny"))
    scene.add_component(reflection_bunny, TransformComponent(glm.vec3(1.5, 0, 0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(reflection_bunny, LinkComponent(root))
    scene.add_component(reflection_bunny, WebGPUStaticMeshComponent('bunny_mesh'))
    scene.add_component(reflection_bunny, WebGPUMaterialComponent('M_EnvironmentReflection'))

    # Register components to refraction bunny - acts like its a bunny made from glass
    scene.add_component(refraction_bunny, InfoComponent("refraction_bunny"))
    scene.add_component(refraction_bunny, TransformComponent(glm.vec3(-1.5, 0, 0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(refraction_bunny, LinkComponent(root))
    scene.add_component(refraction_bunny, WebGPUStaticMeshComponent('bunny_mesh'))
    scene.add_component(refraction_bunny, WebGPUMaterialComponent('M_EnvironmentRefraction'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-0.25, 1, -4), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
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