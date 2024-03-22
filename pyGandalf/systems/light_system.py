from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System

class LightSystem(System):
    """
    The system responsible for the lighting.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        pass

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        pass