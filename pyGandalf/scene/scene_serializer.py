from pyGandalf.scene.scene import Scene
from pyGandalf.scene.components import Component, InfoComponent
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureData
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.usd_utilities import USDUtilities

import inspect
from pxr import Usd, UsdGeom, Sdf, Gf
from pathlib import Path

class SceneSerializer:
    def __init__(self, scene: Scene) -> None:
        self.scene : Scene = scene
        self.stage : Usd.Stage = None
                
    def serialize(self, path: Path):
        self.stage = Usd.Stage.CreateNew(str(path))
        self.stage.DefinePrim("/Hierachy")

        for entity in self.scene.get_entities():
            name : str = ""
            if self.scene.has_component(entity, InfoComponent):
                info_component : InfoComponent = self.scene.get_component(entity, InfoComponent)
                name = info_component.tag
            else:
                logger.critical(f'Cannot serialize entity: {entity.id}, no InfoComponent is present')
                continue

            entity_prim = self.stage.DefinePrim("/Hierachy/" + name)
            entity_prim_id = entity_prim.CreateAttribute("id", Sdf.ValueTypeNames.String)
            entity_prim_id.Set(entity.id.hex)
            entity_prim_enabled = entity_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool)
            entity_prim_enabled.Set(entity.enabled)

            for cls in Component.__subclasses__():
                if self.scene.has_component(entity, cls):

                    component = self.scene.get_component(entity, cls)

                    entity_component_prim = self.stage.DefinePrim("/Hierachy/" + name + "/" + cls.__name__)

                    # getmembers() returns all the members of an object 
                    for i in inspect.getmembers(component):                        
                        # to remove private and protected functions
                        if not i[0].startswith('_'):                            
                            # To remove other methods that does not start with a underscore
                            if not inspect.ismethod(i[1]):
                                usd_type = USDUtilities().convert_type(type(i[1]))

                                if usd_type == None:
                                    continue
                                
                                entity_prim_attribute = entity_component_prim.CreateAttribute(i[0], usd_type)
                                entity_prim_attribute.Set(USDUtilities().convert_value(i[1]))

        self.stage.DefinePrim("/Systems")

        for system in self.scene.get_systems():
            system_prim = self.stage.DefinePrim("/Systems/" + type(system).__name__)

            system_prim_name = system_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            system_prim_name.Set(type(system).__name__)

            filters = []
            for filter in system.filters:
                filters.append(filter.__name__)

            system_prim_filters = system_prim.CreateAttribute("filters", Sdf.ValueTypeNames.StringArray)
            system_prim_filters.Set(filters)

        self.stage.DefinePrim("/Textures")

        for texture in OpenGLTextureLib().get_textures().values():
            texture_prim = self.stage.DefinePrim("/Textures/" + texture.name)

            texture_prim_id = texture_prim.CreateAttribute("id", Sdf.ValueTypeNames.Int)
            texture_prim_id.Set(int(texture.id))

            texture_prim_slot = texture_prim.CreateAttribute("slot", Sdf.ValueTypeNames.Float)
            texture_prim_slot.Set(float(texture.slot))

            texture_prim_name = texture_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            texture_prim_name.Set(texture.name)

            texture_prim_path = texture_prim.CreateAttribute("path", Sdf.ValueTypeNames.String)
            texture_prim_path.Set(str('') if texture.path is None else str(texture.path))

            dimension = Gf.Vec2i(-1, -1)
            if texture.data is not None:
                dimension = Gf.Vec2i(texture.data[1], texture.data[2])                

            texture_prim_dimensions = texture_prim.CreateAttribute("dimensions", Sdf.ValueTypeNames.Int2)
            texture_prim_dimensions.Set(dimension)

            data = []
            if texture.data is not None:
                data = [byte for byte in texture.data[0]]

            texture_prim_dimensions = texture_prim.CreateAttribute("data", Sdf.ValueTypeNames.IntArray)
            texture_prim_dimensions.Set(data)

        self.stage.DefinePrim("/Shaders")

        for shader in OpenGLShaderLib().get_shaders().values():
            shader_prim = self.stage.DefinePrim("/Shaders/" + shader.name)

            shader_prim_id = shader_prim.CreateAttribute("shader_program", Sdf.ValueTypeNames.Int)
            shader_prim_id.Set(int(shader.shader_program))

            shader_prim_name = shader_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            shader_prim_name.Set(shader.name)

            shader_prim_vs_path = shader_prim.CreateAttribute("vs_path", Sdf.ValueTypeNames.String)
            shader_prim_vs_path.Set(str(shader.vs_path))

            shader_prim_fs_path = shader_prim.CreateAttribute("fs_path", Sdf.ValueTypeNames.String)
            shader_prim_fs_path.Set(str(shader.fs_path))

        self.stage.DefinePrim("/Materials")

        for material in OpenGLMaterialLib().get_materials().values():
            material_prim = self.stage.DefinePrim("/Materials/" + material.name)

            material_prim_name = material_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            material_prim_name.Set(material.name)

            material_prim_shader_program = material_prim.CreateAttribute("shader_program", Sdf.ValueTypeNames.Int)
            material_prim_shader_program.Set(material.shader_program)

            material_prim_textures = material_prim.CreateAttribute("textures", Sdf.ValueTypeNames.StringArray)
            material_prim_textures.Set(material.textures)

        self.stage.DefinePrim("/Meshes")

        for mesh in OpenGLMeshLib().get_meshes().values():
            mesh_prim = self.stage.DefinePrim("/Meshes/" + mesh.name)

            mesh_prim_name = mesh_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            mesh_prim_name.Set(mesh.name)

            mesh_prim_path = mesh_prim.CreateAttribute("path", Sdf.ValueTypeNames.String)
            mesh_prim_path.Set(str(mesh.path))

        self.stage.GetRootLayer().Save()

    def deserialize(self, path: Path):
        self.stage: Usd.Stage = Usd.Stage.Open(str(path))

        # Get the root prim of the stage
        root_prim = self.stage.GetPseudoRoot()

        # Traverse all prims in the stage
        all_prims = []
        for prim in Usd.PrimRange(root_prim):
            all_prims.append(prim)
            print("Prim Path:", prim.GetPath())

            # Print information about each attribute
            for attribute in prim.GetAttributes():
                print("\tAttribute Name:", attribute.GetName())
                print("\tAttribute Type:", attribute.GetTypeName())
                print("\tAttribute Value:", attribute.Get())
                print("\t")