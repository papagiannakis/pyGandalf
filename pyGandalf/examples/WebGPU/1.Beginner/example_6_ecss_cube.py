from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow

from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib

from pyGandalf.utilities.logger import logger

from pyGandalf.utilities.definitions import SHADERS_PATH

import numpy as np
import glm

"""
Showcase of an ecss cube consisting of an empty parent entity and six other entities for each face of the cube.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('ECSS Cube', 1280, 720, True), WebGPURenderer)

    # Create a new scene
    scene = Scene('ECSS Cube')

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

    # Build shaders 
    WebGPUShaderLib().build('unlit', SHADERS_PATH / 'webgpu' / 'unlit.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_Unlit', MaterialData('unlit', []))

    # Vertices of the square
    vertices = np.array([
        [-0.5, -0.5, 0.0], # 0 - Bottom left
        [ 0.5, -0.5, 0.0], # 1 - Bottom right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [-0.5,  0.5, 0.0], # 3 - Top left
        [-0.5, -0.5, 0.0]  # 0 - Bottom left
    ], dtype=np.float32)

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent("root"))
    scene.add_component(root, LinkComponent(None))

    # Register components to cube
    scene.add_component(cube, InfoComponent("cube"))
    scene.add_component(cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(15, 15, 15), glm.vec3(1, 1, 1)))
    scene.add_component(cube, LinkComponent(root))

    # Register components to cube_face_front
    scene.add_component(cube_face_front, InfoComponent("cube_face_front"))
    scene.add_component(cube_face_front, TransformComponent(glm.vec3(0.0, 0.0, 0.5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_front, LinkComponent(cube))
    scene.add_component(cube_face_front, WebGPUStaticMeshComponent('cube_face_front', [vertices]))
    scene.add_component(cube_face_front, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_back
    scene.add_component(cube_face_back, InfoComponent("cube_face_back"))
    scene.add_component(cube_face_back, TransformComponent(glm.vec3(0.0, 0.0, -0.5), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_back, LinkComponent(cube))
    scene.add_component(cube_face_back, WebGPUStaticMeshComponent('cube_face_back', [vertices]))
    scene.add_component(cube_face_back, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(1.0, 0.0, 0.0)

    # Register components to cube_face_right
    scene.add_component(cube_face_right, InfoComponent("cube_face_right"))
    scene.add_component(cube_face_right, TransformComponent(glm.vec3(0.5, 0.0, 0.0), glm.vec3(0, 90, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_right, LinkComponent(cube))
    scene.add_component(cube_face_right, WebGPUStaticMeshComponent('cube_face_right', [vertices]))
    scene.add_component(cube_face_right, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_left
    scene.add_component(cube_face_left, InfoComponent("cube_face_left"))
    scene.add_component(cube_face_left, TransformComponent(glm.vec3(-0.5, 0.0, 0.0), glm.vec3(0, 90, 180), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_left, LinkComponent(cube))
    scene.add_component(cube_face_left, WebGPUStaticMeshComponent('cube_face_left', [vertices]))
    scene.add_component(cube_face_left, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(0.0, 0.0, 1.0)

    # Register components to cube_face_top
    scene.add_component(cube_face_top, InfoComponent("cube_face_top"))
    scene.add_component(cube_face_top, TransformComponent(glm.vec3(0.0, 0.5, 0.0), glm.vec3(90, 0, 180), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_top, LinkComponent(cube))
    scene.add_component(cube_face_top, WebGPUStaticMeshComponent('cube_face_top', [vertices]))
    scene.add_component(cube_face_top, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to cube_face_bottom
    scene.add_component(cube_face_bottom, InfoComponent("cube_face_bottom"))
    scene.add_component(cube_face_bottom, TransformComponent(glm.vec3(0.0, -0.5, 0.0), glm.vec3(90, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(cube_face_bottom, LinkComponent(cube))
    scene.add_component(cube_face_bottom, WebGPUStaticMeshComponent('cube_face_bottom', [vertices]))
    scene.add_component(cube_face_bottom, WebGPUMaterialComponent('M_Unlit')).color = glm.vec3(1.0, 1.0, 0.0)

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, -5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([WebGPUStaticMeshComponent, WebGPUMaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()