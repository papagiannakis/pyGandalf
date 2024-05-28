from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import Component

from pyGandalf.core.events import Event, PushEvent, EventType
from pyGandalf.utilities.logger import logger

from enum import Enum

class SystemState(Enum):
    NONE = 0
    PLAY = 1
    PAUSE = 2

class System:
    """A class that represents a system that operates on entities that have all the specified components.
    """
    def __init__(self, filters: list[type]):
        self.filters = filters
        self.filtered_components = []
        self.filtered_entities = []
        self.state = SystemState.PLAY        

    def set_state(self, state: SystemState):
        """Sets the state of the system.

        Args:
            state (SystemState): The state of the system.
        """
        self.state = state
        self.record_system_state_event(type(self), self.state)

    def get_state(self) -> SystemState:
        """Returns the state of the system.

        Returns:
            SystemState: The state of the system.
        """
        return self.state
    
    def filter(self, scene):
        """Filters from the given scene the entities and their component that the system operates on and caches them.

        Args:
            scene (Scene): The scene to filter entities from.
        """
        components_array = scene.get_components_array()

        for entity in scene.get_entities():
            entity_components = scene.get_entity_component_references(entity)
            self.filter_entity_components(entity, entity_components, components_array)

    def filter_entity_components(self, entity, entity_components, components_array):
        """Stores the given entity and its components if the entity has all the components that the system operates on.

        Args:
            entity (Entity): The entity to process.
            entity_components (_type_): The components of the entity.
            components_array (_type_): The dictionary holding all the component arrays.
        """
        if (entity in self.filtered_entities):
            return
        
        i, j = 0, 0
        for filter in self.filters:
            j += 1
            if filter in entity_components.keys():
                i += 1            
        if (j == i):
            self.filtered_components.append(tuple(components_array[filter][entity_components[filter]] for filter in self.filters))
            self.filtered_entities.append(entity)
            
            return self.filtered_components[-1]
        
        return None

    def remove_entity_components(self, entity, component):
        """Removes the entity and its component from the cached arrays.

        Args:
            entity (Entity): The entity to remove.
            component (_type_): The component to remove.

        Returns:
            bool: ```True``` if the enity and the component was successfully removed from the system or ```False``` if it was not present in the cached arrays of the system.
        """
        if entity not in self.filtered_entities:
            return False

        index = self.filtered_entities.index(entity)
        
        if not tuple(filter(lambda i: (type(i) == component), self.filtered_components[index])):
            return False

        self.filtered_entities.remove(entity)
        self.filtered_components.pop(index)

        return True

    def on_create_base(self):
        """Calls the `on_create_entity` and `on_create_system` method of the system for each entity and its filtered components.
        """
        if self.state is SystemState.PLAY:
            self.on_create_system()

        if self.state is SystemState.PLAY:
            for entity, components in zip(self.filtered_entities, self.filtered_components):
                if (len(components) == 1):
                    self.on_create_entity(entity, components[0])
                else:
                    self.on_create_entity(entity, components)

    def on_update_base(self, ts: float):
        """Calls the `on_update_entity` and `on_update_system` methods of the system for each entity and its filtered components.
        """
        if self.state is SystemState.PLAY:
            self.on_update_system(ts)

        if self.state is SystemState.PLAY:
            for entity, components in zip(self.filtered_entities, self.filtered_components):
                if (len(components) == 1):
                    self.on_update_entity(ts, entity, components[0])
                else:
                    self.on_update_entity(ts, entity, components)

    def on_gui_update_base(self, ts: float):
        """Calls the `on_gui_update_entity` and `on_gui_update_system` methods of the system for each entity and its filtered components.
        """
        if self.state is SystemState.PLAY:
            self.on_gui_update_system(ts)

        if self.state is SystemState.PLAY:
            for entity, components in zip(self.filtered_entities, self.filtered_components):
                if (len(components) == 1):
                    self.on_gui_update_entity(ts, entity, components[0])
                else:
                    self.on_gui_update_entity(ts, entity, components)
    
    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        """Gets called once in the first frame for each entity that the system operates on.

        Args:
            entity (Entity): The current entity to process.
            components (Component | tuple[Component]): The component(s) of the current entity that are manipulated by the system.
        """
        pass

    def on_update_entity(self, ts: float, entity: Entity, components: Component | tuple[Component]):
        """Gets called every frame for each entity that the system operates on.

        Args:
            ts (float): The application time step (delta time).
            entity (Entity): The current entity to process.
            components (Component | tuple[Component]): The component(s) of the current entity that are manipulated by the system.
        """
        pass

    def on_gui_update_entity(self, ts: float, entity: Entity, components: Component | tuple[Component]):
        """Gets called every frame for each entity that the system operates on and responsible for drawing gui elements.

        Args:
            ts (float): The application time step (delta time).
            entity (Entity): The current entity to process.
            components (Component | tuple[Component]): The component(s) of the current entity that are manipulated by the system.
        """
        pass

    def on_create_system(self):
        """Gets called once in the first frame and initializes the system (filtered entities and their components).
        """
        pass

    def on_update_system(self, ts: float):
        """Gets called every frame to update the system (filtered entities and their components).

        Args:
            ts (float): The application time step (delta time).
        """
        pass

    def on_gui_update_system(self, ts: float):
        """Gets called every frame to update the system gui (gui for filtered entities and their components).

        Args:
            ts (float): The application time step (delta time).
        """
        pass

    def filtered_data(self):
        """Returns the entities and components that the system operates on, zipped.

        Returns:
            _type_: The entities and components that the system operates on, zipped.
        """
        return zip(self.filtered_entities, self.filtered_components)
    
    def get_filtered_entities(self):
        """Returns the entities that the system operates on.

        Returns:
            list[Entity]: The entities that the system operates on.
        """
        return self.filtered_entities
    
    def get_filtered_components(self):
        """Returns the components that the system operates on.

        Returns:
            list[tuple]: The components that the system operates on.
        """
        return self.filtered_components
    
    def record_system_state_event(cls, type: type, state: SystemState):
        """Pushes an EventType.SYSTEM_STATE event when the system state changes.

        Args:
            type (type): The type of the System
            state (SystemState): The new system state.
        """
        ev = {  
            "type": type,
            "state": state
        }

        event = Event() 
        event.type = EventType.SYSTEM_STATE
        event.data = ev  
        PushEvent(event)