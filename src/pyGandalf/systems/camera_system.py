from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System
from pyGandalf.scene.components import CameraComponent, TransformComponent

from pyGandalf.scene.scene_manager import SceneManager

import glm

class CameraSystem(System):
    """
    The system responsible for the cameras.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        camera, transform = components
        camera.view = glm.inverse(transform.world_matrix)
        camera.view_projection = camera.projection * camera.view

        if camera.primary:
            SceneManager().set_main_camera(camera)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        camera, transform = components

        if not camera.static:
            camera, transform = components
            camera.view = glm.inverse(transform.world_matrix)
            camera.view_projection = camera.projection * camera.view

            if camera.primary:
                SceneManager().set_main_camera(camera)
        else:
            if camera.primary:
                SceneManager().set_main_camera(camera)