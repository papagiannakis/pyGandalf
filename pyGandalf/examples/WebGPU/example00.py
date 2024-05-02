from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.components import Component, CameraComponent, WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent, InfoComponent
from pyGandalf.systems.system import System
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib

from pyGandalf.core.input_manager import InputManager

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH

from pyGandalf.utilities.logger import logger

import glm
import glfw
import numpy as np

class MovementComponent(Component):
    def __init__(self) -> None:
        self.selected = False
        self.speed = 0.5

class MovementSystem(System):
    """
    The system responsible for moving.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        movement, transform, info = components
        pass

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        movement, transform, info = components

        if InputManager().get_key_down(glfw.KEY_1):
            if info.tag == 'e1': movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_2):
            if info.tag == 'e2':movement.selected = True
            else: movement.selected = False
        if InputManager().get_key_down(glfw.KEY_3):
            if info.tag == 'e3':movement.selected = True
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
    entity1 = scene.enroll_entity()
    entity2 = scene.enroll_entity()
    entity3 = scene.enroll_entity()
    camera = scene.enroll_entity()

    # Create application
    Application().create(WebGPUWindow('Hello World', 1280, 720, True), WebGPURenderer)

    # Build textures
    WebGPUTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')
    WebGPUTextureLib().build('dark_wood_texture', TEXTURES_PATH/'dark_wood_texture.jpg')

    # Build shaders 
    WebGPUShaderLib().build('unlit', SHADERS_PATH / 'web_gpu' / 'unlit.wgsl')
    WebGPUShaderLib().build('unlit_textured', SHADERS_PATH / 'web_gpu' / 'unlit_textured.wgsl')

    # Build Materials
    WebGPUMaterialLib().build('M_Unlit', MaterialData('unlit', []))
    WebGPUMaterialLib().build('M_Unlit_Textured_1', MaterialData('unlit_textured', ['uoc_logo']))
    WebGPUMaterialLib().build('M_Unlit_Textured_2', MaterialData('unlit_textured', ['dark_wood_texture']))

    vertex_data_1 = np.array([
        [-0.5, -0.5, 0.0],
        [ 0.5, -0.5, 0.0],
        [ 0.5,  0.5, 0.0],
        [-0.5,  0.5, 0.0],
    ], np.float32)

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

    index_data = np.array([
        [0,1,2],
        [0,2,3],
    ], np.uint32)

    texture_coords_1 = np.array([
        [0.0, 1.0], #0
        [1.0, 1.0], #1
        [1.0, 0.0], #2
        [0.0, 0.0], #3
    ], dtype=np.float32)

    # Add components
    scene.add_component(entity1, InfoComponent('e1'))
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0.5, 0.5, 0.5)))
    scene.add_component(entity1, WebGPUStaticMeshComponent('triangle_1', [vertex_data_1], index_data))
    scene.add_component(entity1, WebGPUMaterialComponent('M_Unlit'))
    scene.add_component(entity1, MovementComponent())

    scene.add_component(entity2, InfoComponent('e2'))
    scene.add_component(entity2, TransformComponent(glm.vec3(-1, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, WebGPUStaticMeshComponent('triangle_2', [vertices, texture_coords]))
    scene.add_component(entity2, WebGPUMaterialComponent('M_Unlit_Textured_1'))
    scene.add_component(entity2, MovementComponent())

    scene.add_component(entity3, InfoComponent('e3'))
    scene.add_component(entity3, TransformComponent(glm.vec3(1, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0.75, 0.75, 0.75)))
    scene.add_component(entity3, WebGPUStaticMeshComponent('triangle_3', [vertex_data_1, texture_coords_1], index_data))
    scene.add_component(entity3, WebGPUMaterialComponent('M_Unlit_Textured_2'))
    scene.add_component(entity3, MovementComponent())

    # Register components to camera
    scene.add_component(camera, InfoComponent('camera'))
    scene.add_component(camera, TransformComponent(glm.vec3(0.0, 0, -2.0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, CameraComponent(75, 1.778, 0.001, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(MovementSystem([MovementComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()