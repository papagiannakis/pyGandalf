from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
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

from pyGandalf.utilities.logger import logger

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH

import numpy as np
import glm
import glfw

"""
Showcase of an ecss cube consisting of an empty parent entity and six other entities for each face of the cube.
A custom component is added to the root entity to rotate around the whole cube.
"""

class DemoComponent(Component):
    def __init__(self, axis, speed, rotate_around, main_camera) -> None:
        self.axis = axis
        self.speed = speed
        self.rotate_around = rotate_around
        self.main_camera = main_camera

class DemoSystem(System):
    """
    The system responsible showcasing new features.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        demo, transform, info = components

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        demo, transform, info = components

        if demo.rotate_around == True:
            if demo.axis[0] == 1:
                transform.rotation[0] += demo.speed * ts

            if demo.axis[1] == 1:
                transform.rotation[1] += demo.speed * ts

            if demo.axis[2] == 1:
                transform.rotation[2] += demo.speed * ts
        else:
            demo.main_camera = False

            if glfw.get_key(Application().get_window().get_handle(), glfw.KEY_C) == glfw.PRESS:
                if info.tag == 'camera':
                    demo.main_camera = True
            elif glfw.get_key(Application().get_window().get_handle(), glfw.KEY_V) == glfw.PRESS:
                if info.tag == 'camera_alt':
                    demo.main_camera = True

            SceneManager().get_active_scene().get_component(entity, CameraComponent).primary = demo.main_camera
        

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    camera_alt = scene.enroll_entity()
    cube = scene.enroll_entity()
    cube_face_front = scene.enroll_entity()
    cube_face_back = scene.enroll_entity()
    cube_face_right = scene.enroll_entity()
    cube_face_left = scene.enroll_entity()
    cube_face_top = scene.enroll_entity()
    cube_face_bottom = scene.enroll_entity()

    Application().create(OpenGLWindow('ECSS Cube', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')

    # Build shaders 
    OpenGLShaderLib().build('unlit_simple', SHADERS_PATH/'unlit_simple_vertex.glsl', SHADERS_PATH/'unlit_simple_fragment.glsl')
    OpenGLShaderLib().build('unlit_textured', SHADERS_PATH/'unlit_textured_vertex.glsl', SHADERS_PATH/'unlit_textured_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('unlit_simple', []))
    OpenGLMaterialLib().build('M_Red_Textured', MaterialData('unlit_textured', ['uoc_logo']))
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

    # Register components to cube
    scene.add_component(cube, InfoComponent("cube"))
    scene.add_component(cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(45, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube, LinkComponent(root))
    scene.add_component(cube, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to cube_face_front
    scene.add_component(cube_face_front, InfoComponent("cube_face_front"))
    scene.add_component(cube_face_front, TransformComponent(glm.vec3(0.0, 0.0, 0.5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_front, LinkComponent(cube))
    scene.add_component(cube_face_front, StaticMeshComponent('f', [vertices, texture_coords], None))
    scene.add_component(cube_face_front, MaterialComponent('M_Red_Textured')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_back
    scene.add_component(cube_face_back, InfoComponent("cube_face_back"))
    scene.add_component(cube_face_back, TransformComponent(glm.vec3(0.0, 0.0, -0.5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_back, LinkComponent(cube))
    scene.add_component(cube_face_back, StaticMeshComponent('b', [vertices, texture_coords], None))
    scene.add_component(cube_face_back, MaterialComponent('M_Red_Textured')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_right
    scene.add_component(cube_face_right, InfoComponent("cube_face_right"))
    scene.add_component(cube_face_right, TransformComponent(glm.vec3(0.5, 0.0, 0.0), glm.vec3(0, 90, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_right, LinkComponent(cube))
    scene.add_component(cube_face_right, StaticMeshComponent('r', [vertices, texture_coords], None))
    scene.add_component(cube_face_right, MaterialComponent('M_Blue_Textured')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_left
    scene.add_component(cube_face_left, InfoComponent("cube_face_left"))
    scene.add_component(cube_face_left, TransformComponent(glm.vec3(-0.5, 0.0, 0.0), glm.vec3(0, 90, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_left, LinkComponent(cube))
    scene.add_component(cube_face_left, StaticMeshComponent('l', [vertices, texture_coords], None))
    scene.add_component(cube_face_left, MaterialComponent('M_Blue_Textured')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_top
    scene.add_component(cube_face_top, InfoComponent("cube_face_top"))
    scene.add_component(cube_face_top, TransformComponent(glm.vec3(0.0, 0.5, 0.0), glm.vec3(90, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_top, LinkComponent(cube))
    scene.add_component(cube_face_top, StaticMeshComponent('t', [vertices], None))
    scene.add_component(cube_face_top, MaterialComponent('M_Yellow_Simple')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to cube_face_bottom
    scene.add_component(cube_face_bottom, InfoComponent("cube_face_bottom"))
    scene.add_component(cube_face_bottom, TransformComponent(glm.vec3(0.0, -0.5, 0.0), glm.vec3(90, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_bottom, LinkComponent(cube))
    scene.add_component(cube_face_bottom, StaticMeshComponent('b', [vertices], None))
    scene.add_component(cube_face_bottom, MaterialComponent('M_Yellow_Simple')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, DemoComponent((1, 1, 0), 25, False, True))

    # Register components to camera_alt
    scene.add_component(camera_alt, InfoComponent("camera_alt"))
    scene.add_component(camera_alt, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera_alt, LinkComponent(root))
    scene.add_component(camera_alt, CameraComponent(45, 1.778, 0.1, 1000, 1.8, CameraComponent.Type.ORTHOGRAPHIC, False))
    scene.add_component(camera_alt, DemoComponent((1, 1, 0), 25, False, True))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(DemoSystem([DemoComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()