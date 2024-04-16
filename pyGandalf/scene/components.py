from pyGandalf.scene.entity import Entity

import glm

from enum import Enum

class Component(object):
    pass

class InfoComponent(Component):
    def __init__(self, tag = 'UnnamedEntity'):
        self.tag = tag
        self.enabled = True

class TransformComponent(Component):
    def __init__(self, translation: glm.vec3, rotation: glm.vec3, scale: glm.vec3):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)
        self.quaternion = glm.quat()

        self.dirty = True
        self.static = False
    
    def get_world_position(self):
        return (self.world_matrix * glm.vec4(self.translation, 1.0)).xyz

class LinkComponent(Component):
    def __init__(self, parent: Entity):
        self.parent_id = 0
        if parent != None:
            self.parent_id = parent.id
        self.parent: Entity = parent
        self.prev_parent: Entity = parent
        self.children: list[Entity] = []

class MaterialComponent(Component):
    def __init__(self, name, color = glm.vec3(1.0, 1.0, 1.0)):
        self.name = name
        self.instance = None
        self.color = color
        self.glossiness = 5.0
        self.metallicness = 0.0

class CameraComponent(Component):
    class Type(Enum):
        PERSPECTIVE = 1
        ORTHOGRAPHIC = 2

    def __init__(self, fov, aspect_ratio, near, far, zoom_level, type: Type, primary = True, static = False):
        self.zoom_level = zoom_level
        self.fov = fov
        self.near = near
        self.far = far
        self.aspect_ratio = aspect_ratio
        self.type: CameraComponent.Type = type

        self.view = glm.mat4(1.0)
        if type is CameraComponent.Type.ORTHOGRAPHIC:
            self.projection = glm.ortho(-self.aspect_ratio * self.zoom_level, self.aspect_ratio * self.zoom_level, -self.zoom_level, self.zoom_level, self.near, self.far)
        elif type is CameraComponent.Type.PERSPECTIVE:
            self.projection = glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)
        self.view_projection = glm.mat4(1.0)

        self.primary = primary
        self.static = static

class StaticMeshComponent(Component):
    def __init__(self, name, attributes = None, indices = None, primitive = None):
        self.name = name
        self.attributes = attributes
        self.indices = indices
        self.primitive = primitive
        self.vao = 0
        self.vbo = []
        self.ebo = 0
        self.batch = -1

class LightComponent(Component):
    def __init__(self, color, intensity, static = True):
        self.color = color
        self.intensity = intensity
        self.static = static
