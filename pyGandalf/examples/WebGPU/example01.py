from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.components import Component, CameraComponent, CameraControllerComponent, LightComponent, WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent, InfoComponent
from pyGandalf.systems.system import System
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.light_system import LightSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.core.input_manager import InputManager

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH

from pyGandalf.utilities.logger import logger

import glm
import glfw
import numpy as np

class MovementComponent(Component):
    def __init__(self) -> None:
        self.selected = False
        self.speed = 2.5

class MovementSystem(System):
    """
    The system responsible for moving.
    """

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        movement, transform, info = components

        if InputManager().get_key_down(glfw.KEY_1):
            if info.tag == 'e1': movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_2):
            if info.tag == 'e2':movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_P):
            if info.tag == 'pistol':movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_M):
            if info.tag == 'monkeh':movement.selected = True
            else: movement.selected = False

        if movement.selected:
            if InputManager().get_key_down(glfw.KEY_D):
                transform.translation.x += movement.speed * ts
            elif InputManager().get_key_down(glfw.KEY_A):
                transform.translation.x -= movement.speed * ts
            if InputManager().get_key_down(glfw.KEY_W):
                transform.translation.y += movement.speed * ts
            elif InputManager().get_key_down(glfw.KEY_S):
                transform.translation.y -= movement.speed * ts

def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    pistol = scene.enroll_entity()
    monkeh = scene.enroll_entity()
    light = scene.enroll_entity()
    camera = scene.enroll_entity()

    # Create application
    Application().create(WebGPUWindow('Hello World', 1280, 720, True), WebGPURenderer)

    # Build textures
    WebGPUTextureLib().build('dark_wood_texture', TEXTURES_PATH/'dark_wood_texture.jpg')
    WebGPUTextureLib().build('pistol_albedo', TEXTURES_PATH/'fa_flintlockPistol_albedo.jpg')
    WebGPUTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])

    # Build shaders 
    WebGPUShaderLib().build('unlit', SHADERS_PATH / 'web_gpu' / 'unlit.wgsl')
    WebGPUShaderLib().build('unlit_textured', SHADERS_PATH / 'web_gpu' / 'unlit_textured.wgsl')
    WebGPUShaderLib().build('lit_blinn_phong', SHADERS_PATH / 'web_gpu' / 'lit_blinn_phong.wgsl')

    # Build Materials
    WebGPUMaterialLib().build('M_Unlit', MaterialData('unlit', []))
    WebGPUMaterialLib().build('M_Unlit_Textured', MaterialData('unlit_textured', ['dark_wood_texture']))
    WebGPUMaterialLib().build('M_Monkeh', MaterialData('lit_blinn_phong', ['white_texture']))
    WebGPUMaterialLib().build('M_Pistol', MaterialData('lit_blinn_phong', ['pistol_albedo']))

    # Load models
    OpenGLMeshLib().build('monkeh_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')

    scene.add_component(pistol, InfoComponent('pistol'))
    scene.add_component(pistol, TransformComponent(glm.vec3(-3, 0, 0), glm.vec3(0, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(pistol, WebGPUStaticMeshComponent('pistol_mesh'))
    scene.add_component(pistol, WebGPUMaterialComponent('M_Pistol'))
    scene.add_component(pistol, MovementComponent())

    # Register components to monkeh
    scene.add_component(monkeh, InfoComponent("monkeh"))
    scene.add_component(monkeh, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1.5, 1.5, 1.5)))
    scene.add_component(monkeh, WebGPUStaticMeshComponent('monkeh_mesh'))
    scene.add_component(monkeh, WebGPUMaterialComponent('M_Monkeh'))
    scene.add_component(monkeh, MovementComponent())

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 1, 2), glm.vec3(0, 0, 0), glm.vec3(1, 1, 0)))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent('camera'))
    scene.add_component(camera, TransformComponent(glm.vec3(0.0, 0.0, 10.0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, CameraComponent(75, 1.778, 0.001, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    # scene.add_component(camera, CameraControllerComponent())

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(MovementSystem([MovementComponent, TransformComponent, InfoComponent]))
    # scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()