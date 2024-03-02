from utilities.logger import logger

from enum import Enum

class SystemState(Enum):
    NONE = 0
    PLAY = 1
    PAUSE = 2

class System:
    def __init__(self, filters: list[type]):
        self.filters = filters
        self.filtered_components = []
        self.filtered_entities = []
        self.state = SystemState.PLAY        

    def set_state(self, state: SystemState):
        self.state = state

    def get_state(self):
        return self.state
    
    def filter(self, scene):
        components_array = scene.get_components_array()

        for entity in scene.get_entities():
            entity_components = scene.get_entity_component_references(entity)
            self.filter_entity_components(entity, entity_components, components_array)

    def filter_entity_components(self, entity, entity_components, components_array):
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
        if entity not in self.filtered_entities:
            return False

        index = self.filtered_entities.index(entity)
        
        if not tuple(filter(lambda i: (type(i) == component), self.filtered_components[index])):
            return False

        self.filtered_entities.remove(entity)
        self.filtered_components.pop(index)

        return True

    def on_create_base(self):
        # Check if the subclass has overridden the method
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
        # Check if the subclass has overridden the method
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
        return zip(self.filtered_entities, self.filtered_components)