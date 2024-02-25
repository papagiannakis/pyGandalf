from scene.entity import Entity
from systems.system import System

import utilities.math as utils

import numpy as np

class TransformSystem(System):
    """
    The system responsible for transformations.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        transform = components

        T = utils.translate(transform.translation[0], transform.translation[1], transform.translation[2])
        R = utils.rotate((1, 0, 0), transform.rotation[0]) @ utils.rotate((0, 1, 0), transform.rotation[1]) @ utils.rotate((0, 0, 1), transform.rotation[2])
        S = utils.scale(transform.scale[0], transform.scale[1], transform.scale[2])
        
        transform.local_matrix = S @ R @ T

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        transform = components

        previous_local_matrix = transform.local_matrix
        
        T = utils.translate(transform.translation[0], transform.translation[1], transform.translation[2])
        R = utils.rotate((1, 0, 0), transform.rotation[0]) @ utils.rotate((0, 1, 0), transform.rotation[1]) @ utils.rotate((0, 0, 1), transform.rotation[2])
        S = utils.scale(transform.scale[0], transform.scale[1], transform.scale[2])
        
        transform.local_matrix = S @ R @ T
        transform.world_matrix = transform.local_matrix

        if (np.array_equal(previous_local_matrix, transform.local_matrix)):
            transform.is_dirty = False
        else:
            transform.is_dirty = True