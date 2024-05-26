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
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureDescriptor
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np

"""
Showcase of shadow mapping and basic Blinn-Phong lighting.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('Shadow Mapping', 1280, 720, True), OpenGLRenderer)

    OpenGLRenderer().set_shadows_enabled(True)

    # Create a new scene
    scene = Scene('Shadow Mapping')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    bunny = scene.enroll_entity()
    dragon = scene.enroll_entity()
    floor = scene.enroll_entity()
    light = scene.enroll_entity()
    debug_depth_quad = scene.enroll_entity()

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
    OpenGLTextureLib().build('white_texture', None, 0xffffffff.to_bytes(4, byteorder='big'), descriptor=TextureDescriptor(width=1, height=1))
    OpenGLTextureLib().build('brickwall_texture', TEXTURES_PATH/'brickwall.jpg')

    # Build shaders
    OpenGLShaderLib().build('shadow_mesh', SHADERS_PATH/'shadow_mapping_vertex.glsl', SHADERS_PATH/'shadow_mapping_fragment.glsl')
    OpenGLShaderLib().build('depth_pre_pass', SHADERS_PATH/'shadow_mapping_depth_vertex.glsl', SHADERS_PATH/'shadow_mapping_depth_fragment.glsl')
    OpenGLShaderLib().build('debug_quad_depth', SHADERS_PATH/'debug_quad_depth_vertex.glsl', SHADERS_PATH/'debug_quad_depth_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_LitShadows', MaterialData('shadow_mesh', ['white_texture', 'depth_texture']))
    OpenGLMaterialLib().build('M_BrickFloor', MaterialData('shadow_mesh', ['brickwall_texture', 'depth_texture']))
    OpenGLMaterialLib().build('M_DepthPrePass', MaterialData('depth_pre_pass', []))
    OpenGLMaterialLib().build('M_DebugQuadDepth', MaterialData('debug_quad_depth', ['depth_texture']))

    # Load models
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')
    OpenGLMeshLib().build('dragon_mesh', MODELS_PATH/'dragon.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to bunny
    scene.add_component(bunny, InfoComponent("bunny"))
    scene.add_component(bunny, TransformComponent(glm.vec3(-1, 0, 0), glm.vec3(0, 10, 0), glm.vec3(1, 1, 1)))
    scene.add_component(bunny, LinkComponent(root))
    scene.add_component(bunny, StaticMeshComponent('bunny_mesh'))
    scene.add_component(bunny, MaterialComponent('M_LitShadows')).glossiness = 1.5

    # Register components to dragon
    scene.add_component(dragon, InfoComponent("dragon"))
    scene.add_component(dragon, TransformComponent(glm.vec3(2, 0.8, 0), glm.vec3(0, 90, 0), glm.vec3(3, 3, 3)))
    scene.add_component(dragon, LinkComponent(root))
    scene.add_component(dragon, StaticMeshComponent('dragon_mesh'))
    scene.add_component(dragon, MaterialComponent('M_LitShadows')).glossiness = 1.5

    # Register components to floor
    scene.add_component(floor, InfoComponent("floor"))
    scene.add_component(floor, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(270, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(floor, LinkComponent(root))
    scene.add_component(floor, StaticMeshComponent('floor_mesh', [plane_vertices, plane_normals, plane_texture_coords]))
    scene.add_component(floor, MaterialComponent('M_BrickFloor')).glossiness = 0.75

    # Register components to debug_depth_quad
    scene.add_component(debug_depth_quad, InfoComponent("debug_depth_quad"))
    scene.add_component(debug_depth_quad, TransformComponent(glm.vec3(-4, 4, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(debug_depth_quad, LinkComponent(root))
    scene.add_component(debug_depth_quad, StaticMeshComponent('debug_depth_quad_mesh', [plane_vertices, plane_texture_coords]))
    scene.add_component(debug_depth_quad, MaterialComponent('M_DebugQuadDepth')).glossiness = 1.0

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 2, 2), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 4, 8), glm.vec3(-25, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
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