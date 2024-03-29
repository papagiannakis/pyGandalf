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

        match camera.type:
            case CameraComponent.Type.PERSPECTIVE:
                camera.projection = glm.perspective(glm.radians(camera.fov), camera.aspect_ratio, camera.near, camera.far)
            case CameraComponent.Type.ORTHOGRAPHIC:
                camera.projection = glm.ortho(-camera.aspect_ratio * camera.zoom_level, camera.aspect_ratio * camera.zoom_level, -camera.zoom_level, camera.zoom_level, camera.near, camera.far)

        if camera.primary:
            SceneManager().set_main_camera(entity, camera)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        camera, transform = components

        if not camera.static:
            camera, transform = components
            camera.view = glm.inverse(transform.world_matrix)
            camera.view_projection = camera.projection * camera.view
        
        match camera.type:
            case CameraComponent.Type.PERSPECTIVE:
                camera.projection = glm.perspective(glm.radians(camera.fov), camera.aspect_ratio, camera.near, camera.far)
            case CameraComponent.Type.ORTHOGRAPHIC:
                camera.projection = glm.ortho(-camera.aspect_ratio * camera.zoom_level, camera.aspect_ratio * camera.zoom_level, -camera.zoom_level, camera.zoom_level, camera.near, camera.far)

        if camera.primary:
            SceneManager().set_main_camera(entity, camera)