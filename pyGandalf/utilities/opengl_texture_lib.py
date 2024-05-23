from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.definitions import TEXTURES_PATH

import OpenGL.GL as gl
from PIL import Image

import os
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

class TextureDimension(Enum):
    D2 = 0
    D3 = 1
    CUBE = 2

@dataclass
class TextureDescriptor:
    flip: bool = False
    dimention: TextureDimension = TextureDimension.D2
    width: float = 0.0
    height: float = 0.0

class TextureData:
    def __init__(self, id, slot, name: str, descriptor: TextureDescriptor, path: Path | list[Path], data: tuple[bytes, int, int] = None):
        self.id = id
        self.slot = slot
        self.name = name
        self.descriptor = descriptor
        self.path = path
        self.data = data

class OpenGLTextureLib(object):
    """A class that is used to build textures and get texture data.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLTextureLib, cls).__new__(cls)
            cls.instance.textures = {}
            cls.instance.slots = {}
            cls.instance.current_slot = 0
        return cls.instance
    
    def build(cls, name: str, path: Path | list[Path] = None, img_data: bytes = None, texture_descriptor: TextureDescriptor = TextureDescriptor()):
        """Builds a new texture (if one does not already exists with that name) and returns its slot.

        Args:
            name (str): The name of the texture.
            path (Path, optional): The path the testure asset. Defaults to None.
            img_data (tuple[bytes, int, int], optional): A tuple consisting of the pixel data in bytes, the width and height that will be used to create the texture. Defaults to None.
            flip (bool, optional): Wheter or not to flip the texture vertically. Defaults to False.

        Returns:
            int: The texture slot.
        """
        if cls.instance.textures.get(name) != None:
            return cls.instance.textures[name].slot

        img_bytes = img_data
        img = None

        if path is None or type(path) is not list:
            assert texture_descriptor.dimention == TextureDimension.D2 or texture_descriptor.dimention == TextureDimension.D3, "Single texture path only supported for 2d or 3d textures dimensions"

            if path is not None:
                img = Image.open(path)
                if texture_descriptor.flip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

            texture_id = gl.glGenTextures(1)        
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,                                            #Target
                0,                                                           # Level
                gl.GL_RGBA8,                                                 # Internal Format
                img.width if img is not None else texture_descriptor.width,  # Width
                img.height if img is not None else texture_descriptor.height,# Height
                0,                                                           # Border
                gl.GL_RGBA,                                                  # Format
                gl.GL_UNSIGNED_BYTE,                                         # Type
                img_bytes                                                    # Data
            )

            gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

            relative_path = None
            if path is not None:
                relative_path = Path(os.path.relpath(path, TEXTURES_PATH))

            if img is not None:
                texture_descriptor.width = img.width
                texture_descriptor.height = img.height

            data : TextureData = TextureData(texture_id, cls.instance.current_slot, name, texture_descriptor, relative_path, img_data)
            cls.instance.textures[name] = data

            cls.instance.current_slot += 1

            return data.slot
        elif type(path) is list:
            assert texture_descriptor.dimention == TextureDimension.CUBE, "Multiple texture paths are only supported for cube dimetion type"

            texture_id = gl.glGenTextures(1)        
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture_id)

            relative_path: list[Path] = []
            for i, p in enumerate(path):
                img = Image.open(p)
                if texture_descriptor.flip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img_bytes = img.convert("RGBA").tobytes("raw", "RGB", 0, -1)

                gl.glTexImage2D(
                    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0, gl.GL_RGB8, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_bytes
                )

                if path is not None:
                    relative_path.append(Path(os.path.relpath(p, TEXTURES_PATH)))

            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)

            data : TextureData = TextureData(texture_id, cls.instance.current_slot, name, texture_descriptor, relative_path, img_data)
            cls.instance.textures[name] = data

            cls.instance.current_slot += 1

            return data.slot

    def get_id(cls, name: str):
        """Returns the renderer id of texture with the given name.

        Args:
            name (str): The name of the texture.

        Returns:
            _type_: The renderer id.
        """
        return cls.instance.textures.get(name).id
    
    def get_slot(cls, name: str):
        """Returns the slot of texture with the given name.

        Args:
            name (str): The name of the texture.

        Returns:
            float: The texture slot.
        """
        return float(cls.instance.textures.get(name).slot)
    
    def bind(cls, name: str):
        """Binds the texture with the given name.

        Args:
            name (str): The name of the texture to bind.
        """
        texture_data: TextureData = cls.instance.textures.get(name)
        target = None

        match texture_data.descriptor.dimention:
            case TextureDimension.D2:
                target = gl.GL_TEXTURE_2D
            case TextureDimension.CUBE:
                target = gl.GL_TEXTURE_CUBE_MAP

        gl.glActiveTexture(texture_data.slot + gl.GL_TEXTURE0)
        gl.glBindTexture(target, cls.instance.get_id(name))

    def unbind(cls, name: str):
        """Unbinds the texture with the given name.

        Args:
            name (str): The name of the texture to unbind.
        """
        texture_data: TextureData = cls.instance.textures.get(name)
        target = None

        match texture_data.descriptor.dimention:
            case TextureDimension.D2:
                target = gl.GL_TEXTURE_2D
            case TextureDimension.CUBE:
                target = gl.GL_TEXTURE_CUBE_MAP

        gl.glActiveTexture(texture_data.slot + gl.GL_TEXTURE0)
        gl.glBindTexture(target, 0)

    def bind_textures(cls):
        """Binds all the available textures.
        """
        for texture in cls.instance.textures.values():
            target = None
            match texture.descriptor.dimention:
                case TextureDimension.D2:
                    target = gl.GL_TEXTURE_2D
                case TextureDimension.CUBE:
                    target = gl.GL_TEXTURE_CUBE_MAP
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(target, texture.id)

    def unbind_textures(cls):
        """Unbinds all the available textures.
        """
        for texture in cls.instance.textures.values():
            target = None
            match texture.descriptor.dimention:
                case TextureDimension.D2:
                    target = gl.GL_TEXTURE_2D
                case TextureDimension.CUBE:
                    target = gl.GL_TEXTURE_CUBE_MAP
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(target, 0)
    
    def get_textures(cls) -> dict[str, TextureData]:
        """Returns a dictionary the holds all the textures. As the key is the name of the texture, as the value is the texture data.

        Returns:
            dict[str, TextureData]: A dictionary the holds all the textures.
        """
        return cls.instance.textures