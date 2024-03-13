from pyGandalf.utilities.logger import logger

import trimesh
from pathlib import Path
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
    
    def build(cls, name: str, path: Path):
        filename = str(path)

        mesh: trimesh.Trimesh = trimesh.load(filename, force='mesh')

        vertices = np.asarray(mesh.vertices, dtype=np.float32)
        indices = np.asarray(mesh.faces, dtype=np.uint32)
        normals = np.asarray(mesh.vertex_normals, dtype=np.float32)
        texcoords = np.asarray(mesh.visual.uv, dtype=np.float32)

        cls.instance.meshes[name] = MeshInstance(name, vertices, indices, normals, texcoords)

        return

    def get(cls, name: str):
        return cls.instance.meshes[name]