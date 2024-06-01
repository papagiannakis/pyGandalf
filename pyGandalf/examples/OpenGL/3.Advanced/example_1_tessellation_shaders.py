from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.core.events import EventType
from pyGandalf.core.event_manager import EventManager

from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.systems.light_system import LightSystem
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData, MaterialDescriptor
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH
from pyGandalf.utilities.logger import logger

import glfw
import numpy as np
import OpenGL.GL as gl

"""
Showcase of displaying a height map using tessellation shaders.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    patch_resolution = 20
    vertices_per_patch = 4

    # Create a new application
    Application().create(OpenGLWindow('Tessellation Shaders', 1280, 720, True), OpenGLRenderer)

    # Create a new scene
    scene = Scene('Tessellation Shaders')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    terrain = scene.enroll_entity()

    # Build textures
    OpenGLTextureLib().build('height_map', TEXTURES_PATH/'iceland_heightmap.png')

    # Build shaders
    OpenGLShaderLib().build('default_tessellation', SHADERS_PATH/'tessellation_vertex.glsl', SHADERS_PATH/'tessellation_fragment.glsl', SHADERS_PATH/'tessellation_control.glsl', SHADERS_PATH/'tessellation_evaluation.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Terrain', MaterialData('default_tessellation', ['height_map']), MaterialDescriptor(primitive=gl.GL_PATCHES, cull_face=gl.GL_FRONT, patch_resolution=patch_resolution, vertices_per_patch=vertices_per_patch))

    vertices = []
    tex_coords = []

    width = OpenGLTextureLib().get_textures()['height_map'].descriptor.width
    height = OpenGLTextureLib().get_textures()['height_map'].descriptor.height

    for i in range(patch_resolution):
        for j in range(patch_resolution):
            vertex = []
            vertex.append(-width / 2.0 + width * i / float(patch_resolution))  # v.x
            vertex.append(0.0)  # v.y
            vertex.append(-height / 2.0 + height * j / float(patch_resolution))  # v.z
            vertices.append(vertex)

            tex_coord = []
            tex_coord.append(i / float(patch_resolution))  # u
            tex_coord.append(j / float(patch_resolution))  # v
            tex_coords.append(tex_coord)

            vertex = []
            vertex.append(-width / 2.0 + width * (i + 1) / float(patch_resolution))  # v.x
            vertex.append(0.0)  # v.y
            vertex.append(-height / 2.0 + height * j / float(patch_resolution))  # v.z
            vertices.append(vertex)

            tex_coord = []
            tex_coord.append((i + 1) / float(patch_resolution))  # u
            tex_coord.append(j / float(patch_resolution))  # v
            tex_coords.append(tex_coord)

            vertex = []
            vertex.append(-width / 2.0 + width * i / float(patch_resolution))  # v.x
            vertex.append(0.0)  # v.y
            vertex.append(-height / 2.0 + height * (j + 1) / float(patch_resolution))  # v.z
            vertices.append(vertex)

            tex_coord = []
            tex_coord.append(i / float(patch_resolution))  # u
            tex_coord.append((j + 1) / float(patch_resolution))  # v
            tex_coords.append(tex_coord)

            vertex = []
            vertex.append(-width / 2.0 + width * (i + 1) / float(patch_resolution))  # v.x
            vertex.append(0.0)  # v.y
            vertex.append(-height / 2.0 + height * (j + 1) / float(patch_resolution))  # v.z
            vertices.append(vertex)

            tex_coord = []
            tex_coord.append((i + 1) / float(patch_resolution))  # u
            tex_coord.append((j + 1) / float(patch_resolution))  # v
            tex_coords.append(tex_coord)

    vertices = np.asarray(vertices, np.float32)
    tex_coords = np.asarray(tex_coords, np.float32)

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to terrain
    scene.add_component(terrain, InfoComponent("terrain"))
    scene.add_component(terrain, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(terrain, LinkComponent(root))
    scene.add_component(terrain, StaticMeshComponent('terrain_mesh', [vertices, tex_coords]))
    scene.add_component(terrain, MaterialComponent('M_Terrain'))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 50, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, LinkComponent(root))
    scene.add_component(camera, CameraComponent(45, 1.778, 0.1, 2000, 1.2, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent(15, 2))

    # Create Register systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(LightSystem([LightComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Attach events
    def on_key_callback(key, modifiers):
        if key == glfw.KEY_F:
            OpenGLRenderer().set_fill_mode(gl.GL_FILL)
        if key == glfw.KEY_L:
            OpenGLRenderer().set_fill_mode(gl.GL_LINE)

    EventManager().attach_callback(EventType.KEY_PRESS, on_key_callback, True)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()