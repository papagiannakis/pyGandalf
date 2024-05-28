from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System
from pyGandalf.utilities.logger import logger
from pyGandalf.scene.components import LinkComponent
from pyGandalf.scene.editor_components import EditorVisibleComponent

class Scene():
    """A class that represents a scene which contains all the entities, their components and the registered systems.
    """
    def __init__(self, name = 'UnnamedScene'):
        self.entity_components = {}
        self.component_arrays = {}
        self.entities = []
        self.systems = []
        self.name = name
    
    def enroll_entity(self) -> Entity:
        """Creates and enrolls a new entity to the scene.

        Returns:
            Entity: The newly created entity.
        """
        entity = Entity()
        self.entities.append(entity)
        self.add_component(entity, EditorVisibleComponent())
        return entity
    
    def enroll_entity_with_uuid(self, uuid) -> Entity:
        """Creates and enrolls a new entity to the scene with the given uuid as id.

        Args:
            uuid (_type_): The uuid to set to the entitys' id.

        Returns:
            Entity: The newly created entity.
        """
        entity = Entity()
        entity.id = uuid
        self.entities.append(entity)
        self.add_component(entity, EditorVisibleComponent())
        return entity
    
    def destroy_entity(self, entity: Entity):
        """Destroy the given entity from the scene. If the entity has children, recursively destroys them all.

        Args:
            entity (Entity): The entity to destroy.
        """
        entity_component_references = self.get_entity_component_references(entity)

        component_types = []
        for type in entity_component_references.keys():
            component_types.append(type)

        # Recursively destroy all children of entity.
        link = self.get_component(entity, LinkComponent)
        if link != None:
            for child in link.children:
                self.destroy_entity(child)

        # Remove all components from entity.
        for component_type in component_types:
            self.remove_component(entity, component_type)

        # Remove entity from list.
        if entity in self.entities:
            self.entities.remove(entity) 

    def get_entities(self) -> list[Entity]:
        """Returns a list containing all the enrolled entities of the scene.

        Returns:
            list[Entity]: A list containing all the enrolled entities of the scene.
        """
        return self.entities
    
    def add_component(self, entity: Entity, component):
        """Adds to the specified entity the given component, if the entity does not already have a component of that type. Also adds the component and entity to the systems that operate on the compoent type.

        Args:
            entity (Entity): The entity to add the given component to.
            component (type(component)): The component to add to the given entity.

        Returns:
            type(component): The component that was added or the already existing one if the entity already has a component of that type.
        """
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
            components = system.filter_entity_components(entity, entity_components, self.component_arrays)

            from pyGandalf.core.application import Application
            if (Application().is_running()):
                if components != None:
                    if (len(components) == 1):
                        system.on_create_entity(entity, components[0])
                    else:
                        system.on_create_entity(entity, components)

        return component
    
    def remove_component(self, entity: Entity, component_type: type):
        """Removes from the specified entity the component of the given type (if the entity has a component of that type) and from all the systems that operate on the component type.

        Args:
            entity (Entity): The entity to remove the component from.
            component_type (type): The type of the component to remove from the entity.
        """
        if self.has_component(entity, component_type) is False:
            return

        # Update existing systems that operate on this component. (Usefull in runtime deletion of components)
        for system in self.systems:
            system.remove_entity_components(entity, component_type)

        # Update component arrays and entity components references
        self.component_arrays[component_type][self.entity_components[entity.id][component_type]] = None
        self.entity_components[entity.id][component_type] = None

    def has_component(self, entity: Entity, component_type: type) -> bool:
        """Returns whether or not the specified entity has a compoent of the given type.

        Args:
            entity (Entity): The entity to check.
            component_type (type): The type of component to check.

        Returns:
            bool: ```True``` if the entity has the component or ```False``` otherwise.
        """
        return (entity.id in self.entity_components and
                component_type in self.entity_components.get(entity.id) and
                self.entity_components[entity.id][component_type] != None and
                self.component_arrays[component_type][self.entity_components[entity.id][component_type]] != None)
    
    def get_component(self, entity: Entity, component_type: type):
        """Returns a component of the specified type from the given entity or ```None``` if the entity does not have a component of the specified type.

        Args:
            entity (Entity): The entity to get the component from.
            component_type (type): The type of component to get from the given entity.

        Returns:
            component: The component of the specified type from the given entity or ```None``` if the entity does not have a component of the specified type.
        """
        if self.has_component(entity, component_type) == False:
            return None
        
        component_index = self.entity_components[entity.id][component_type]
        return self.component_arrays[component_type][component_index]
    
    def get_entity_component_references(self, entity: Entity):
        """Returns a dictionary with keys the component type and values the indices to the component arrays for the specified entity.

        Args:
            entity (Entity): The entity to get the component references for.

        Returns:
            dict[type, list[int]]: A dictionary with keys the component type and values the indices to the component arrays for the specified entity.
        """
        return self.entity_components.get(entity.id, {})
    
    def get_components_array(self):
        """Returns a dictionary with keys the compoennt type and values the component arrays.

        Returns:
            dict[type, list[component]]: A dictionary with keys the component type and values the component arrays.
        """
        return self.component_arrays
    
    def register_system(self, system: System):
        """Registers a system to the scene. If called at runtime it will also start the system.

        Args:
            system (System): The system to register to the scene.
        """
        self.systems.append(system)

        system.filter(self)

        from pyGandalf.core.application import Application

        if (Application().is_running()):
            system.on_create_base()

    def get_systems(self) -> list[System]:
        """Return a list containing all the systems of the scene.

        Returns:
            list[System]: A list containing all the systems of the scene.
        """
        return self.systems
    
    def get_system(self, system_type: type) -> (System | None):
        """Returns a system from the scene of the specified type.

        Args:
            system_type (type): The type of the system to get.

        Returns:
            System: A system from the scene of the specified type or ```None``` if the scene does not have a system with the specified type.
        """
        for system in self.systems:
            if type(system) is system_type:
                return system
        return None
    
    def on_create(self):
        """Called on the first frame and calls all the on_create_base method from all the registered systems of the scene.
        """
        from pyGandalf.core.application import Application

        Application().set_is_running(True)
        
        for system in self.systems:
            system.on_create_base()

    def on_update(self, ts: float):
        """Called every frame and calls all the on_update_base method from all the registered systems of the scene.

        Args:
            ts (float): The application timestep.
        """
        for system in self.systems:
            system.on_update_base(ts)

    def on_gui_update(self, ts: float):
        """Called every frame and calls all the on_update_gui_base method from all the registered systems of the scene.

        Args:
            ts (float): The application timestep.
        """
        for system in self.systems:
            system.on_gui_update_base(ts)