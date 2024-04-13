from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import *
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager

from pyGandalf.utilities.definitions import SHADERS_PATH
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData

import numpy as np

def create_empty() -> Entity:
    scene: Scene = SceneManager().get_active_scene()
    entity_empty = scene.enroll_entity()
    scene.add_component(entity_empty, InfoComponent('Empty Entity'))
    scene.add_component(entity_empty, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_empty, LinkComponent(None))
    return entity_empty

def create_plane() -> Entity:
    vertices = np.array([
        [-0.5, -0.5, 0.0], #0
        [ 0.5, -0.5, 0.0], #1
        [ 0.5,  0.5, 0.0], #2
        [ 0.5,  0.5, 0.0], #2
        [-0.5,  0.5, 0.0], #3
        [-0.5, -0.5, 0.0]  #0
    ], dtype=np.float32)

    texture_coords = np.array([
        [0.0, 1.0], #0
        [1.0, 1.0], #1
        [1.0, 0.0], #2
        [1.0, 0.0], #2
        [0.0, 0.0], #3
        [0.0, 1.0]  #0
    ], dtype=np.float32)

    normals = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0] 
    ], dtype=np.float32)

    lit_blinn_phong_vertex = OpenGLShaderLib().load_from_file(SHADERS_PATH/'lit_blinn_phong_vertex.glsl')
    lit_blinn_phong_fragment = OpenGLShaderLib().load_from_file(SHADERS_PATH/'lit_blinn_phong_fragment.glsl')

    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLShaderLib().build('default_mesh', lit_blinn_phong_vertex, lit_blinn_phong_fragment)
    OpenGLMaterialLib().build('M_Plane', MaterialData('default_mesh', ['white_texture']))

    scene: Scene = SceneManager().get_active_scene()

    entity_plane = scene.enroll_entity()
    scene.add_component(entity_plane, InfoComponent('Plane'))
    scene.add_component(entity_plane, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(270, 0, 0), glm.vec3(10, 10, 10)))
    scene.add_component(entity_plane, LinkComponent(None))
    scene.add_component(entity_plane, StaticMeshComponent('plane_mesh', [vertices, normals, texture_coords]))
    scene.add_component(entity_plane, MaterialComponent('M_Plane'))
    return entity_plane

def create_cube() -> Entity:
    vertices = np.array([
        [-1.0, -1.0, -1.0],
        [-1.0, -1.0,  1.0],
        [-1.0,  1.0,  1.0],

        [1.0,  1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [-1.0,  1.0, -1.0],

        [1.0, -1.0,  1.0],
        [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0],

        [1.0,  1.0, -1.0],
        [1.0, -1.0, -1.0],
        [-1.0, -1.0, -1.0],

        [-1.0, -1.0, -1.0],
        [-1.0,  1.0,  1.0],
        [-1.0,  1.0, -1.0],

        [1.0, -1.0,  1.0],
        [-1.0, -1.0,  1.0],
        [-1.0, -1.0, -1.0],

        [-1.0,  1.0,  1.0],
        [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0],

        [1.0,  1.0,  1.0],
        [1.0, -1.0, -1.0],
        [1.0,  1.0, -1.0],

        [1.0, -1.0, -1.0],
        [1.0,  1.0,  1.0],
        [1.0, -1.0,  1.0],

        [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0],
        [-1.0,  1.0, -1.0],

        [1.0,  1.0,  1.0],
        [-1.0,  1.0, -1.0],
        [-1.0,  1.0,  1.0],

        [1.0,  1.0,  1.0],
        [-1.0,  1.0,  1.0],
        [1.0, -1.0,  1.0]
    ], dtype=np.float32)

    normals = np.zeros_like(vertices)
    for i in range(0, len(vertices), 3):
        v1 = vertices[i]
        v2 = vertices[i+1]
        v3 = vertices[i+2]
        edge1 = v2 - v1
        edge2 = v3 - v1
        normal = np.cross(edge1, edge2)
        normal /= np.linalg.norm(normal)
        for j in range(3):
            normals[i+j] = normal

    texture_coords = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0], #

        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0], #

        [0.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],

        [0.0, 1.0],
        [0.0, 0.0],
        [1.0, 0.0], #

        [0.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0], #

        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],

        [0.0, 1.0],
        [0.0, 0.0],
        [1.0, 0.0], #

        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0], #

        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 0.0], #

        [1.0, 0.0],
        [1.0, 1.0], #
        [0.0, 1.0],

        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 0.0], #

        [1.0, 1.0],
        [0.0, 1.0],
        [1.0, 0.0], #
    ], dtype=np.float32)

    lit_blinn_phong_vertex = OpenGLShaderLib().load_from_file(SHADERS_PATH/'lit_blinn_phong_vertex.glsl')
    lit_blinn_phong_fragment = OpenGLShaderLib().load_from_file(SHADERS_PATH/'lit_blinn_phong_fragment.glsl')

    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLShaderLib().build('default_mesh', lit_blinn_phong_vertex, lit_blinn_phong_fragment)
    OpenGLMaterialLib().build('M_Cube', MaterialData('default_mesh', ['white_texture']))

    scene: Scene = SceneManager().get_active_scene()

    entity_cube = scene.enroll_entity()
    scene.add_component(entity_cube, InfoComponent('Cube'))
    scene.add_component(entity_cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_cube, LinkComponent(None))
    scene.add_component(entity_cube, StaticMeshComponent('cube_mesh', [vertices, normals, texture_coords]))
    scene.add_component(entity_cube, MaterialComponent('M_Cube'))

    return entity_cube

def create_camera() -> Entity:
    scene: Scene = SceneManager().get_active_scene()
    entity_camera = scene.enroll_entity()
    scene.add_component(entity_camera, InfoComponent('Camera'))
    scene.add_component(entity_camera, TransformComponent(glm.vec3(0, 0, 10), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_camera, LinkComponent(None))
    scene.add_component(entity_camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    return entity_camera

def create_light() -> Entity:
    scene: Scene = SceneManager().get_active_scene()
    entity_light = scene.enroll_entity()
    scene.add_component(entity_light, InfoComponent('Light'))
    scene.add_component(entity_light, TransformComponent(glm.vec3(0, 5, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_light, LinkComponent(None))
    scene.add_component(entity_light, LightComponent(glm.vec3(1, 1, 1), 0.75))
    return entity_light
