from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureDescriptor
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib

from pyGandalf.utilities.logger import logger

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH

import numpy as np
import glm

"""
Showcase of an ecss textured cube consisting of an empty parent entity and six other entities for each face of the cube.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('ECSS Textured Cube', 1280, 720, True), OpenGLRenderer)

    # Create a new scene
    scene = Scene('ECSS Textured Cube')

    # Enroll entities to registry
    root = scene.enroll_entity()
    cube = scene.enroll_entity()
    cube_face_front = scene.enroll_entity()
    cube_face_back = scene.enroll_entity()
    cube_face_right = scene.enroll_entity()
    cube_face_left = scene.enroll_entity()
    cube_face_top = scene.enroll_entity()
    cube_face_bottom = scene.enroll_entity()
    camera = scene.enroll_entity()

    # Build textures
    OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png', TextureDescriptor(flip=True))
    OpenGLTextureLib().build('dark_wood', TEXTURES_PATH/'dark_wood_texture.jpg')

    # Build shaders 
    OpenGLShaderLib().build('unlit', SHADERS_PATH/'unlit_simple_vertex.glsl', SHADERS_PATH/'unlit_simple_fragment.glsl')
    OpenGLShaderLib().build('unlit_textured', SHADERS_PATH/'unlit_textured_vertex.glsl', SHADERS_PATH/'unlit_textured_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Unlit', MaterialData('unlit', []))
    OpenGLMaterialLib().build('M_Blue_Textured', MaterialData('unlit_textured', ['uoc_logo']))
    OpenGLMaterialLib().build('M_Yellow_Textured', MaterialData('unlit_textured', ['dark_wood']))

    # Vertices of the square
    vertices = np.array([
        [-0.5, -0.5, 0.0], # 0 - Bottom left
        [ 0.5, -0.5, 0.0], # 1 - Bottom right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [-0.5,  0.5, 0.0], # 3 - Top left
        [-0.5, -0.5, 0.0]  # 0 - Bottom left
    ], dtype=np.float32)

    # Texture coordinates of the square
    texture_coords = np.array([
        [0.0, 1.0], # 0
        [1.0, 1.0], # 1
        [1.0, 0.0], # 2
        [1.0, 0.0], # 2
        [0.0, 0.0], # 3
        [0.0, 1.0]  # 0
    ], dtype=np.float32)

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent("root"))
    scene.add_component(root, LinkComponent(None))

    # Register components to cube
    scene.add_component(cube, InfoComponent("cube"))
    scene.add_component(cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(25, 45, 15), glm.vec3(1, 1, 1)))
    scene.add_component(cube, LinkComponent(root))

    # Register components to cube_face_front
    scene.add_component(cube_face_front, InfoComponent("cube_face_front"))
    scene.add_component(cube_face_front, TransformComponent(glm.vec3(0.0, 0.0, 0.5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_front, LinkComponent(cube))
    scene.add_component(cube_face_front, StaticMeshComponent('cube_face_front', [vertices]))
    scene.add_component(cube_face_front, MaterialComponent('M_Unlit')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_back
    scene.add_component(cube_face_back, InfoComponent("cube_face_back"))
    scene.add_component(cube_face_back, TransformComponent(glm.vec3(0.0, 0.0, -0.5), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_back, LinkComponent(cube))
    scene.add_component(cube_face_back, StaticMeshComponent('cube_face_back', [vertices]))
    scene.add_component(cube_face_back, MaterialComponent('M_Unlit')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_right
    scene.add_component(cube_face_right, InfoComponent("cube_face_right"))
    scene.add_component(cube_face_right, TransformComponent(glm.vec3(0.5, 0.0, 0.0), glm.vec3(0, 90, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_right, LinkComponent(cube))
    scene.add_component(cube_face_right, StaticMeshComponent('cube_face_right', [vertices, texture_coords]))
    scene.add_component(cube_face_right, MaterialComponent('M_Blue_Textured')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_left
    scene.add_component(cube_face_left, InfoComponent("cube_face_left"))
    scene.add_component(cube_face_left, TransformComponent(glm.vec3(-0.5, 0.0, 0.0), glm.vec3(0, 90, 180), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_left, LinkComponent(cube))
    scene.add_component(cube_face_left, StaticMeshComponent('cube_face_left', [vertices, texture_coords]))
    scene.add_component(cube_face_left, MaterialComponent('M_Blue_Textured')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_top
    scene.add_component(cube_face_top, InfoComponent("cube_face_top"))
    scene.add_component(cube_face_top, TransformComponent(glm.vec3(0.0, 0.5, 0.0), glm.vec3(90, 0, 180), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_top, LinkComponent(cube))
    scene.add_component(cube_face_top, StaticMeshComponent('cube_face_top', [vertices, texture_coords]))
    scene.add_component(cube_face_top, MaterialComponent('M_Yellow_Textured')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to cube_face_bottom
    scene.add_component(cube_face_bottom, InfoComponent("cube_face_bottom"))
    scene.add_component(cube_face_bottom, TransformComponent(glm.vec3(0.0, -0.5, 0.0), glm.vec3(90, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_bottom, LinkComponent(cube))
    scene.add_component(cube_face_bottom, StaticMeshComponent('cube_face_bottom', [vertices, texture_coords]))
    scene.add_component(cube_face_bottom, MaterialComponent('M_Yellow_Textured')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()