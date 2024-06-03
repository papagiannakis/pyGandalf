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
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

"""
Showcase of sphere with textures and Physically Based Rendering(PBR).
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Physically Based Rendering(PBR) with Textured Sphere', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('Physically Based Rendering(PBR) with Textured Sphere')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    cerberus = scene.enroll_entity()
    light = scene.enroll_entity()

    # Build textures
    WebGPUTextureLib().build('cerberus_albedo', TextureData(TEXTURES_PATH / 'Cerberus' / 'Cerberus_A.png'))
    WebGPUTextureLib().build('cerberus_normal', TextureData(TEXTURES_PATH / 'Cerberus' / 'Cerberus_N.png'))
    WebGPUTextureLib().build('cerberus_metallic', TextureData(TEXTURES_PATH / 'Cerberus' / 'Cerberus_M.png'))
    WebGPUTextureLib().build('cerberus_roughness', TextureData(TEXTURES_PATH / 'Cerberus' / 'Cerberus_R.png'))

    # Build shaders
    WebGPUShaderLib().build('pbr_mesh', SHADERS_PATH / 'webgpu' / 'lit_pbr.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_PBR', MaterialData('pbr_mesh', ['cerberus_albedo', 'cerberus_normal', 'cerberus_metallic', 'cerberus_roughness']))

    # Load models
    OpenGLMeshLib().build('cerberus_mesh', MODELS_PATH / 'cerberus_lp.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to cerberus
    scene.add_component(cerberus, InfoComponent("cerberus"))
    scene.add_component(cerberus, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0.1, 0.1, 0.1)))
    scene.add_component(cerberus, LinkComponent(root))
    scene.add_component(cerberus, WebGPUStaticMeshComponent('cerberus_mesh'))
    scene.add_component(cerberus, WebGPUMaterialComponent('M_PBR'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 0, 4.5), glm.vec3(50, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 100.0))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-8, 3, -15.0), glm.vec3(22, 40, 0), glm.vec3(1, 1, 1)))
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