from src.scene.entity import Entity

import numpy as np

class InfoComponent:
    def __init__(self, name = 'UnnamedEntity'):
        self.tag = name
        self.enabled = True

class TransformComponent:
    def __init__(self, translation, rotation, scale):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

        self.local_matrix = np.identity(4)
        self.world_matrix = np.identity(4)

        self.is_dirty = True
        self.is_static = False

class LinkComponent:
    def __init__(self, parent: Entity):
        self.parent: Entity = parent

class RenderComponent:
    def __init__(self, attributes, indices):
        self.attributes = attributes
        self.indices = indices
        self.vao = 0
        self.vbo = []
        self.ebo = 0
        self.batch = -1

class MaterialComponent:
    def __init__(self, name):
        self.name = name
        self.instance = None