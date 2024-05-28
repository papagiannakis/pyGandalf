from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.core.input_manager import InputManager
from pyGandalf.core.event_manager import EventManager
from pyGandalf.core.events import EventType

from pyGandalf.systems.system import System, SystemState
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import Component, InfoComponent, TransformComponent, LinkComponent, WebGPUMaterialComponent, CameraComponent, WebGPUStaticMeshComponent, LightComponent

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np
import glfw
import glm

"""
Showcase of obj model loading with textures and basic Blinn-Phong lighting consisting of two scenes.
A custom component is added to the entities to rotate around.
Event system showcase:
- Press SPACE to change between the two scenes
- Press P to PLAY / PAUSE the DemoSystem that rotates around entites.
- There attached callbacks when a scene change happens and the DemoSystem state changes, check console.
"""

class DemoComponent:
    def __init__(self, axis, speed, rotate_around, main_camera) -> None:
        self.axis = axis
        self.speed = speed
        self.rotate_around = rotate_around
        self.main_camera = main_camera

class DemoSystem(System):
    """
    The system responsible showcasing new features.
    """

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        demo, transform, info = components

        if demo.rotate_around == True:
            if demo.axis[0] == 1:
                transform.rotation[0] += demo.speed * ts

            if demo.axis[1] == 1:
                transform.rotation[1] += demo.speed * ts

            if demo.axis[2] == 1:
                transform.rotation[2] += demo.speed * ts

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene1 = Scene('The first scene')
    scene2 = Scene('A rabbit in marbles')

    # Create Enroll entities to registry
    root1 = scene1.enroll_entity()
    camera1 = scene1.enroll_entity()
    monkeh1 = scene1.enroll_entity()
    pistol1 = scene1.enroll_entity()
    floor1 = scene1.enroll_entity()
    light1 = scene1.enroll_entity()

    root2 = scene2.enroll_entity()
    camera2 = scene2.enroll_entity()
    floor2 = scene2.enroll_entity()
    floor3 = scene2.enroll_entity()
    light2 = scene2.enroll_entity()
    rabbit2 = scene2.enroll_entity()

    vertices = np.array([
        [-0.5, -0.5, 0.0], #0
        [ 0.5, -0.5, 0.0], #1
        [ 0.5,  0.5, 0.0], #2
        [ 0.5,  0.5, 0.0], #2
        [-0.5,  0.5, 0.0], #3
        [-0.5, -0.5, 0.0]  #0
    ], dtype=np.float32)

    texture_coords = np.array([
        [0.0, 1.0], #0
        [1.0, 1.0], #1
        [1.0, 0.0], #2
        [1.0, 0.0], #2
        [0.0, 0.0], #3
        [0.0, 1.0]  #0
    ], dtype=np.float32)

    normals = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0] 
    ], dtype=np.float32)

    Application().create(WebGPUWindow('ECSS Cube', 1280, 720, True), WebGPURenderer)

    # Build textures
    WebGPUTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    WebGPUTextureLib().build('rabbit_albedo', TEXTURES_PATH/'fg_spkRabbit_albedo.jpg')
    WebGPUTextureLib().build('flintlockPistol_albedo', TEXTURES_PATH/'fa_flintlockPistol_albedo.jpg')
    WebGPUTextureLib().build('dark_wood_texture', TEXTURES_PATH/'dark_wood_texture.jpg')
    WebGPUTextureLib().build('marble_texture', TEXTURES_PATH/'4K_carrara_gioa_p1004___polished___marble_diffuse.png')

    # Build shaders
    WebGPUShaderLib().build('default_mesh', SHADERS_PATH/ 'web_gpu' / 'lit_blinn_phong.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_Rabbit', MaterialData('default_mesh', ['rabbit_albedo']))
    WebGPUMaterialLib().build('M_Monkeh', MaterialData('default_mesh', ['white_texture']))
    WebGPUMaterialLib().build('M_Floor1', MaterialData('default_mesh', ['dark_wood_texture']))
    WebGPUMaterialLib().build('M_Floor2', MaterialData('default_mesh', ['marble_texture']))
    WebGPUMaterialLib().build('M_Pistol', MaterialData('default_mesh', ['flintlockPistol_albedo']))

    # Load models
    OpenGLMeshLib().build('monkeh_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('rabbit_mesh', MODELS_PATH/'fg_spkRabbit.obj')
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')

    # Root entity of scene1
    scene1.add_component(root1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene1.add_component(root1, InfoComponent("root1"))
    scene1.add_component(root1, LinkComponent(None))

    # Register components to monkeh
    scene1.add_component(monkeh1, InfoComponent("monkeh"))
    scene1.add_component(monkeh1, TransformComponent(glm.vec3(5, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1.5, 1.5, 1.5)))
    scene1.add_component(monkeh1, LinkComponent(root1))
    scene1.add_component(monkeh1, WebGPUStaticMeshComponent('monkeh_mesh'))
    scene1.add_component(monkeh1, WebGPUMaterialComponent('M_Monkeh'))
    scene1.add_component(monkeh1, DemoComponent((1, 0, 0), 25, True, False))

    # Register components to pistol
    scene1.add_component(pistol1, InfoComponent("pistol"))
    scene1.add_component(pistol1, TransformComponent(glm.vec3(-2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(20, 20, 20)))
    scene1.add_component(pistol1, LinkComponent(root1))
    scene1.add_component(pistol1, WebGPUStaticMeshComponent('pistol_mesh'))
    scene1.add_component(pistol1, WebGPUMaterialComponent('M_Pistol'))
    scene1.add_component(pistol1, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to floor
    scene1.add_component(floor1, InfoComponent("floor"))
    scene1.add_component(floor1, TransformComponent(glm.vec3(0, -2, 0), glm.vec3(270, 0, 0), glm.vec3(20, 20, 20)))
    scene1.add_component(floor1, LinkComponent(root1))
    scene1.add_component(floor1, WebGPUStaticMeshComponent('floor_mesh', [vertices, normals, texture_coords]))
    scene1.add_component(floor1, WebGPUMaterialComponent('M_Floor1'))

    # Register components to light
    scene1.add_component(light1, InfoComponent("light"))
    scene1.add_component(light1, TransformComponent(glm.vec3(-3, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene1.add_component(light1, LinkComponent(root1))
    scene1.add_component(light1, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene1.add_component(camera1, InfoComponent("camera"))
    scene1.add_component(camera1, TransformComponent(glm.vec3(0, 5, -10), glm.vec3(25, 0, 0), glm.vec3(1, 1, 1)))
    scene1.add_component(camera1, LinkComponent(root1))
    scene1.add_component(camera1, CameraComponent(45, 1.778, 0.1, 1000, 5.0, CameraComponent.Type.PERSPECTIVE))

    # Create Register systems
    scene1.register_system(TransformSystem([TransformComponent]))
    scene1.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene1.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene1.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene1.register_system(LightSystem([LightComponent, TransformComponent]))
    scene1.register_system(DemoSystem([DemoComponent, TransformComponent, InfoComponent]))

    #############################################################################################################################

    # Root entity of scene2
    scene2.add_component(root2, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene2.add_component(root2, InfoComponent("root2"))
    scene2.add_component(root2, LinkComponent(None))

    # Register components to camera
    scene2.add_component(camera2, InfoComponent("camera"))
    scene2.add_component(camera2, TransformComponent(glm.vec3(0, 5, -10), glm.vec3(25, 0, 0), glm.vec3(1, 1, 1)))
    scene2.add_component(camera2, LinkComponent(root2))
    scene2.add_component(camera2, CameraComponent(45, 1.778, 0.1, 1000, 5.0, CameraComponent.Type.PERSPECTIVE))

    # Register components to light
    scene2.add_component(light2, InfoComponent("light"))
    scene2.add_component(light2, TransformComponent(glm.vec3(0, 10, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene2.add_component(light2, LinkComponent(root2))
    scene2.add_component(light2, LightComponent(glm.vec3(1.0, 1.0, 1.0), 1))

    # Register components to floor
    scene2.add_component(floor2, InfoComponent("floor2"))
    scene2.add_component(floor2, TransformComponent(glm.vec3(0, -2, 0), glm.vec3(270, 0, 0), glm.vec3(25, 20, 20)))
    scene2.add_component(floor2, LinkComponent(root2))
    scene2.add_component(floor2, WebGPUStaticMeshComponent('floor_mesh', [vertices, normals, texture_coords]))
    scene2.add_component(floor2, WebGPUMaterialComponent('M_Floor2')).glossiness = 0.01

    scene2.add_component(floor3, InfoComponent("floor3"))
    scene2.add_component(floor3, TransformComponent(glm.vec3(0, 0, 3), glm.vec3(-20, 180, 0), glm.vec3(25, 20, 20)))
    scene2.add_component(floor3, LinkComponent(root2))
    scene2.add_component(floor3, WebGPUStaticMeshComponent('floor_mesh', [vertices, normals, texture_coords]))
    scene2.add_component(floor3, WebGPUMaterialComponent('M_Floor2')).glossiness = 0.01

    # Register components to rabbit
    scene2.add_component(rabbit2, InfoComponent("rabbit"))
    scene2.add_component(rabbit2, TransformComponent(glm.vec3(0, -2, 0), glm.vec3(0, 0, 0), glm.vec3(40, 40, 40)))
    scene2.add_component(rabbit2, LinkComponent(root2))
    scene2.add_component(rabbit2, WebGPUStaticMeshComponent('rabbit_mesh'))
    scene2.add_component(rabbit2, WebGPUMaterialComponent('M_Rabbit'))
    scene2.add_component(rabbit2, DemoComponent((0, 1, 0), 25, True, False))

    # Create Register systems
    scene2.register_system(TransformSystem([TransformComponent]))
    scene2.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene2.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene2.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene2.register_system(LightSystem([LightComponent, TransformComponent]))
    scene2.register_system(DemoSystem([DemoComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene1)
    SceneManager().add_scene(scene2)

    # Attach events
    def on_scene_change(s1, s2):
        print(f'Changed from scene: \'{s1.name}\' to scene: \'{s2.name}\'')
    
    def on_system_state(type, state):
        print(f'System of type: {type} changed to state: {state}')

    def on_key_callback(key, modifiers):
        if key == glfw.KEY_SPACE:
            scene = SceneManager().get_active_scene()
            if scene == scene1:
                SceneManager().change_scene(scene2)
            else:
                SceneManager().change_scene(scene1)
            
        if key == glfw.KEY_P:
            state = SceneManager().get_active_scene().get_system(DemoSystem).get_state()
            if state is SystemState.PAUSE:
                state = SceneManager().get_active_scene().get_system(DemoSystem).set_state(SystemState.PLAY)
            else:
                state = SceneManager().get_active_scene().get_system(DemoSystem).set_state(SystemState.PAUSE)

    EventManager().attach_callback(EventType.SCENE_CHANGE, on_scene_change, True)
    EventManager().attach_callback(EventType.KEY_PRESS, on_key_callback, True)
    EventManager().attach_callback(EventType.SYSTEM_STATE, on_system_state, True)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()