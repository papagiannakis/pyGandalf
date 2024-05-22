from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureDescriptor, TextureDimension
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np

"""
Showcase of obj model loading with basic Blinn-Phong lighting.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('Cube Mapping - Skybox', 1280, 720, True), OpenGLRenderer)

    # Create a new scene
    scene = Scene('Cube Mapping - Skybox')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    bunny = scene.enroll_entity()
    light = scene.enroll_entity()
    skybox = scene.enroll_entity()

    # Array that holds all the skybox textures
    skybox_textures = [
        TEXTURES_PATH / 'skybox' / 'right.jpg',
        TEXTURES_PATH / 'skybox' / 'left.jpg',
        TEXTURES_PATH / 'skybox' / 'top.jpg',
        TEXTURES_PATH / 'skybox' / 'bottom.jpg',
        TEXTURES_PATH / 'skybox' / 'front.jpg',
        TEXTURES_PATH / 'skybox' / 'back.jpg'
    ]

    # Vertices for the cube
    vertices = np.array([
        [-1.0, -1.0, -1.0], [-1.0, -1.0,  1.0], [-1.0,  1.0,  1.0], [ 1.0,  1.0, -1.0],
        [-1.0, -1.0, -1.0], [-1.0,  1.0, -1.0], [1.0, -1.0,  1.0], [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0], [ 1.0,  1.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0],

        [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0,  1.0, -1.0], [ 1.0, -1.0,  1.0],
        [-1.0, -1.0,  1.0], [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0], [1.0,  1.0,  1.0], [1.0, -1.0, -1.0], [1.0,  1.0, -1.0],

        [1.0, -1.0, -1.0], [1.0,  1.0,  1.0], [1.0, -1.0,  1.0], [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0], [-1.0,  1.0, -1.0], [1.0,  1.0,  1.0], [-1.0,  1.0, -1.0],
        [-1.0,  1.0,  1.0], [1.0,  1.0,  1.0], [-1.0,  1.0,  1.0], [1.0, -1.0,  1.0]
    ], dtype=np.float32)

    # Build textures
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLTextureLib().build('cube_map', skybox_textures, None, TextureDescriptor(flip=True, dimention=TextureDimension.CUBE))

    # Build shaders
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLShaderLib().build('skybox', SHADERS_PATH/'skybox_vertex.glsl', SHADERS_PATH/'skybox_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Bunny', MaterialData('default_mesh', ['white_texture']))
    OpenGLMaterialLib().build('M_Skybox', MaterialData('skybox', ['cube_map']))

    # Load models
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to skybox
    scene.add_component(skybox, InfoComponent("skybox"))
    scene.add_component(skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1000, 1000, 1000)))
    scene.add_component(skybox, LinkComponent(None))
    scene.add_component(skybox, StaticMeshComponent('skybox', [vertices]))
    scene.add_component(skybox, MaterialComponent('M_Skybox'))

    # Register components to bunny
    scene.add_component(bunny, InfoComponent("bunny"))
    scene.add_component(bunny, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 10, 0), glm.vec3(1, 1, 1)))
    scene.add_component(bunny, LinkComponent(root))
    scene.add_component(bunny, StaticMeshComponent('bunny_mesh'))
    scene.add_component(bunny, MaterialComponent('M_Bunny'))

    # Change the material properties of the bunny
    material: MaterialComponent = scene.get_component(bunny, MaterialComponent)
    material.color = glm.vec3(0.8, 0.5, 0.3)
    material.glossiness = 1.0

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-0.25, 2, 4), glm.vec3(-15, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 2000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()