from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.definitions import MODELS_PATH

import numpy as np
import trimesh
from pxr import Usd, UsdGeom
# import kaolin

import os
from pathlib import Path

class MeshInstance:
    def __init__(self, name, path, vertices, indices, normals, texcoords):
        self.name = name
        self.path = path
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

        mesh = None
        vertices = None
        indices = None
        normals = None
        texcoords = None

        if '.usd' in path.name:
            # kaolin.io.usd.import_mesh(filename, with_normals=True)
            # mesh: kaolin.rep.SurfaceMesh = kaolin.io.usd.import_mesh(filename, with_normals=True)
            stage = Usd.Stage.Open(filename)
            flattened_stage = stage.Flatten().ExportToString()
            logger.debug(flattened_stage)

            meshes, face_vertex_count = cls.instance._parse_usd(name, filename)
            mesh: MeshInstance = meshes[0]

            vertices = np.asarray(mesh.vertices, dtype=np.float32)

            if face_vertex_count == 3:
                indices = np.asarray(mesh.indices, dtype=np.uint32).reshape(-1, 3)
            elif face_vertex_count == 4:
                result = []
                indices = np.asarray(mesh.indices, dtype=np.uint32)
                for i in range(0, len(indices), 4):
                    sub_array = indices[i:i+4]
                    extracted_elements = np.array([
                        [sub_array[0], sub_array[1], sub_array[2]],
                        [sub_array[2], sub_array[3], sub_array[0]]
                    ])
                    result.extend(extracted_elements)
                indices = np.array(result)

            normals = np.asarray(mesh.normals, dtype=np.float32)
            texcoords = np.asarray(mesh.texcoords, dtype=np.float32)
        else:
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
    
    def _parse_usd(cls, name, file_path):
        logger.debug(file_path)
        stage = Usd.Stage.Open(file_path)

        submeshes: list[MeshInstance] = []

        # Iterate over all prims in the stage
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(prim)

                # Get vertices
                points_attr = mesh.GetPointsAttr()
                vertices = np.array(points_attr.Get(), dtype=np.float32)

                face_vertex_count_attr = mesh.GetFaceVertexCountsAttr()
                face_vertex_count = np.array(face_vertex_count_attr.Get(), dtype=np.uint32)[0] if face_vertex_count_attr else 0

                # Get vertex indices (faces) if available
                indices_attr = mesh.GetFaceVertexIndicesAttr()
                indices = np.array(indices_attr.Get(), dtype=np.uint32) if indices_attr else None

                # Get normals if available
                normals_attr = mesh.GetNormalsAttr()
                normals = np.array(normals_attr.Get(), dtype=np.float32) if normals_attr else None

                # Get UVs if available
                uvs = None
                primvar_names = prim.GetAttributes()
                for primvar in primvar_names:
                    if primvar.GetTypeName() == 'texCoord2f[]':
                        uvs = np.array(primvar.Get(), dtype=np.float32)

                submeshes.append(MeshInstance(name, file_path, vertices, indices, normals, uvs))
    
        return submeshes, face_vertex_count