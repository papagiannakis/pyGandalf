from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
from pyGandalf.core.input_manager import InputManager
from pyGandalf.core.event_manager import EventManager
from pyGandalf.core.events import EventType
from pyGandalf.scene.components import Component
from pyGandalf.systems.system import System
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH
from pyGandalf.utilities.logger import logger

import glfw
import numpy as np
import glm

"""
Showcase of basic usage and API with three 2d quads in a ecss hierachy.
- Press 1,2,3 to select between the entities.
- Use WASD keys to move around the selected entity.
"""

class MovementComponent(Component):
    def __init__(self) -> None:
        self.selected = False
        self.speed = 0.5

class MovementSystem(System):
    """
    The system responsible for moving.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        movement, transform, info = components
        def on_close_callback():
            print(f'Entity with name: {info.tag} says goodbye')

        EventManager().attach_callback(EventType.WINDOW_CLOSE, on_close_callback)

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        movement, transform, info = components

        if InputManager().get_key_down(glfw.KEY_1):
            if info.tag == 'e3': movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_2):
            if info.tag == 'e1': movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_3):
            if info.tag == 'e2':movement.selected = True
            else: movement.selected = False

        if movement.selected:
            if InputManager().get_key_down(glfw.KEY_D):
                transform.translation[0] += movement.speed * ts
            elif InputManager().get_key_down(glfw.KEY_A):
                transform.translation[0] -= movement.speed * ts
            if InputManager().get_key_down(glfw.KEY_W):
                transform.translation[1] += movement.speed * ts
            elif InputManager().get_key_down(glfw.KEY_S):
                transform.translation[1] -= movement.speed * ts

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    entity1 = scene.enroll_entity()
    entity2 = scene.enroll_entity()
    entity3 = scene.enroll_entity()
    camera = scene.enroll_entity()
    root = scene.enroll_entity()

    Application().create(OpenGLWindow('Hello World', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('dark_wood', TEXTURES_PATH/'dark_wood_texture.jpg')
    OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])

    # Build shaders 
    OpenGLShaderLib().build('unlit_simple', SHADERS_PATH/'unlit_simple_vertex.glsl', SHADERS_PATH/'unlit_simple_fragment.glsl')
    OpenGLShaderLib().build('unlit_textured', SHADERS_PATH/'unlit_textured_vertex.glsl', SHADERS_PATH/'unlit_textured_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('unlit_simple', []))
    OpenGLMaterialLib().build('M_Red_Textured', MaterialData('unlit_textured', ['dark_wood']))
    OpenGLMaterialLib().build('M_Blue_Textured', MaterialData('unlit_textured', ['uoc_logo']))

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

    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent("root"))
    scene.add_component(root, LinkComponent(None))

    # Register components to entity1
    scene.add_component(entity1, InfoComponent("e1"))
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(root))
    scene.add_component(entity1, StaticMeshComponent('', [vertices, texture_coords], None))
    scene.add_component(entity1, MaterialComponent('M_Red_Textured')).color = glm.vec3(1.0, 0.0, 0.0)
    scene.add_component(entity1, MovementComponent())

    # Register components to entity2
    scene.add_component(entity2, InfoComponent("e2"))
    scene.add_component(entity2, TransformComponent(glm.vec3(0.5, -1.25, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))
    scene.add_component(entity2, StaticMeshComponent('', [vertices], None))
    scene.add_component(entity2, MaterialComponent('M_Yellow_Simple')).color = glm.vec3(1.0, 1.0, 0.0)
    scene.add_component(entity2, MovementComponent())

    # Register components to entity3
    scene.add_component(entity3, InfoComponent("e3"))
    scene.add_component(entity3, TransformComponent(glm.vec3(-2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity3, LinkComponent(root))
    scene.add_component(entity3, StaticMeshComponent('', [vertices, texture_coords], None))
    scene.add_component(entity3, MaterialComponent('M_Blue_Textured')).color = glm.vec3(0.0, 0.0, 1.0)
    scene.add_component(entity3, MovementComponent())

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(MovementSystem([MovementComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    def on_pointer_entered(entered):
        if entered == 1:
            print(f'The pointer got inside')
        else:
            print(f'The pointer got outside')

    EventManager().attach_callback(EventType.CURSOR_ENTER, on_pointer_entered, True)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()