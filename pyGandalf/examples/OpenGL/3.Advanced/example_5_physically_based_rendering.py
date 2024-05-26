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
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger

import numpy as np
import OpenGL.GL as gl

"""
Showcase of obj model loading with textures and Physically Based Rendering(PBR).
"""

def get_sphere_vertex_data():
    positions = []
    uv = []
    normals = []
    indices = []

    X_SEGMENTS = 64
    Y_SEGMENTS = 64

    for x in range(X_SEGMENTS + 1):
        for y in range(Y_SEGMENTS + 1):
            xSegment = float(x) / float(X_SEGMENTS)
            ySegment = float(y) / float(Y_SEGMENTS)
            xPos = np.cos(xSegment * 2.0 * np.pi) * np.sin(ySegment * np.pi)
            yPos = np.cos(ySegment * np.pi)
            zPos = np.sin(xSegment * 2.0 * np.pi) * np.sin(ySegment * np.pi)

            positions.append([xPos, yPos, zPos])
            uv.append([xSegment, ySegment])
            normals.append([xPos, yPos, zPos])

    oddRow = False
    for y in range(Y_SEGMENTS):
        if not oddRow:  # even rows: y == 0, y == 2; and so on
            for x in range(X_SEGMENTS + 1):
                indices.append(y * (X_SEGMENTS + 1) + x)
                indices.append((y + 1) * (X_SEGMENTS + 1) + x)
        else:
            for x in range(X_SEGMENTS, -1, -1):
                indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                indices.append(y * (X_SEGMENTS + 1) + x)
        oddRow = not oddRow

    vertices = np.asarray(positions, dtype=np.float32)
    normals = np.asarray(normals, dtype=np.float32)
    uvs = np.asarray(uv, dtype=np.float32)
    indices = np.asarray(indices, dtype=np.uint32)

    return vertices, normals, uvs, indices

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('Physically Based Rendering(PBR) Textured Model', 1280, 720, True), OpenGLRenderer)

    # Create a new scene
    scene = Scene('Physically Based Rendering(PBR) Textured Model')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    rusted_sphere = scene.enroll_entity()
    light = scene.enroll_entity()

    # Build textures
    OpenGLTextureLib().build('rusted_sphere_albedo', TEXTURES_PATH / 'rusted_iron' / 'rustediron2_basecolor.png')
    OpenGLTextureLib().build('rusted_sphere_normal', TEXTURES_PATH / 'rusted_iron' / 'rustediron2_normal.png')
    OpenGLTextureLib().build('rusted_sphere_metallic', TEXTURES_PATH / 'rusted_iron' / 'rustediron2_metallic.png')
    OpenGLTextureLib().build('rusted_sphere_roughness', TEXTURES_PATH / 'rusted_iron' / 'rustediron2_roughness.png')
    # OpenGLTextureLib().build('rusted_sphere_ao', TEXTURES_PATH / 'rusted_iron' / 'fa_flintlockPistol_albedo.jpg')

    # Build shaders
    OpenGLShaderLib().build('pbr_mesh', SHADERS_PATH/'lit_pbr_vertex.glsl', SHADERS_PATH/'lit_pbr_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_PBR', MaterialData('pbr_mesh', ['rusted_sphere_albedo', 'rusted_sphere_normal', 'rusted_sphere_metallic', 'rusted_sphere_roughness']))

    # Load models
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

    vertices, normals, uvs, indices = get_sphere_vertex_data()

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to rusted_sphere
    scene.add_component(rusted_sphere, InfoComponent("rusted_sphere"))
    scene.add_component(rusted_sphere, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(rusted_sphere, LinkComponent(root))
    scene.add_component(rusted_sphere, StaticMeshComponent('sphere_mesh', [vertices, normals, uvs], indices))
    scene.add_component(rusted_sphere, MaterialComponent('M_PBR', descriptor=MaterialComponent.Descriptor(primitive=gl.GL_TRIANGLE_STRIP)))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 2, 2), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 1.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-0.25, 2, 4), glm.vec3(-25, 0, 0), glm.vec3(1, 1, 1)))
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