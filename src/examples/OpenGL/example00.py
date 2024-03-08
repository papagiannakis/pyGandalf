from core.application import Application
from core.opengl_window import OpenGLWindow
from systems.system import System
from systems.link_system import LinkSystem
from systems.transform_system import TransformSystem
from systems.opengl_rendering_system import OpenGLRenderingSystem
from renderer.opengl_renderer import OpenGLRenderer
from scene.entity import Entity
from scene.scene import Scene
from scene.scene_manager import SceneManager

from scene.components import InfoComponent, TransformComponent, LinkComponent, OpenGLRenderComponent, MaterialComponent

from utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from utilities.opengl_texture_lib import OpenGLTextureLib
from utilities.opengl_shader_lib import OpenGLShaderLib

from utilities.logger import logger

import glfw
import numpy as np
import glm

from definitions import SHADERS_PATH, TEXTURES_PATH

"""
Showcase of basic usage and API with three 2d quads in a ecss hierachy
"""

class MovementComponent:
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

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        movement, transform, info = components

        movement.selected = False

        if glfw.get_key(Application().get_window().get_handle(), glfw.KEY_1) == glfw.PRESS:
            if info.tag == 'e1': movement.selected = True
        elif glfw.get_key(Application().get_window().get_handle(), glfw.KEY_2) == glfw.PRESS:
            if info.tag == 'e2': movement.selected = True
        elif glfw.get_key(Application().get_window().get_handle(), glfw.KEY_3) == glfw.PRESS:
            if info.tag == 'e3': movement.selected = True

        if movement.selected:
            if glfw.get_key(Application().get_window().get_handle(), glfw.KEY_D) == glfw.PRESS:
                transform.translation[0] += movement.speed * ts
            elif glfw.get_key(Application().get_window().get_handle(), glfw.KEY_A) == glfw.PRESS:
                transform.translation[0] -= movement.speed * ts
            if glfw.get_key(Application().get_window().get_handle(), glfw.KEY_W) == glfw.PRESS:
                transform.translation[1] += movement.speed * ts
            elif glfw.get_key(Application().get_window().get_handle(), glfw.KEY_S) == glfw.PRESS:
                transform.translation[1] -= movement.speed * ts

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    entity1 = scene.enroll_entity()
    entity2 = scene.enroll_entity()
    entity3 = scene.enroll_entity()

    # Load shader source code
    vertex_shader_code = OpenGLShaderLib().load_from_file(SHADERS_PATH/'vertex_shader_code.glsl')
    fragment_shader_code_yellow = OpenGLShaderLib().load_from_file(SHADERS_PATH/'fragment_shader_code_yellow.glsl')
    textured_vertex_shader_code = OpenGLShaderLib().load_from_file(SHADERS_PATH/'textured_vertex_shader_code.glsl')
    textured_fragment_shader_code_blue = OpenGLShaderLib().load_from_file(SHADERS_PATH/'textured_fragment_shader_code_blue.glsl')
    textured_fragment_shader_code_red = OpenGLShaderLib().load_from_file(SHADERS_PATH/'textured_fragment_shader_code_red.glsl')

    Application().create(OpenGLWindow('Hello World', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('dark_wood', TEXTURES_PATH/'dark_wood_texture.jpg')
    OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])

    # Build shaders 
    OpenGLShaderLib().build('default_colored_yellow', vertex_shader_code, fragment_shader_code_yellow)
    OpenGLShaderLib().build('textured_colored_blue', textured_vertex_shader_code, textured_fragment_shader_code_blue)
    OpenGLShaderLib().build('textured_colored_red', textured_vertex_shader_code, textured_fragment_shader_code_red)
    
    # Build Materials
    OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))
    OpenGLMaterialLib().build('M_Red_Textured', MaterialData('textured_colored_red', ['dark_wood']))
    OpenGLMaterialLib().build('M_Blue_Textured', MaterialData('textured_colored_blue', ['uoc_logo']))

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

    # Register components to entity1
    scene.add_component(entity1, InfoComponent("e1"))
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(None))
    scene.add_component(entity1, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(entity1, MaterialComponent('M_Red_Textured'))
    scene.add_component(entity1, MovementComponent())

    # Register components to entity2
    scene.add_component(entity2, InfoComponent("e2"))
    scene.add_component(entity2, TransformComponent(glm.vec3(2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))
    scene.add_component(entity2, OpenGLRenderComponent([vertices], None))
    scene.add_component(entity2, MaterialComponent('M_Yellow_Simple'))
    scene.add_component(entity2, MovementComponent())

    # Register components to entity3
    scene.add_component(entity3, InfoComponent("e3"))
    scene.add_component(entity3, TransformComponent(glm.vec3(-2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity3, LinkComponent(entity1))
    scene.add_component(entity3, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(entity3, MaterialComponent('M_Blue_Textured'))
    scene.add_component(entity3, MovementComponent())

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(OpenGLRenderingSystem([OpenGLRenderComponent, MaterialComponent, TransformComponent]))
    scene.register_system(MovementSystem([MovementComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()