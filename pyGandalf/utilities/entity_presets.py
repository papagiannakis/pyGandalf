from pyGandalf.scene.entity import Entity
from pyGandalf.scene.components import *
from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager

from pyGandalf.utilities.definitions import SHADERS_PATH
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureData
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData, MaterialDescriptor

import numpy as np
import OpenGL.GL as gl

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

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh_plane', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Plane', MaterialData('default_mesh_plane', ['white_texture']))

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

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh_cube', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Cube', MaterialData('default_mesh_cube', ['white_texture']))

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
    scene.add_component(entity_light, TransformComponent(glm.vec3(0, 2, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_light, LinkComponent(None))
    scene.add_component(entity_light, LightComponent(glm.vec3(1, 1, 1), 0.75))
    return entity_light

def create_sphere() -> Entity:
    positions = []
    uv = []
    normals = []
    indices = []

    X_SEGMENTS = 64
    Y_SEGMENTS = 64

    for x in range(X_SEGMENTS + 1):
        for y in range(Y_SEGMENTS + 1):
            xSegment = float(x) / float(X_SEGMENTS)
            ySegment = float(y) / float(Y_SEGMENTS)
            xPos = np.cos(xSegment * 2.0 * np.pi) * np.sin(ySegment * np.pi)
            yPos = np.cos(ySegment * np.pi)
            zPos = np.sin(xSegment * 2.0 * np.pi) * np.sin(ySegment * np.pi)

            positions.append([xPos, yPos, zPos])
            uv.append([xSegment, ySegment])
            normals.append([xPos, yPos, zPos])

    oddRow = False
    for y in range(Y_SEGMENTS):
        if not oddRow:  # even rows: y == 0, y == 2; and so on
            for x in range(X_SEGMENTS + 1):
                indices.append(y * (X_SEGMENTS + 1) + x)
                indices.append((y + 1) * (X_SEGMENTS + 1) + x)
        else:
            for x in range(X_SEGMENTS, -1, -1):
                indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                indices.append(y * (X_SEGMENTS + 1) + x)
        oddRow = not oddRow

    vertices = np.asarray(positions, dtype=np.float32)
    uvs = np.asarray(uv, dtype=np.float32)
    normals = np.asarray(normals, dtype=np.float32)
    indices = np.asarray(indices, dtype=np.uint32)

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh_sphere', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Sphere', MaterialData('default_mesh_sphere', ['white_texture']), MaterialDescriptor(primitive=gl.GL_TRIANGLE_STRIP))

    scene: Scene = SceneManager().get_active_scene()

    entity_sphere = scene.enroll_entity()
    scene.add_component(entity_sphere, InfoComponent('Sphere'))
    scene.add_component(entity_sphere, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_sphere, LinkComponent(None))
    scene.add_component(entity_sphere, StaticMeshComponent('sphere_mesh', [vertices, normals, uvs], indices))
    scene.add_component(entity_sphere, MaterialComponent('M_Sphere'))

    return entity_sphere

def create_cylinder() -> Entity:
    vertices = []
    indices = []
    normals = []
    texture_coords = []

    for i in range(0, 20):
        for j in range(0, 20):
            x = np.cos(2 * np.pi * j / 20)
            y = np.sin(2 * np.pi * j / 20)
            z = 2 * i / 20 - 1

            vertices.append([x, y, z])
            normals.append([x, y, 0])
            texture_coords.append([j / 20.0, i / 20.0])
    
    for i in range(0, 20):
        for j in range(0, 20):
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + (j + 1) % 20)

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Cylinder', MaterialData('default_mesh', ['white_texture']))

    scene: Scene = SceneManager().get_active_scene()

    entity_cylinder = scene.enroll_entity()
    scene.add_component(entity_cylinder, InfoComponent('Cylinder'))
    scene.add_component(entity_cylinder, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_cylinder, LinkComponent(None))
    scene.add_component(entity_cylinder, StaticMeshComponent('cylinder_mesh', [np.asarray(vertices, dtype=np.float32), np.asarray(normals, dtype=np.float32), np.asarray(texture_coords, dtype=np.float32)], np.asarray(indices, dtype=np.uint32)))
    scene.add_component(entity_cylinder, MaterialComponent('M_Cylinder'))

    return entity_cylinder

def create_cone() -> Entity:
    vertices = []
    indices = []
    normals = []
    texture_coords = []

    for i in range(0, 20):
        for j in range(0, 20):
            x = np.cos(2 * np.pi * j / 20) * (1 - i / 20)
            y = np.sin(2 * np.pi * j / 20) * (1 - i / 20)
            z = 2 * i / 20 - 1

            vertices.append([x, y, z])
            normals.append([x, y, 0])
            texture_coords.append([j / 20.0, i / 20.0])

    for i in range(0, 20):
        for j in range(0, 20):
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + (j + 1) % 20)

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Cone', MaterialData('default_mesh', ['white_texture']))

    scene: Scene = SceneManager().get_active_scene()

    entity_cone = scene.enroll_entity()
    scene.add_component(entity_cone, InfoComponent('Cone'))
    scene.add_component(entity_cone, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_cone, LinkComponent(None))
    scene.add_component(entity_cone, StaticMeshComponent('cone_mesh', [np.asarray(vertices, dtype=np.float32), np.asarray(normals, dtype=np.float32), np.asarray(texture_coords, dtype=np.float32)], np.asarray(indices, dtype=np.uint32)))
    scene.add_component(entity_cone, MaterialComponent('M_Cone'))

    return entity_cone

def create_torus() -> Entity:
    vertices = []
    indices = []
    normals = []
    texture_coords = []

    for i in range(0, 21):
        for j in range(0, 21):
            x = np.cos(2 * np.pi * j / 20) * (1 + np.cos(2 * np.pi * i / 20) / 2)
            y = np.sin(2 * np.pi * j / 20) * (1 + np.cos(2 * np.pi * i / 20) / 2)
            z = np.sin(2 * np.pi * i / 20) / 2

            vertices.append([x, y, z])
            normals.append([x, y, z])
            texture_coords.append([j / 20.0, i / 20.0])

    for i in range(0, 20):
        for j in range(0, 20):
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + j)
            indices.append((i + 1) * 20 + (j + 1) % 20)
            indices.append(i * 20 + (j + 1) % 20)

    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
    OpenGLMaterialLib().build('M_Torus', MaterialData('default_mesh', ['white_texture']))

    scene: Scene = SceneManager().get_active_scene()

    entity_torus = scene.enroll_entity()
    scene.add_component(entity_torus, InfoComponent('Torus'))
    scene.add_component(entity_torus, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity_torus, LinkComponent(None))
    scene.add_component(entity_torus, StaticMeshComponent('torus_mesh', [np.asarray(vertices, dtype=np.float32), np.asarray(normals, dtype=np.float32), np.asarray(texture_coords, dtype=np.float32)], np.asarray(indices, dtype=np.uint32)))
    scene.add_component(entity_torus, MaterialComponent('M_Torus'))

    return entity_torus