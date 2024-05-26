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

"""
Showcase of obj model loading with textures and Physically Based Rendering(PBR).
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(OpenGLWindow('Physically Based Rendering(PBR) with Textured Model', 1280, 720, True), OpenGLRenderer, True, True)

    # Create a new scene
    scene = Scene('Physically Based Rendering(PBR) with Textured Model')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    cerberus = scene.enroll_entity()
    light = scene.enroll_entity()

    # Build textures
    OpenGLTextureLib().build('cerberus_albedo', TEXTURES_PATH / 'Cerberus' / 'Cerberus_A.png')
    OpenGLTextureLib().build('cerberus_normal', TEXTURES_PATH / 'Cerberus' / 'Cerberus_N.png')
    OpenGLTextureLib().build('cerberus_metallic', TEXTURES_PATH / 'Cerberus' / 'Cerberus_M.png')
    OpenGLTextureLib().build('cerberus_roughness', TEXTURES_PATH / 'Cerberus' / 'Cerberus_R.png')

    # Build shaders
    OpenGLShaderLib().build('pbr_mesh', SHADERS_PATH/'lit_pbr.vs', SHADERS_PATH/'lit_pbr.fs')
    
    # Build Materials
    OpenGLMaterialLib().build('M_PBR', MaterialData('pbr_mesh', ['cerberus_albedo', 'cerberus_normal', 'cerberus_metallic', 'cerberus_roughness']))

    # Load models
    OpenGLMeshLib().build('cerberus_mesh', MODELS_PATH/'cerberus_lp.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to cerberus
    scene.add_component(cerberus, InfoComponent("cerberus"))
    scene.add_component(cerberus, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0.1, 0.1, 0.1)))
    scene.add_component(cerberus, LinkComponent(root))
    scene.add_component(cerberus, StaticMeshComponent('cerberus_mesh'))
    scene.add_component(cerberus, MaterialComponent('M_PBR'))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(0, 0, 4.5), glm.vec3(50, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 100.0))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(6, 3, 6.5), glm.vec3(-22, 40, 0), glm.vec3(1, 1, 1)))
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