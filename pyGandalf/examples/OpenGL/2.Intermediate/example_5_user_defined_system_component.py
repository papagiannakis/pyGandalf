from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.systems.system import System
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

"""
Showcase of user defined system and component.
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

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        # NOTE: These should match the components that the system operates on, which are defined in the system instantiation.
        #       See line 145: 'scene.register_system(RotateAroundSystem([RotateAroundComponent, TransformComponent]))'
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
    Application().create(OpenGLWindow('User Defined System and Component', 1280, 720, True), OpenGLRenderer)

    # Create a new scene
    scene = Scene('User Defined System and Component')

    # Create Enroll entities to registry
    root = scene.enroll_entity()
    camera = scene.enroll_entity()
    pistol = scene.enroll_entity()
    monkey = scene.enroll_entity()
    bunny = scene.enroll_entity()
    light = scene.enroll_entity()

    # Build textures
    OpenGLTextureLib().build('white_texture', None, 0xffffffff.to_bytes(4, byteorder='big'), descriptor=TextureDescriptor(width=1, height=1))
    OpenGLTextureLib().build('flintlockPistol_albedo', TEXTURES_PATH/'fa_flintlockPistol_albedo.jpg')

    # Build shaders
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    
    # Build Materials
    OpenGLMaterialLib().build('M_Pistol', MaterialData('default_mesh', ['flintlockPistol_albedo']))
    OpenGLMaterialLib().build('M_BlinnPhong', MaterialData('default_mesh', ['white_texture']))

    # Load models
    OpenGLMeshLib().build('pistol_mesh', MODELS_PATH/'fa_flintlockPistol.obj')
    OpenGLMeshLib().build('monkey_mesh', MODELS_PATH/'monkey_flat.obj')
    OpenGLMeshLib().build('bunny_mesh', MODELS_PATH/'bunny.obj')

    # Register components to root
    scene.add_component(root, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(root, InfoComponent('root'))
    scene.add_component(root, LinkComponent(None))

    # Register components to pistol
    scene.add_component(pistol, InfoComponent("pistol"))
    scene.add_component(pistol, TransformComponent(glm.vec3(0, 1, 0), glm.vec3(0, 0, 0), glm.vec3(15, 15, 15)))
    scene.add_component(pistol, LinkComponent(root))
    scene.add_component(pistol, StaticMeshComponent('pistol_mesh'))
    scene.add_component(pistol, MaterialComponent('M_Pistol'))
    scene.add_component(pistol, RotateAroundComponent([0, 1, 0], 30.0))

    # Change the material properties of the pistol
    material: MaterialComponent = scene.get_component(pistol, MaterialComponent)
    material.glossiness = 2.0

    # Register components to monkey
    scene.add_component(monkey, InfoComponent("monkey"))
    scene.add_component(monkey, TransformComponent(glm.vec3(5, 1, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(monkey, LinkComponent(root))
    scene.add_component(monkey, StaticMeshComponent('monkey_mesh'))
    scene.add_component(monkey, MaterialComponent('M_BlinnPhong'))
    scene.add_component(monkey, RotateAroundComponent([1, 0, 0], 30.0))

    # Register components to bunny
    scene.add_component(bunny, InfoComponent("bunny"))
    scene.add_component(bunny, TransformComponent(glm.vec3(-5, 1, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(bunny, LinkComponent(root))
    scene.add_component(bunny, StaticMeshComponent('bunny_mesh'))
    scene.add_component(bunny, MaterialComponent('M_BlinnPhong'))
    scene.add_component(bunny, RotateAroundComponent([0, 0, 1], 30.0))

    # Register components to light
    scene.add_component(light, InfoComponent("light"))
    scene.add_component(light, TransformComponent(glm.vec3(-2, 4, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(light, LinkComponent(root))
    scene.add_component(light, LightComponent(glm.vec3(1.0, 1.0, 1.0), 0.75))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(-0.25, 5, 9), glm.vec3(-25, 0, 0), glm.vec3(1, 1, 1)))
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

    # Register our custom system - it needs all the entities that have the RotateAroundComponent and the TransformComponent
    scene.register_system(RotateAroundSystem([RotateAroundComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()