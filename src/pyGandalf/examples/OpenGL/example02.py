from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
from pyGandalf.systems.system import System
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.opengl_static_mesh_rendering_system import OpenGLStaticMeshRenderingSystem
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.scene.entity import Entity
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager

from pyGandalf.scene.components import InfoComponent, TransformComponent, LinkComponent, MaterialComponent, CameraComponent, StaticMeshComponent

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.logger import logger

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH

import numpy as np
import glm
import glfw

"""
Showcase of an ecss cube consisting of an empty parent entity and six other entities for each face of the cube.
A custom component is added to the root entity to rotate around the whole cube.
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
    lion = scene.enroll_entity()

    blinn_phong_mesh_vertex = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_vertex.glsl')
    blinn_phong_mesh_fragment = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_fragment.glsl')

    vertices = np.array([
        [-0.5, -0.5, 0.0], #0
        [ 0.5, -0.5, 0.0], #1
        [ 0.5,  0.5, 0.0], #2
        [ 0.5,  0.5, 0.0], #2
        [-0.5,  0.5, 0.0], #3
        [-0.5, -0.5, 0.0]  #0
    ], dtype=np.float32)

    Application().create(OpenGLWindow('ECSS Cube', 1280, 720, False), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLTextureLib().build('lion_albedo', TEXTURES_PATH/'fg_spkRabbit_albedo.jpg')
    OpenGLTextureLib().build('flintlockPistol_albedo', TEXTURES_PATH/'fa_flintlockPistol_albedo.jpg')

    # Build shaders
    OpenGLShaderLib().build('default_mesh', blinn_phong_mesh_vertex, blinn_phong_mesh_fragment)
    
    # Build Materials
    OpenGLMaterialLib().build('M_Lion', MaterialData('default_mesh', ['lion_albedo']))
    OpenGLMaterialLib().build('M_Monkeh', MaterialData('default_mesh', ['white_texture']))
    OpenGLMaterialLib().build('M_Pistol', MaterialData('default_mesh', ['flintlockPistol_albedo']))

    # Load models
    OpenGLMeshLib().build('monkeh_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('lion_mesh', MODELS_PATH/'fg_spkRabbit.obj')
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')

    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, LinkComponent(None))

    # Register components to monkeh
    scene.add_component(monkeh, InfoComponent("monkeh"))
    scene.add_component(monkeh, TransformComponent(glm.vec3(5.5, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(monkeh, LinkComponent(root))
    scene.add_component(monkeh, StaticMeshComponent('monkeh_mesh'))
    scene.add_component(monkeh, MaterialComponent('M_Monkeh'))
    scene.add_component(monkeh, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to pistol
    scene.add_component(pistol, InfoComponent("pistol"))
    scene.add_component(pistol, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(pistol, LinkComponent(root))
    scene.add_component(pistol, StaticMeshComponent('pistol_mesh'))
    scene.add_component(pistol, MaterialComponent('M_Pistol'))
    scene.add_component(pistol, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to lion
    scene.add_component(lion, InfoComponent("lion"))
    scene.add_component(lion, TransformComponent(glm.vec3(-5.5, 0, 0), glm.vec3(0, 0, 0), glm.vec3(20, 20, 20)))
    scene.add_component(lion, LinkComponent(root))
    scene.add_component(lion, StaticMeshComponent('lion_mesh'))
    scene.add_component(lion, MaterialComponent('M_Lion'))
    scene.add_component(lion, DemoComponent((1, 1, 0), 25, True, False))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 10), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(None))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 10000, 5.0, CameraComponent.Type.PERSPECTIVE))

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