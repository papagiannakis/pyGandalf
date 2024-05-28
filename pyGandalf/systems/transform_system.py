from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import Component
from pyGandalf.systems.system import System

import numpy as np
import glm

class TransformSystem(System):
    """
    The system responsible for transformations.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        transform = components

        T = glm.translate(glm.mat4(1.0), glm.vec3(transform.translation.x, transform.translation.y, transform.translation.z))
        R = glm.quat(glm.vec3(glm.radians(transform.rotation.x), glm.radians(transform.rotation.y), glm.radians(transform.rotation.z)))
        S = glm.scale(glm.mat4(1.0), glm.vec3(transform.scale.x, transform.scale.y, transform.scale.z))

        transform.quaternion = R        
        transform.local_matrix = T * glm.mat4(R) * S
        transform.world_matrix = transform.local_matrix

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        transform = components

        if not transform.static:
            previous_local_matrix = transform.local_matrix

            T = glm.translate(glm.mat4(1.0), glm.vec3(transform.translation.x, transform.translation.y, transform.translation.z))
            R = glm.quat(glm.vec3(glm.radians(transform.rotation.x), glm.radians(transform.rotation.y), glm.radians(transform.rotation.z)))
            S = glm.scale(glm.mat4(1.0), glm.vec3(transform.scale.x, transform.scale.y, transform.scale.z))
            
            transform.quaternion = R
            transform.local_matrix = T * glm.mat4(R) * S
            transform.world_matrix = transform.local_matrix        

            if (np.array_equal(previous_local_matrix, transform.local_matrix)):
                transform.dirty = False
            else:
                transform.dirty = True
        else:
            transform.dirty = False