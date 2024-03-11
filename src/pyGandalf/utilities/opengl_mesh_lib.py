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
        logger.debug(f"{filename}:")
        logger.debug(f"Vertices = {len(attrib.vertices)}")
        logger.debug(f"Normals = {len(attrib.normals)}")
        logger.debug(f"Texcoords = {len(attrib.texcoords)}")

        materials = reader.GetMaterials()
        logger.debug(f"Materials: {len(materials)}")
        for m in materials:
            logger.debug(m.name)
            logger.debug(m.diffuse)

        vertices = []
        normals = []
        texcoords = []

        shapes = reader.GetShapes()
        logger.debug(f"Shapes: {len(shapes)}")
        for shape in shapes:
            for index in shape.mesh.indices:
                if len(attrib.vertices) > 0:
                    vertices.append([attrib.vertices[index.vertex_index * 3 + 0], attrib.vertices[index.vertex_index * 3 + 1], attrib.vertices[index.vertex_index * 3 + 2]])
                if len(attrib.normals) > 0:
                    normals.append([attrib.normals[index.normal_index * 3 + 0], attrib.normals[index.normal_index * 3 + 1], attrib.normals[index.normal_index * 3 + 2]])
                if len(attrib.texcoords) > 0:
                    texcoords.append([attrib.texcoords[index.texcoord_index * 2 + 0], attrib.texcoords[index.texcoord_index * 2 + 1]])

        vertices = None if len(vertices) == 0 else np.asarray(vertices, dtype=np.float32)
        normals = None if len(normals) == 0 else np.asarray(normals, dtype=np.float32)
        texcoords = None if len(texcoords) == 0 else np.asarray(texcoords, dtype=np.float32)

        cls.instance.meshes[name] = MeshInstance(name, vertices, None, normals, texcoords)

    def get(cls, name: str):
        return cls.instance.meshes[name]