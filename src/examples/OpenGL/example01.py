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

import utilities.math as utils

import numpy as np

"""
Showcase of an ecss cube consisting of an empty parent entity and six other entities for each face of the cube.
A custom component is added to the root entity to rotate around the whole cube.
"""

class RotateAroundComponent:
    def __init__(self, axis, speed) -> None:
        self.axis = axis
        self.speed = speed

class RotateAroundSystem(System):
    """
    The system responsible for rotation around.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        rotate_around, transform = components

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        rotate_around, transform = components

        if rotate_around.axis[0] == 1:
            transform.rotation[0] += rotate_around.speed * ts

        if rotate_around.axis[1] == 1:
            transform.rotation[1] += rotate_around.speed * ts

        if rotate_around.axis[2] == 1:
            transform.rotation[2] += rotate_around.speed * ts

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    cube = scene.enroll_entity()
    cube_face_front = scene.enroll_entity()
    cube_face_back = scene.enroll_entity()
    cube_face_right = scene.enroll_entity()
    cube_face_left = scene.enroll_entity()
    cube_face_top = scene.enroll_entity()
    cube_face_bottom = scene.enroll_entity()

    vertex_shader_code = OpenGLShaderLib().load_from_file('../shaders/vertex_shader_code.glsl')
    fragment_shader_code_yellow = OpenGLShaderLib().load_from_file('../shaders/fragment_shader_code_yellow.glsl')
    textured_vertex_shader_code = OpenGLShaderLib().load_from_file('../shaders/textured_vertex_shader_code.glsl')
    textured_fragment_shader_code_blue = OpenGLShaderLib().load_from_file('../shaders/textured_fragment_shader_code_blue.glsl')
    textured_fragment_shader_code_red = OpenGLShaderLib().load_from_file('../shaders/textured_fragment_shader_code_red.glsl')

    Application().create(OpenGLWindow('ECSS Cube', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('uoc_logo', '../textures/uoc_logo.png')

    # Build shaders 
    OpenGLShaderLib().build('default_colored_yellow', vertex_shader_code, fragment_shader_code_yellow)
    OpenGLShaderLib().build('textured_colored_blue', textured_vertex_shader_code, textured_fragment_shader_code_blue)
    OpenGLShaderLib().build('textured_colored_red', textured_vertex_shader_code, textured_fragment_shader_code_red)
    
    # Build Materials
    OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))
    OpenGLMaterialLib().build('M_Red_Textured', MaterialData('textured_colored_red', ['uoc_logo']))
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

    # Register components to cube
    scene.add_component(cube, InfoComponent("cube"))
    scene.add_component(cube, TransformComponent(utils.vec(0, 0, 0), utils.vec(15, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube, LinkComponent(None))
    scene.add_component(cube, RotateAroundComponent((1, 1, 0), 15))

    # Register components to cube_face_front
    scene.add_component(cube_face_front, InfoComponent("cube_face_front"))
    scene.add_component(cube_face_front, TransformComponent(utils.vec(0, 0, 0.5), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_front, LinkComponent(cube))
    scene.add_component(cube_face_front, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(cube_face_front, MaterialComponent('M_Red_Textured'))

    # Register components to cube_face_back
    scene.add_component(cube_face_back, InfoComponent("cube_face_back"))
    scene.add_component(cube_face_back, TransformComponent(utils.vec(0, 0, -0.5), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_back, LinkComponent(cube))
    scene.add_component(cube_face_back, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(cube_face_back, MaterialComponent('M_Red_Textured'))

    # Register components to cube_face_right
    scene.add_component(cube_face_right, InfoComponent("cube_face_right"))
    scene.add_component(cube_face_right, TransformComponent(utils.vec(0.0, 0, 0.5), utils.vec(0, 90, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_right, LinkComponent(cube))
    scene.add_component(cube_face_right, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(cube_face_right, MaterialComponent('M_Blue_Textured'))

    # Register components to cube_face_left
    scene.add_component(cube_face_left, InfoComponent("cube_face_left"))
    scene.add_component(cube_face_left, TransformComponent(utils.vec(-0.0, 0, -0.5), utils.vec(0, 90, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_left, LinkComponent(cube))
    scene.add_component(cube_face_left, OpenGLRenderComponent([vertices, texture_coords], None))
    scene.add_component(cube_face_left, MaterialComponent('M_Blue_Textured'))

    # Register components to cube_face_top
    scene.add_component(cube_face_top, InfoComponent("cube_face_top"))
    scene.add_component(cube_face_top, TransformComponent(utils.vec(0, 0, 0.5), utils.vec(90, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_top, LinkComponent(cube))
    scene.add_component(cube_face_top, OpenGLRenderComponent([vertices], None))
    scene.add_component(cube_face_top, MaterialComponent('M_Yellow_Simple'))

    # Register components to cube_face_bottom
    scene.add_component(cube_face_bottom, InfoComponent("cube_face_top"))
    scene.add_component(cube_face_bottom, TransformComponent(utils.vec(0, 0, -0.5), utils.vec(90, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(cube_face_bottom, LinkComponent(cube))
    scene.add_component(cube_face_bottom, OpenGLRenderComponent([vertices], None))
    scene.add_component(cube_face_bottom, MaterialComponent('M_Yellow_Simple'))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(OpenGLRenderingSystem([OpenGLRenderComponent, MaterialComponent, TransformComponent]))
    scene.register_system(RotateAroundSystem([RotateAroundComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()