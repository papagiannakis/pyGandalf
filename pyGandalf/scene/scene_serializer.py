from pyGandalf.core.application import Application
from pyGandalf.scene.scene import Scene
from pyGandalf.systems.system import System
from pyGandalf.scene.components import Component

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureInstance, TextureData
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.mesh_lib import MeshLib
from pyGandalf.utilities.component_lib import ComponentLib

from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.definitions import TEXTURES_PATH, SHADERS_PATH, MODELS_PATH
from pyGandalf.utilities.usd_serializer import USDSerializer

import glm
from pxr import Usd, UsdGeom, Sdf, Gf

import uuid
import inspect
from pathlib import Path

class SceneSerializer:
    def __init__(self, scene: Scene) -> None:
        self.scene : Scene = scene
        self.stage : Usd.Stage = None
                
    def serialize(self, path: Path):
        self.stage = Usd.Stage.CreateNew(str(path))
        self.stage.DefinePrim("/Hierachy")

        for entity in self.scene.get_entities():
            entity_prim = self.stage.DefinePrim("/Hierachy/" + "Entity" + entity.id.hex)
            entity_prim_id = entity_prim.CreateAttribute("id", Sdf.ValueTypeNames.String)
            entity_prim_id.Set(entity.id.hex)
            entity_prim_enabled = entity_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool)
            entity_prim_enabled.Set(entity.enabled)

            for cls in Component.__subclasses__():
                if self.scene.has_component(entity, cls):
                    component = self.scene.get_component(entity, cls)

                    entity_component_prim = self.stage.DefinePrim("/Hierachy/" + "Entity" + entity.id.hex + "/" + cls.__name__)

                    if hasattr(component, "custom_serialization"):
                        entity_component_prim = USDSerializer().serialize(entity_component_prim, component)
                    else:
                        entity_prim_args = entity_component_prim.CreateAttribute("dict", Sdf.ValueTypeNames.String)
                        entity_prim_args.Set(str(USDSerializer().to_json(component)))

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

            texture_prim_data = texture_prim.CreateAttribute("data", Sdf.ValueTypeNames.String)
            texture_prim_data.Set(str(USDSerializer().to_json(texture.data)))

            texture_prim_descriptor = texture_prim.CreateAttribute("descriptor", Sdf.ValueTypeNames.String)
            texture_prim_descriptor.Set(str(USDSerializer().to_json(texture.descriptor)))

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

            shader_prim_tcs_path = shader_prim.CreateAttribute("tcs_path", Sdf.ValueTypeNames.String)
            shader_prim_tcs_path.Set('' if shader.tcs_path == None else str(shader.tcs_path))

            shader_prim_tes_path = shader_prim.CreateAttribute("tes_path", Sdf.ValueTypeNames.String)
            shader_prim_tes_path.Set('' if shader.tes_path == None else str(shader.tes_path))

        self.stage.DefinePrim("/Materials")

        for material in OpenGLMaterialLib().get_materials().values():
            material_prim = self.stage.DefinePrim("/Materials/" + material.name)

            material_prim_name = material_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            material_prim_name.Set(material.name)

            material_prim_base_template = material_prim.CreateAttribute("base_template", Sdf.ValueTypeNames.String)
            material_prim_base_template.Set(material.data.base_template)

            material_prim_textures = material_prim.CreateAttribute("textures", Sdf.ValueTypeNames.StringArray)
            material_prim_textures.Set(material.data.textures)

            material_prim_textures = material_prim.CreateAttribute("color", Sdf.ValueTypeNames.Color4f)
            material_prim_textures.Set(Gf.Vec4f(material.data.color.r, material.data.color.g, material.data.color.b, material.data.color.a))

            material_prim_textures = material_prim.CreateAttribute("glossiness", Sdf.ValueTypeNames.Float)
            material_prim_textures.Set(float(material.data.glossiness))

            material_prim_descriptor = material_prim.CreateAttribute("descriptor", Sdf.ValueTypeNames.String)
            material_prim_descriptor.Set(str(USDSerializer().to_json(material.descriptor)))

        self.stage.DefinePrim("/Meshes")

        for mesh in MeshLib().get_meshes().values():
            mesh_prim = self.stage.DefinePrim("/Meshes/" + mesh.name)

            mesh_prim_name = mesh_prim.CreateAttribute("name", Sdf.ValueTypeNames.String)
            mesh_prim_name.Set(mesh.name)

            mesh_prim_path = mesh_prim.CreateAttribute("path", Sdf.ValueTypeNames.String)
            mesh_prim_path.Set(str(mesh.path))

        self.stage.DefinePrim("/Renderer")
        shadows_prim = self.stage.DefinePrim("/Renderer/" + "Shadows")
        shadows_prim_enabled = shadows_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool)
        shadows_prim_enabled.Set(OpenGLRenderer().get_shadows_enabled())

        self.stage.DefinePrim("/Decorators")
        components_prim = self.stage.DefinePrim("/Decorators/" + "Components")
        decorated_component_prim = components_prim.CreateAttribute('dict', Sdf.ValueTypeNames.String)
        decorated_component_prim.Set(str(USDSerializer().to_json(ComponentLib().Decorators)))

        self.stage.GetRootLayer().Save()

    def deserialize(self, path: Path):
        # Set the application running to false to prevent the newly created components
        # to call the on_create of the sytems that they are involved in.
        Application().set_is_running(False)

        self.stage: Usd.Stage = Usd.Stage.Open(str(path))

        # Get the root prim of the stage
        root_prim = self.stage.GetPseudoRoot()

        # Traverse all Hierachy prims in the stage
        entity_prims = []
        entity_id_attrs = []
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Hierachy' in str(prim_path):
                prims = str(prim_path).split('/')
                if len(prims) == 3:
                    entity_prims.append(prim)
                    entity_id_attrs.append(prim.GetAttribute("id").Get())

        for i, prim in enumerate(entity_prims):
            entity = self.scene.enroll_entity_with_uuid(uuid.UUID(entity_id_attrs[i]))
            for index, component_prim in enumerate(Usd.PrimRange(prim)):
                # Skip entity prim
                if index == 0:
                    continue

                prim_path: Path = component_prim.GetPath()
                
                for cls in Component.__subclasses__():
                    if component_prim.GetName() == cls.__name__:
                        component = None
                        if self.has_custom_serialization(cls):
                            component = USDSerializer().deserialize(component_prim, cls)
                        else:
                            component = USDSerializer().from_json(str(component_prim.GetAttribute("dict").Get()))

                        self.scene.add_component(entity, component)
                        break
        
        # Traverse all Systems prims in the stage
        skip_first_system_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Systems' in str(prim_path):
                # Skip the system prim
                if skip_first_system_prim:
                    skip_first_system_prim = False
                    continue

                name_attr = prim.GetAttribute("name").Get()

                components = []
                filters_attr = prim.GetAttribute("filters").Get()
                for filter in filters_attr:
                    for cls in Component.__subclasses__():
                        if filter == cls.__name__:
                            components.append(cls)
                            break

                for cls in System.__subclasses__():
                    if name_attr == cls.__name__:
                        self.scene.register_system(cls(components))
                        break
        
        # Traverse all Textures prims in the stage
        skip_first_texture_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Textures' in str(prim_path):
                # Skip the texture prim
                if skip_first_texture_prim:
                    skip_first_texture_prim = False
                    continue

                name_attr = str(prim.GetAttribute("name").Get())
                path_attr = prim.GetAttribute("path").Get()

                descriptor = USDSerializer().from_json(str(prim.GetAttribute("descriptor").Get()))
                data = USDSerializer().from_json(str(prim.GetAttribute("data").Get()))

                if data.path == None:
                    OpenGLTextureLib().build(name_attr, data, descriptor)
                elif type(data.path) is not list:
                    path: str = str(data.path)
                    paths = path.split('\\')
                    if '\\' not in path:
                        paths = path.split('/')
                    final_path: Path = Path()
                    for path_element in paths:
                        final_path = final_path / path_element

                    data.path = TEXTURES_PATH / final_path
                    OpenGLTextureLib().build(name_attr, data, descriptor)
                elif type(data.path) is list:
                    texture_paths: list[Path] = []
                    for p in data.path:
                        path: str = str(p)
                        paths = path.split('\\')
                        if '\\' not in path:
                            paths = path.split('/')
                        final_path: Path = Path()
                        for path_element in paths:
                            final_path = final_path / path_element
                        texture_paths.append(TEXTURES_PATH / final_path)

                    data.path = texture_paths
                    OpenGLTextureLib().build(name_attr, data, descriptor)
        
        # Traverse all Shaders prims in the stage
        skip_first_shader_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Shaders' in str(prim_path):
                # Skip the shader prim
                if skip_first_shader_prim:
                    skip_first_shader_prim = False
                    continue

                name_attr = str(prim.GetAttribute("name").Get())
                
                vs_attr = str(prim.GetAttribute("vs_path").Get())
                path: str = vs_attr
                paths = path.split('\\')
                if '\\' not in path:
                    paths = path.split('/')
                final_path: Path = Path()
                for path_element in paths:
                    final_path = final_path / path_element
                vs_attr = SHADERS_PATH / final_path

                fs_attr = str(prim.GetAttribute("fs_path").Get())
                path: str = fs_attr
                paths = path.split('\\')
                if '\\' not in path:
                    paths = path.split('/')
                final_path: Path = Path()
                for path_element in paths:
                    final_path = final_path / path_element
                fs_attr = SHADERS_PATH / final_path

                tcs_attr = str(prim.GetAttribute("tcs_path").Get())
                if (tcs_attr == '' or tcs_attr == 'None'):
                    tcs_attr = None
                else:
                    path: str = tcs_attr
                    paths = path.split('\\')
                    if '\\' not in path:
                        paths = path.split('/')
                    final_path: Path = Path()
                    for path_element in paths:
                        final_path = final_path / path_element
                    tcs_attr = SHADERS_PATH / final_path

                tes_attr = str(prim.GetAttribute("tes_path").Get())
                if (tes_attr == '' or tes_attr == 'None'):
                    tes_attr = None
                else:
                    path: str = tes_attr
                    paths = path.split('\\')
                    if '\\' not in path:
                        paths = path.split('/')
                    final_path: Path = Path()
                    for path_element in paths:
                        final_path = final_path / path_element
                    tes_attr = SHADERS_PATH / final_path

                OpenGLShaderLib().build(name_attr, vs_attr, fs_attr, tcs_attr, tes_attr)

        # Traverse all Materials prims in the stage
        skip_first_material_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Materials' in str(prim_path):
                # Skip the material prim
                if skip_first_material_prim:
                    skip_first_material_prim = False
                    continue

                name_attr = str(prim.GetAttribute("name").Get())
                base_template_attr = str(prim.GetAttribute("base_template").Get())

                textures_attr = [str(texture) for texture in prim.GetAttribute("textures").Get()]

                color_attr: Gf.Vec4f = prim.GetAttribute("color").Get()
                color = glm.vec4(float(color_attr[0]), float(color_attr[1]), float(color_attr[2]), float(color_attr[3]))

                glossiness_attr = float(prim.GetAttribute("glossiness").Get())

                descriptor = USDSerializer().from_json(str(prim.GetAttribute("descriptor").Get()))

                OpenGLMaterialLib().build(name_attr, MaterialData(base_template_attr, textures_attr, color, glossiness_attr), descriptor)
        
        # Traverse all Meshes prims in the stage
        skip_first_mesh_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Meshes' in str(prim_path):
                # Skip the mesh prim
                if skip_first_mesh_prim:
                    skip_first_mesh_prim = False
                    continue

                name_attr = str(prim.GetAttribute("name").Get())
                path_attr = str(prim.GetAttribute("path").Get())

                MeshLib().build(name_attr, MODELS_PATH / path_attr)

        # Traverse all Renderer prims in the stage
        skip_first_renderer_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Renderer' in str(prim_path):
                # Skip the mesh prim
                if skip_first_renderer_prim:
                    skip_first_renderer_prim = False
                    continue
            
                enabled_attr = bool(prim.GetAttribute("enabled").Get())

                OpenGLRenderer().set_shadows_enabled(enabled_attr)
        
        # Traverse all Decorator prims in the stage
        skip_first_decorator_prim = True
        for prim in Usd.PrimRange(root_prim):
            prim_path: Path = prim.GetPath()
            if 'Decorators' in str(prim_path):
                # Skip the mesh prim
                if skip_first_decorator_prim:
                    skip_first_decorator_prim = False
                    continue
                
                decorators = USDSerializer().from_json(str(prim.GetAttribute('dict').Get()))
                for component_type in decorators.values():
                    ComponentLib().register(component_type)

    def has_custom_serialization(self, cls):
        try:
            # Get constructor signature
            constructor_signature = inspect.signature(cls.__init__)

            # Generate arguments dynamically
            args = [None] * (len(constructor_signature.parameters) - 1)  # Subtract 1 for 'self' parameter
            instance = cls(*args)

            # Check if the instance has the 'custom_serialization' attribute
            return hasattr(instance, 'custom_serialization')
        except (TypeError, ValueError, AttributeError):
            return False