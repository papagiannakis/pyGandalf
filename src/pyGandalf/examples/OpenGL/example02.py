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
    cube_mesh = scene.enroll_entity()
    quad = scene.enroll_entity()

    vertex_shader_code = OpenGLShaderLib().load_from_file(SHADERS_PATH/'vertex_shader_code.glsl')
    fragment_shader_code_yellow = OpenGLShaderLib().load_from_file(SHADERS_PATH/'fragment_shader_code_yellow.glsl')

    vertices = np.array([
        [-0.5, -0.5, 0.0], #0
        [ 0.5, -0.5, 0.0], #1
        [ 0.5,  0.5, 0.0], #2
        [ 0.5,  0.5, 0.0], #2
        [-0.5,  0.5, 0.0], #3
        [-0.5, -0.5, 0.0]  #0
    ], dtype=np.float32)

    Application().create(OpenGLWindow('ECSS Cube', 1280, 720, True), OpenGLRenderer)

    # Build textures
    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])

    # Build shaders 
    OpenGLShaderLib().build('default_colored_yellow', vertex_shader_code, fragment_shader_code_yellow)
    
    # Build Materials
    OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))

    # Load models
    OpenGLMeshLib().build('monkeh_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('cornell_box_mesh', MODELS_PATH/'cornell_box.obj')
    OpenGLMeshLib().build('cube_mesh', MODELS_PATH/'cube.obj')

    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, LinkComponent(None))

    # Register components to monkeh
    scene.add_component(monkeh, InfoComponent("monkeh"))
    scene.add_component(monkeh, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(monkeh, LinkComponent(root))
    scene.add_component(monkeh, StaticMeshComponent('monkeh_mesh'))
    scene.add_component(monkeh, MaterialComponent('M_Yellow_Simple'))
    scene.add_component(monkeh, DemoComponent((0, 1, 0), 25, True, False))

    # Register components to cube_mesh
    scene.add_component(cube_mesh, InfoComponent("cube_mesh"))
    scene.add_component(cube_mesh, TransformComponent(glm.vec3(3, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_mesh, LinkComponent(root))
    scene.add_component(cube_mesh, StaticMeshComponent('cube_mesh'))
    scene.add_component(cube_mesh, MaterialComponent('M_Yellow_Simple'))

    # Register components to quad
    scene.add_component(quad, InfoComponent("quad"))
    scene.add_component(quad, TransformComponent(glm.vec3(-3, -2, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(quad, LinkComponent(root))
    scene.add_component(quad, StaticMeshComponent('quad', [vertices]))
    scene.add_component(quad, MaterialComponent('M_Yellow_Simple'))

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