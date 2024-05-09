from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import Component
from pyGandalf.systems.system import System

class LightSystem(System):
    """
    The system responsible for the lighting.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        pass

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        pass