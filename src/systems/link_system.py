from scene.entity import Entity
from scene.components import LinkComponent, TransformComponent
from scene.scene_manager import SceneManager
from systems.system import System

import numpy as np
import glm

class LinkSystem(System):
    """
    The system responsible for the scene hierachy.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        link, transform = components
        transform.world_matrix = self.get_world_space_transform(entity, link)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        link, transform = components
        transform.world_matrix = self.get_world_space_transform(entity, link)

    def get_world_space_transform(self, entity, link):
        transform = glm.mat4(1.0)

        if link is not None:
            if link.parent is not None:
                parent_link = SceneManager().get_active_scene().get_component(link.parent, LinkComponent)
                transform = self.get_world_space_transform(link.parent, parent_link)

        return transform * SceneManager().get_active_scene().get_component(entity, TransformComponent).local_matrix