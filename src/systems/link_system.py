from scene.entity import Entity
from scene.components import LinkComponent, TransformComponent
from scene.scene_manager import SceneManager
from systems.system import System

import numpy as np

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
        transform = np.identity(4)

        if (link != None):
            if (link.parent != None):
                parent_link = SceneManager().get_active_scene().get_component(link.parent, LinkComponent)
                transform = self.get_world_space_transform(link.parent, parent_link)

        return transform @ SceneManager().get_active_scene().get_component(entity, TransformComponent).local_matrix