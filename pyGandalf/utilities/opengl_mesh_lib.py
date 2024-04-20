from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.definitions import MODELS_PATH

import numpy as np
import trimesh

import os
from pathlib import Path

class MeshInstance:
    def __init__(self, name, path, vertices, indices, normals, texcoords):
        self.name = name
        self.path = path
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
            cls.instance.meshes_names: dict[str, str] = {} # type: ignore
        return cls.instance
    
    def build(cls, name: str, path: Path):
        filename = str(path)

        if cls.instance.meshes.get(filename) != None:
            return cls.instance.meshes[filename]

        mesh: trimesh.Trimesh = trimesh.load(filename, force='mesh')

        vertices = np.asarray(mesh.vertices, dtype=np.float32)
        indices = np.asarray(mesh.faces, dtype=np.uint32)
        normals = np.asarray(mesh.vertex_normals, dtype=np.float32)
        texcoords = np.asarray(mesh.visual.uv, dtype=np.float32)

        rel_path = Path(os.path.relpath(path, MODELS_PATH))

        cls.instance.meshes_names[name] = filename
        cls.instance.meshes[filename] = MeshInstance(name, rel_path, vertices, indices, normals, texcoords)

        return cls.instance.meshes[filename]

    def get(cls, name: str) -> MeshInstance | None:
        if name not in cls.instance.meshes_names.keys():
            return None
        
        filename = cls.instance.meshes_names[name]

        if filename not in cls.instance.meshes.keys():
            return None
        
        return cls.instance.meshes[filename]
    
    def get_meshes(cls) -> dict[str, MeshInstance]:
        return cls.instance.meshes