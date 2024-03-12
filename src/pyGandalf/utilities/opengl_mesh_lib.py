from pyGandalf.utilities.logger import logger

import sys
import tinyobjloader

import numpy as np

class MeshInstance:
    def __init__(self, name, vertices, indices, normals, texcoords):
        self.name = name
        self.handle = None
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.texcoords = texcoords

class OpenGLMeshLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLMeshLib, cls).__new__(cls)
            cls.instance.meshes: dict[str, MeshInstance] = {} # type: ignore
        return cls.instance
    
    def build(cls, name: str, path):
        # Create reader.
        reader = tinyobjloader.ObjReader()

        filename = str(path)

        # Load .obj(and .mtl) using default configuration
        ret = reader.ParseFromFile(filename)

        if ret == False:
            logger.warn(reader.Warning())
            logger.error(reader.Error())
            logger.error(f"Failed to load: {filename}")
            return

        if reader.Warning():
            logger.warn(reader.Warning())

        attrib = reader.GetAttrib()

        vertices_length = len(attrib.vertices)
        normals_length = len(attrib.normals)
        texcoords_length = len(attrib.texcoords)

        logger.debug(f"{filename}:")
        logger.debug(f"Vertices = {vertices_length}")
        logger.debug(f"Normals = {normals_length}")
        logger.debug(f"Texcoords = {texcoords_length}")

        materials = reader.GetMaterials()
        logger.debug(f"Materials: {len(materials)}")
        for m in materials:
            logger.debug(m.name)
            logger.debug(m.diffuse)

        shapes = reader.GetShapes()

        length = 0

        for shape in shapes:
            length += len(shape.mesh.indices)

        vertices = np.zeros((length, 3), dtype=np.float32)
        normals = np.zeros((length, 3), dtype=np.float32)
        texcoords = np.zeros((length, 2), dtype=np.float32)

        logger.debug(f"Shapes: {len(shapes)}")

        i = 0

        for shape in shapes:
            for index in shape.mesh.indices:
                if vertices_length > 0:
                    vertices[i] = attrib.vertices[index.vertex_index * 3: index.vertex_index * 3 + 3]
                if normals_length > 0:
                    normals[i] = attrib.normals[index.normal_index * 3: index.normal_index * 3 + 3]
                if texcoords_length > 0:
                    texcoords[i] = attrib.texcoords[index.texcoord_index * 2: index.texcoord_index * 2 + 2]
                i += 1

        vertices = None if np.all(vertices == 0) else vertices
        normals = None if np.all(normals == 0) else normals
        texcoords = None if np.all(texcoords == 0) else texcoords

        cls.instance.meshes[name] = MeshInstance(name, vertices, None, normals, texcoords)

    def get(cls, name: str):
        return cls.instance.meshes[name]