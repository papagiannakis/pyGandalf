from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.core.events import EventType
from pyGandalf.core.event_manager import EventManager

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

import glfw
import numpy as np

"""
Showcase of multiple scenes support.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('Cube Mapping - Skybox', 1280, 720, True), OpenGLRenderer)

    # Array that holds all the sea skybox textures
    sea_skybox_textures = [
        TEXTURES_PATH / 'skybox' / 'sea' / 'right.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'left.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'top.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'bottom.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'front.jpg',
        TEXTURES_PATH / 'skybox' / 'sea' / 'back.jpg'
    ]

    # Array that holds all the cloudy skybox textures
    cloudy_skybox_textures = [
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'right.jpg',
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'left.jpg',
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'top.jpg',
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'bottom.jpg',
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'front.jpg',
        TEXTURES_PATH / 'skybox' / 'cloudy' / 'back.jpg'
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

    # Vertex data for the plane
    plane_vertices = np.array([
        [-0.5, -0.5, 0.0], [ 0.5, -0.5, 0.0], [ 0.5,  0.5, 0.0],
        [ 0.5,  0.5, 0.0], [-0.5,  0.5, 0.0], [-0.5, -0.5, 0.0]
    ], dtype=np.float32)

    plane_texture_coords = np.array([
        [0.0, 1.0], [1.0, 1.0], [1.0, 0.0],
        [1.0, 0.0], [0.0, 0.0], [0.0, 1.0]
    ], dtype=np.float32)

    plane_normals = np.array([
        [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]
    ], dtype=np.float32)

    # Build textures
    OpenGLTextureLib().build('white_texture', None, 0xffffffff.to_bytes(4, byteorder='big'), TextureDescriptor(width=1, height=1))
    OpenGLTextureLib().build('dark_wood_texture', TEXTURES_PATH/'dark_wood_texture.jpg')
    OpenGLTextureLib().build('marble_texture', TEXTURES_PATH/'marble_diffuse.png')
    OpenGLTextureLib().build('sea_cube_map', sea_skybox_textures, None, TextureDescriptor(flip=True, dimention=TextureDimension.CUBE))
    OpenGLTextureLib().build('cloudy_cube_map', cloudy_skybox_textures, None, TextureDescriptor(flip=True, dimention=TextureDimension.CUBE))

    # Build shaders
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLShaderLib().build('skybox', SHADERS_PATH/'skybox_vertex.glsl', SHADERS_PATH/'skybox_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Bunny', MaterialData('default_mesh', ['white_texture']))
    OpenGLMaterialLib().build('M_WoodFloor', MaterialData('default_mesh', ['dark_wood_texture']))
    OpenGLMaterialLib().build('M_MarbleFloor', MaterialData('default_mesh', ['marble_texture']))
    OpenGLMaterialLib().build('M_SeaSkybox', MaterialData('skybox', ['sea_cube_map']))
    OpenGLMaterialLib().build('M_CloudySkybox', MaterialData('skybox', ['cloudy_cube_map']))

    # Load models
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

    # Create a new scene
    sea_scene = Scene('Cube Mapping - Sea Skybox')

    # Create Enroll entities to registry
    sea_root = sea_scene.enroll_entity()
    sea_camera = sea_scene.enroll_entity()
    sea_bunny = sea_scene.enroll_entity()
    sea_floor = sea_scene.enroll_entity()
    sea_light = sea_scene.enroll_entity()
    sea_skybox = sea_scene.enroll_entity()

    # Register components to root
    sea_scene.add_component(sea_root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    sea_scene.add_component(sea_root, InfoComponent('root'))
    sea_scene.add_component(sea_root, LinkComponent(None))

    # Register components to skybox
    sea_scene.add_component(sea_skybox, InfoComponent("sea_skybox"))
    sea_scene.add_component(sea_skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    sea_scene.add_component(sea_skybox, LinkComponent(None))
    sea_scene.add_component(sea_skybox, StaticMeshComponent('skybox', [vertices]))
    sea_scene.add_component(sea_skybox, MaterialComponent('M_SeaSkybox'))

    # Register components to floor
    sea_scene.add_component(sea_floor, InfoComponent("sea_floor"))
    sea_scene.add_component(sea_floor, TransformComponent(glm.vec3(0, -0.5, 0), glm.vec3(270, 0, 0), glm.vec3(20, 20, 20)))
    sea_scene.add_component(sea_floor, LinkComponent(sea_root))
    sea_scene.add_component(sea_floor, StaticMeshComponent('floor_mesh', [plane_vertices, plane_normals, plane_texture_coords]))
    sea_scene.add_component(sea_floor, MaterialComponent('M_WoodFloor')).glossiness = 1.0

    # Register components to bunny
    sea_scene.add_component(sea_bunny, InfoComponent("sea_bunny"))
    sea_scene.add_component(sea_bunny, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 10, 0), glm.vec3(1, 1, 1)))
    sea_scene.add_component(sea_bunny, LinkComponent(sea_root))
    sea_scene.add_component(sea_bunny, StaticMeshComponent('bunny_mesh'))
    sea_scene.add_component(sea_bunny, MaterialComponent('M_Bunny'))

    # Change the material properties of the bunny
    material: MaterialComponent = sea_scene.get_component(sea_bunny, MaterialComponent)
    material.color = glm.vec3(0.8, 0.5, 0.3)
    material.glossiness = 1.0

    # Register components to light
    sea_scene.add_component(sea_light, InfoComponent("sea_light"))
    sea_scene.add_component(sea_light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    sea_scene.add_component(sea_light, LinkComponent(sea_root))
    sea_scene.add_component(sea_light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    sea_scene.add_component(sea_camera, InfoComponent("sea_camera"))
    sea_scene.add_component(sea_camera, TransformComponent(glm.vec3(-0.25, 2, 4), glm.vec3(-15, 0, 0), glm.vec3(1, 1, 1)))
    sea_scene.add_component(sea_camera, LinkComponent(sea_root))
    sea_scene.add_component(sea_camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    sea_scene.add_component(sea_camera, CameraControllerComponent())

    # Create Register systems
    sea_scene.register_system(TransformSystem([TransformComponent]))
    sea_scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    sea_scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    sea_scene.register_system(LightSystem([LightComponent, TransformComponent]))
    sea_scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    sea_scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Create a new scene
    cloudy_scene = Scene('Cube Mapping - Cloudy Skybox')

    # Create Enroll entities to registry
    cloudy_root = cloudy_scene.enroll_entity()
    cloudy_camera = cloudy_scene.enroll_entity()
    cloudy_bunny = cloudy_scene.enroll_entity()
    cloudy_floor = cloudy_scene.enroll_entity()
    cloudy_light = cloudy_scene.enroll_entity()
    cloudy_skybox = cloudy_scene.enroll_entity()

    # Register components to cloudy_root
    cloudy_scene.add_component(cloudy_root, InfoComponent('cloudy_root'))
    cloudy_scene.add_component(cloudy_root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    cloudy_scene.add_component(cloudy_root, LinkComponent(None))

    # Register components to cloudy_skybox
    cloudy_scene.add_component(cloudy_skybox, InfoComponent("cloudy_skybox"))
    cloudy_scene.add_component(cloudy_skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    cloudy_scene.add_component(cloudy_skybox, LinkComponent(None))
    cloudy_scene.add_component(cloudy_skybox, StaticMeshComponent('skybox', [vertices]))
    cloudy_scene.add_component(cloudy_skybox, MaterialComponent('M_CloudySkybox'))

    # Register components to cloudy_floor
    cloudy_scene.add_component(cloudy_floor, InfoComponent("cloudy_floor"))
    cloudy_scene.add_component(cloudy_floor, TransformComponent(glm.vec3(0, 18, 0), glm.vec3(270, 0, 0), glm.vec3(1000, 1000, 1000)))
    cloudy_scene.add_component(cloudy_floor, LinkComponent(cloudy_root))
    cloudy_scene.add_component(cloudy_floor, StaticMeshComponent('floor_mesh', [plane_vertices, plane_normals, plane_texture_coords]))
    cloudy_scene.add_component(cloudy_floor, MaterialComponent('M_MarbleFloor')).glossiness = 0.5

    # Register components to cloudy_bunny
    cloudy_scene.add_component(cloudy_bunny, InfoComponent("cloudy_bunny"))
    cloudy_scene.add_component(cloudy_bunny, TransformComponent(glm.vec3(0, 20, 0), glm.vec3(0, 10, 0), glm.vec3(1, 1, 1)))
    cloudy_scene.add_component(cloudy_bunny, LinkComponent(cloudy_root))
    cloudy_scene.add_component(cloudy_bunny, StaticMeshComponent('bunny_mesh'))
    cloudy_scene.add_component(cloudy_bunny, MaterialComponent('M_Bunny'))

    # Change the material properties of the bunny
    material: MaterialComponent = cloudy_scene.get_component(cloudy_bunny, MaterialComponent)
    material.color = glm.vec3(0.05, 0.9, 0.9)
    material.glossiness = 0.5

    # Register components to cloudy_light
    cloudy_scene.add_component(cloudy_light, InfoComponent("cloudy_light"))
    cloudy_scene.add_component(cloudy_light, TransformComponent(glm.vec3(0, 25, -1), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    cloudy_scene.add_component(cloudy_light, LinkComponent(cloudy_root))
    cloudy_scene.add_component(cloudy_light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to cloudy_camera
    cloudy_scene.add_component(cloudy_camera, InfoComponent("cloudy_camera"))
    cloudy_scene.add_component(cloudy_camera, TransformComponent(glm.vec3(-0.25, 22, 4), glm.vec3(-15, 0, 0), glm.vec3(1, 1, 1)))
    cloudy_scene.add_component(cloudy_camera, LinkComponent(cloudy_root))
    cloudy_scene.add_component(cloudy_camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    cloudy_scene.add_component(cloudy_camera, CameraControllerComponent())

    # Register the systems
    cloudy_scene.register_system(TransformSystem([TransformComponent]))
    cloudy_scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    cloudy_scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    cloudy_scene.register_system(LightSystem([LightComponent, TransformComponent]))
    cloudy_scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    cloudy_scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scenes to manager
    SceneManager().add_scene(sea_scene)
    SceneManager().add_scene(cloudy_scene)

    # Attach events
    def on_scene_change(s1, s2):
        print(f'Changed from scene: \'{s1.name}\' to scene: \'{s2.name}\'')

    def on_key_callback(key, modifiers):
        if key == glfw.KEY_SPACE:
            scene = SceneManager().get_active_scene()
            if scene == sea_scene:
                SceneManager().change_scene(cloudy_scene)
            else:
                SceneManager().change_scene(sea_scene)

    EventManager().attach_callback(EventType.SCENE_CHANGE, on_scene_change, True)
    EventManager().attach_callback(EventType.KEY_PRESS, on_key_callback, True)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()