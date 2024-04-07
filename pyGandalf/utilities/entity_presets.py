from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import *
from pyGandalf.scene.scene_manager import SceneManager

from pyGandalf.utilities.definitions import SHADERS_PATH
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData

import numpy as np

def create_empty() -> Entity:
    entity_empty = SceneManager().get_active_scene().enroll_entity()
    SceneManager().get_active_scene().add_component(entity_empty, InfoComponent('Empty Entity'))
    SceneManager().get_active_scene().add_component(entity_empty, TransformComponent())
    SceneManager().get_active_scene().add_component(entity_empty, LinkComponent())
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

    entity_plane = SceneManager().get_active_scene().enroll_entity()
    print(entity_plane.id)
    SceneManager().get_active_scene().add_component(entity_plane, InfoComponent('Plane'))
    SceneManager().get_active_scene().add_component(entity_plane, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(270, 0, 0), glm.vec3(1, 1, 1)))
    SceneManager().get_active_scene().add_component(entity_plane, LinkComponent())
    SceneManager().get_active_scene().add_component(entity_plane, StaticMeshComponent('plane_mesh', [vertices, normals, texture_coords]))
    SceneManager().get_active_scene().add_component(entity_plane, MaterialComponent('M_Plane'))
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

    entity_cube = SceneManager().get_active_scene().enroll_entity()
    print(entity_cube.id)
    SceneManager().get_active_scene().add_component(entity_cube, InfoComponent('Cube'))
    SceneManager().get_active_scene().add_component(entity_cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    SceneManager().get_active_scene().add_component(entity_cube, LinkComponent(None))
    SceneManager().get_active_scene().add_component(entity_cube, StaticMeshComponent('cube_mesh', [vertices, normals, texture_coords]))
    SceneManager().get_active_scene().add_component(entity_cube, MaterialComponent('M_Cube'))

    return entity_cube

def create_camera() -> Entity:
    entity_camera = SceneManager().get_active_scene().enroll_entity()
    print(entity_camera.id)
    SceneManager().get_active_scene().add_component(entity_camera, InfoComponent('Camera'))
    SceneManager().get_active_scene().add_component(entity_camera, TransformComponent(glm.vec3(0, 0, 10), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    SceneManager().get_active_scene().add_component(entity_camera, LinkComponent(None))
    SceneManager().get_active_scene().add_component(entity_camera, CameraComponent(45, 1.778, 0.1, 1000, 1.2, CameraComponent.Type.PERSPECTIVE))
    return entity_camera
