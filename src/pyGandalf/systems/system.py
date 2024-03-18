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
        """Calls the on_create method of the system for each entity and its filtered components.
        """
        if hasattr(self, 'on_create') and callable(getattr(self, 'on_create')):
            if self.state is SystemState.PLAY:
                for entity, components in zip(self.filtered_entities, self.filtered_components):
                    if (len(components) == 1):
                        self.on_create(entity, components[0])
                    else:
                        self.on_create(entity, components)
        else:
            logger.error("on_update method not implemented")

    def on_update_base(self, ts):
        """Calls the on_update method of the system for each entity and its filtered components.
        """
        if hasattr(self, 'on_update') and callable(getattr(self, 'on_update')):
            if self.state is SystemState.PLAY:
                for entity, components in zip(self.filtered_entities, self.filtered_components):
                    if (len(components) == 1):
                        self.on_update(ts, entity, components[0])
                    else:
                        self.on_update(ts, entity, components)
        else:
            logger.error("on_update method not implemented")

    def filtered_data(self):
        """Returns the entities and components that the system operates on zipped.

        Returns:
            _type_: The entities and components that the system operates on zipped.
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