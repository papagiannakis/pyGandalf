from pyGandalf.scene.entity import Entity

from enum import Enum
import glm

class InfoComponent:
    def __init__(self, name = 'UnnamedEntity'):
        self.tag = name
        self.enabled = True

class TransformComponent:
    def __init__(self, translation : glm.vec3, rotation : glm.vec3, scale : glm.vec3):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)
        self.quaternion = glm.quat()

        self.is_dirty = True
        self.is_static = False

class LinkComponent:
    def __init__(self, parent: Entity):
        self.parent: Entity = parent

class OpenGLRenderComponent:
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

class CameraComponent:
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
            self.projection = glm.perspective(self.fov, self.aspect_ratio, self.near, self.far)
        self.view_projection = glm.mat4(1.0)

        self.primary = primary
        self.static = static

class StaticMeshComponent:
    def __init__(self, name, attributes = None, indices = None):
        self.name = name
        self.attributes = attributes
        self.indices = indices
        self.vao = 0
        self.vbo = []
        self.ebo = 0
        self.batch = -1
