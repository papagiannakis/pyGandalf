from scene.entity import Entity
from systems.system import System

import utilities.math as utils

import numpy as np
import glm

class TransformSystem(System):
    """
    The system responsible for transformations.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        transform = components

        T = glm.translate(glm.mat4(1.0), glm.vec3(transform.translation.x, transform.translation.y, transform.translation.z))
        R = glm.quat(glm.vec3(glm.radians(transform.rotation.x), glm.radians(transform.rotation.y), glm.radians(transform.rotation.z)))
        S = glm.scale(glm.mat4(1.0), glm.vec3(transform.scale.x, transform.scale.y, transform.scale.z))

        transform.quaternion = R        
        transform.local_matrix = S * glm.mat4(R) * T

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        transform = components

        previous_local_matrix = transform.local_matrix

        T = glm.translate(glm.mat4(1.0), glm.vec3(transform.translation.x, transform.translation.y, transform.translation.z))
        R = glm.quat(glm.vec3(glm.radians(transform.rotation.x), glm.radians(transform.rotation.y), glm.radians(transform.rotation.z)))
        S = glm.scale(glm.mat4(1.0), glm.vec3(transform.scale.x, transform.scale.y, transform.scale.z))
        
        transform.quaternion = R
        transform.local_matrix = S * glm.mat4(R) * T
        transform.world_matrix = transform.local_matrix

        if (np.array_equal(previous_local_matrix, transform.local_matrix)):
            transform.is_dirty = False
        else:
            transform.is_dirty = True