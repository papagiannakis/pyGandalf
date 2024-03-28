from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import LinkComponent, TransformComponent
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.systems.system import System

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

        self.add_children(entity, link)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        link, transform = components
        transform.world_matrix = self.get_world_space_transform(entity, link)

        self.update_children(entity, link)

    def get_world_space_transform(self, entity, link):
        transform = glm.mat4(1.0)

        if link is not None:
            if link.parent is not None:
                parent_link = SceneManager().get_active_scene().get_component(link.parent, LinkComponent)
                transform = self.get_world_space_transform(link.parent, parent_link)

        return transform * SceneManager().get_active_scene().get_component(entity, TransformComponent).local_matrix
    
    def add_children(self, entity: Entity, link: LinkComponent):
        # If the entity has a parent, add it as a child of the parent
        if link.parent is not None:
            parent_link = SceneManager().get_active_scene().get_component(link.parent, LinkComponent)
            if parent_link is not None:
                parent_link.children.append(entity)

    def update_children(self, entity: Entity, link: LinkComponent):
        # Check if the entity's parent has changed or if it's no longer a child
        if link.prev_parent != link.parent:
            # Remove the entity from its previous parent's children list
            if link.prev_parent is not None:
                previous_parent_link = SceneManager().get_active_scene().get_component(link.prev_parent, LinkComponent)
                if previous_parent_link is not None and entity in previous_parent_link.children:
                    previous_parent_link.children.remove(entity)

            # Add the entity to its new parent's children list
            if link.parent is not None:
                current_parent_link = SceneManager().get_active_scene().get_component(link.parent, LinkComponent)
                if current_parent_link is not None:
                    current_parent_link.children.append(entity)

            # Update previous parent to be the current
            link.prev_parent = link.parent