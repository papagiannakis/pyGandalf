from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow

from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.system import System
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.webgpu_rendering_system import WebGPUStaticMeshRenderingSystem
from pyGandalf.systems.light_system import LightSystem

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData, MaterialDescriptor
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData, TextureDescriptor
from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.mesh_lib import MeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np

"""
Showcase of shadow mapping and basic Blinn-Phong lighting.
"""

class RotateAroundComponent(Component):
    def __init__(self, axis: list, speed: float) -> None:
        self.axis = axis
        self.speed = speed
        self.enabled = True

class RotateAroundSystem(System):
    """
    The system responsible rotating around entities.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        pass

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        rotate_around, transform = components

        if rotate_around.enabled:
            if rotate_around.axis[0] == 1:
                transform.rotation.x += rotate_around.speed * ts

            if rotate_around.axis[1] == 1:
                transform.rotation.y += rotate_around.speed * ts

            if rotate_around.axis[2] == 1:
                transform.rotation.z += rotate_around.speed * ts

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Shadow Mapping', 1280, 720, True), WebGPURenderer)

    WebGPURenderer().set_shadows_enabled(True)

    # Create a new scene
    scene = Scene('Shadow Mapping')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    bunny = scene.enroll_entity()
    monkey = scene.enroll_entity()
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
    depth_texture_descriptor: TextureDescriptor = TextureDescriptor()
    depth_texture_descriptor.view_format = wgpu.TextureFormat.depth32float
    depth_texture_descriptor.view_aspect = wgpu.TextureAspect.depth_only
    depth_texture_descriptor.format = wgpu.TextureFormat.depth32float
    depth_texture_descriptor.usage = wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.TEXTURE_BINDING
    depth_texture_descriptor.sampler_compare = wgpu.CompareFunction.less_equal
    WebGPUTextureLib().build('depth_texture', TextureData(width=1024, height=1024), descriptor=depth_texture_descriptor)
    WebGPUTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    WebGPUTextureLib().build('brickwall_texture', TextureData(TEXTURES_PATH / 'brickwall.jpg'))

    # Build shaders
    WebGPUShaderLib().build('shadow_mesh', SHADERS_PATH / 'webgpu' / 'shadow_mapping.wgsl')
    WebGPUShaderLib().build('depth_pre_pass', SHADERS_PATH / 'webgpu' / 'shadow_mapping_depth.wgsl')
    # WebGPUShaderLib().build('debug_quad_depth', SHADERS_PATH / 'webgpu' / 'debug_quad_depth.wgsl')
    
    # Build Materials
    WebGPUMaterialLib().build('M_LitShadows', MaterialData('shadow_mesh', ['white_texture', 'depth_texture'], glossiness=1.0))
    WebGPUMaterialLib().build('M_BrickFloor', MaterialData('shadow_mesh', ['brickwall_texture', 'depth_texture'], glossiness=0.75))
    WebGPUMaterialLib().build('M_DepthPrePass', MaterialData('depth_pre_pass', []), MaterialDescriptor(depth_compare=wgpu.CompareFunction.less, depth_format=wgpu.TextureFormat.depth32float))
    # WebGPUMaterialLib().build('M_DebugQuadDepth', MaterialData('debug_quad_depth', ['depth_texture'], glossiness=1.0), MaterialDescriptor(cast_shadows=False))

    # Load models
    MeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')
    MeshLib().build('monkey_mesh', MODELS_PATH/'monkey_flat.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to bunny
    scene.add_component(bunny, InfoComponent("bunny"))
    scene.add_component(bunny, TransformComponent(glm.vec3(-1, 0, 0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(bunny, LinkComponent(root))
    scene.add_component(bunny, StaticMeshComponent('bunny_mesh'))
    scene.add_component(bunny, MaterialComponent('M_LitShadows'))

    # Register components to monkey
    scene.add_component(monkey, InfoComponent("monkey"))
    scene.add_component(monkey, TransformComponent(glm.vec3(-1, 0, 1.5), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(monkey, LinkComponent(root))
    scene.add_component(monkey, StaticMeshComponent('monkey_mesh'))
    scene.add_component(monkey, MaterialComponent('M_LitShadows'))

    # Register components to floor
    scene.add_component(floor, InfoComponent("floor"))
    scene.add_component(floor, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(270, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(floor, LinkComponent(root))
    scene.add_component(floor, StaticMeshComponent('floor_mesh', [plane_vertices, plane_normals, plane_texture_coords]))
    scene.add_component(floor, MaterialComponent('M_LitShadows'))

    # # Register components to debug_depth_quad
    # scene.add_component(debug_depth_quad, InfoComponent("debug_depth_quad"))
    # scene.add_component(debug_depth_quad, TransformComponent(glm.vec3(-4, 4, 0), glm.vec3(0, 180, 0), glm.vec3(2, 2, 2)))
    # scene.add_component(debug_depth_quad, LinkComponent(root))
    # scene.add_component(debug_depth_quad, StaticMeshComponent('debug_depth_quad_mesh', [plane_vertices, plane_texture_coords]))
    # scene.add_component(debug_depth_quad, MaterialComponent('M_DebugQuadDepth'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 2, -2), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 3, -6), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(65, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(WebGPUStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))
    scene.register_system(RotateAroundSystem([RotateAroundComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()