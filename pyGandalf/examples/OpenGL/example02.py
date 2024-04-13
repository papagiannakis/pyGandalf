from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.systems.system import System
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np
import glm

"""
Showcase of obj model loading with textures and basic Blinn-Phong lighting.
A custom component is added to the entities to rotate around.
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

# Example Usage
def main():
    logger.setLevel(logger.DEBUG)

    scene = Scene()

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    monkeh = scene.enroll_entity()
    pistol = scene.enroll_entity()
    rabbit = scene.enroll_entity()
    floor = scene.enroll_entity()
    light = scene.enroll_entity()

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

    Application().create(OpenGLWindow('ECSS Cube', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLTextureLib().build('rabbit_albedo', TEXTURES_PATH/'fg_spkRabbit_albedo.jpg')
    OpenGLTextureLib().build('flintlockPistol_albedo', TEXTURES_PATH/'fa_flintlockPistol_albedo.jpg')
    OpenGLTextureLib().build('dark_wood_texture', TEXTURES_PATH/'dark_wood_texture.jpg')

    # Build shaders
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Rabbit', MaterialData('default_mesh', ['rabbit_albedo']))
    OpenGLMaterialLib().build('M_Monkeh', MaterialData('default_mesh', ['white_texture']))
    OpenGLMaterialLib().build('M_Floor', MaterialData('default_mesh', ['dark_wood_texture']))
    OpenGLMaterialLib().build('M_Pistol', MaterialData('default_mesh', ['flintlockPistol_albedo']))

    # Load models
    OpenGLMeshLib().build('monkeh_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('rabbit_mesh', MODELS_PATH/'fg_spkRabbit.obj')
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')

    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, LinkComponent(None))

    # Register components to monkeh
    scene.add_component(monkeh, InfoComponent("monkeh"))
    scene.add_component(monkeh, TransformComponent(glm.vec3(5.5, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(monkeh, LinkComponent(root))
    scene.add_component(monkeh, StaticMeshComponent('monkeh_mesh'))
    scene.add_component(monkeh, MaterialComponent('M_Monkeh'))
    scene.add_component(monkeh, DemoComponent((1, 0, 0), 25, True, False))

    # Register components to pistol
    scene.add_component(pistol, InfoComponent("pistol"))
    scene.add_component(pistol, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(pistol, LinkComponent(root))
    scene.add_component(pistol, StaticMeshComponent('pistol_mesh'))
    scene.add_component(pistol, MaterialComponent('M_Pistol'))
    scene.add_component(pistol, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to rabbit
    scene.add_component(rabbit, InfoComponent("rabbit"))
    scene.add_component(rabbit, TransformComponent(glm.vec3(-5.5, 0.0, 0), glm.vec3(0, 0, 0), glm.vec3(20, 20, 20)))
    scene.add_component(rabbit, LinkComponent(root))
    scene.add_component(rabbit, StaticMeshComponent('rabbit_mesh'))
    scene.add_component(rabbit, MaterialComponent('M_Rabbit'))
    scene.add_component(rabbit, DemoComponent((0, 1, 0), 25, True, False))

    # Register components to floor
    scene.add_component(floor, InfoComponent("floor"))
    scene.add_component(floor, TransformComponent(glm.vec3(0, -2, 0), glm.vec3(270, 0, 0), glm.vec3(20, 20, 20)))
    scene.add_component(floor, LinkComponent(root))
    scene.add_component(floor, StaticMeshComponent('floor_mesh', [vertices, normals, texture_coords]))
    scene.add_component(floor, MaterialComponent('M_Floor'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(-3, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 5, 10), glm.vec3(-25, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 5.0, CameraComponent.Type.PERSPECTIVE))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(DemoSystem([DemoComponent, TransformComponent, InfoComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()