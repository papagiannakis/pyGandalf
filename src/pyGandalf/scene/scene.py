from pyGandalf.scene.entity import Entity
from pyGandalf.utilities.logger import logger

class Scene():
    def __init__(self):
        self.entity_components = {}
        self.component_arrays = {}
        self.entities = []
        self.systems = []
    
    def enroll_entity(self):
        entity = Entity()
        self.entities.append(entity)
        return entity

    def get_entities(self):
        return self.entities
    
    def add_component(self, entity: Entity, component):
        # Create new component reference array for entity if it does not exist
        if entity.id not in self.entity_components:
            self.entity_components[entity.id] = {}

        # Retrieve type from component
        component_type = type(component)

        # Check if already has component
        if self.has_component(entity, component_type) is True:
            logger.info(f'Entity with id: {entity} already has component of type: {component_type}, returning that.')
            return self.get_component(entity, component_type)

        # Create new component array if it does not exist yet
        if component_type not in self.component_arrays:
            self.component_arrays[component_type] = []

        # Find the entities component reference
        component_array = self.component_arrays[component_type]
        component_index = len(component_array)

        # Update entity's component reference  
        self.entity_components[entity.id][component_type] = component_index

        # Add the new component to the appropriate component array
        component_array.append(component)

        # Update existing systems that operate on this component. (Usefull in runtime addition of components)
        for system in self.systems:
            entity_components = self.get_entity_component_references(entity)
            system.filter_entity_components(entity, entity_components, self.component_arrays)

        return component
    
    def remove_component(self, entity: Entity, component_type: type):
        if self.has_component(entity, component_type) is False:
            return

        # Update existing systems that operate on this component. (Usefull in runtime deletion of components)
        for system in self.systems:
            system.remove_entity_components(entity, component_type)

        # Update component arrays and entity components references
        self.component_arrays[component_type].pop(self.entity_components[entity.id][component_type])
        self.entity_components[entity.id].pop(component_type)

    def has_component(self, entity: Entity, component_type: type):
        return component_type in self.entity_components.get(entity.id)
    
    def get_component(self, entity: Entity, component_type: type):
        if component_type in self.entity_components[entity.id]:
            component_index = self.entity_components[entity.id][component_type]
            return self.component_arrays[component_type][component_index]
        else:
            return None
    
    def get_entity_component_references(self, entity: Entity):
        return self.entity_components.get(entity.id, {})
    
    def get_components_array(self):
        return self.component_arrays
    
    def register_system(self, system):
        self.systems.append(system)

        system.filter(self)

        from pyGandalf.core.application import Application

        if (Application().is_running()):
            system.on_create_base()

    def get_systems(self):
        return self.systems
    
    def get_system(self, system_type: type):
        for system in self.systems:
            if type(system) is system_type:
                return system
        return None
    
    def on_create(self):
        from pyGandalf.core.application import Application

        Application().set_is_running(True)
        
        for system in self.systems:
            system.on_create_base()

    def on_update(self, ts):
        for system in self.systems:
            system.on_update_base(ts)