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

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, MODELS_PATH, TEXTURES_PATH
from pyGandalf.utilities.logger import logger

"""
Showcase of obj model loading with textures and basic Blinn-Phong lighting.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Blinn-Phong Textured Model', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('Blinn-Phong Textured Model')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    pistol = scene.enroll_entity()
    light = scene.enroll_entity()

    # Build textures
    WebGPUTextureLib().build('flintlockPistol_albedo', TextureData(path=TEXTURES_PATH / 'fa_flintlockPistol_albedo.jpg'))

    # Build shaders
    WebGPUShaderLib().build('default_mesh', SHADERS_PATH / 'webgpu' / 'lit_blinn_phong.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_Pistol', MaterialData('default_mesh', ['flintlockPistol_albedo']))

    # Load models
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to pistol
    scene.add_component(pistol, InfoComponent("pistol"))
    scene.add_component(pistol, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(pistol, LinkComponent(root))
    scene.add_component(pistol, WebGPUStaticMeshComponent('pistol_mesh'))
    scene.add_component(pistol, WebGPUMaterialComponent('M_Pistol'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-1, 2, -5), glm.vec3(15, 0, 0), glm.vec3(1, 1, 1)))
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