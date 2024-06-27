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
    internal_format: gl.Constant = gl.GL_RGBA8
    format: gl.Constant = gl.GL_RGBA
    type: gl.Constant = gl.GL_UNSIGNED_BYTE
    wrap_s: gl.Constant = gl.GL_REPEAT
    wrap_t: gl.Constant = gl.GL_REPEAT
    min_filter: gl.Constant = gl.GL_LINEAR
    max_filter: gl.Constant = gl.GL_LINEAR

@dataclass
class TextureData:
    path: Path | list[Path] = None
    image_bytes: bytes = None
    width: int = 0
    height: int = 0

class TextureInstance:
    def __init__(self, id, slot, name: str, data: TextureData, descriptor: TextureDescriptor):
        self.id = id
        self.slot = slot
        self.name = name
        self.data = data
        self.descriptor = descriptor

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
    
    def build(cls, name: str, data: TextureData, descriptor: TextureDescriptor = TextureDescriptor()):
        """Builds a new texture (if one does not already exists with that name) and returns its slot.

        Args:
            name (str): The name of the texture.
            data (TextureData): The data of the texture. You can either give a path (or list of paths if cubemap) or the byte data to use when creating the texture and the width and height.
            descriptor (TextureDescriptor, optional): The description of the texture, which consists of various options and flags.

        Returns:
            int: The texture slot.
        """
        if cls.instance.textures.get(name) != None:
            return cls.instance.textures[name].slot

        img_bytes = data.image_bytes
        img = None

        if data.path is None or type(data.path) is not list:
            assert descriptor.dimention == TextureDimension.D2 or descriptor.dimention == TextureDimension.D3, "Single texture path only supported for 2d or 3d textures dimensions"

            if data.path is not None:
                img = Image.open(data.path)
                if descriptor.flip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

            texture_id = gl.glGenTextures(1)        
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, descriptor.wrap_s)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, descriptor.wrap_t)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, descriptor.min_filter)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, descriptor.min_filter)

            gl.glTexParameterfv(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])

            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,                                     #Target
                0,                                                    # Level
                descriptor.internal_format,                           # Internal Format
                img.width if img is not None else data.width,   # Width
                img.height if img is not None else data.height, # Height
                0,                                                    # Border
                descriptor.format,                                    # Format
                descriptor.type,                                      # Type
                img_bytes                                             # Data
            )

            gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

            if data.path is not None:
                data.path = Path(os.path.relpath(data.path, TEXTURES_PATH))

            if img is not None:
                data.width = img.width
                data.height = img.height

            texture_instance : TextureInstance = TextureInstance(texture_id, cls.instance.current_slot, name, data, descriptor)
            cls.instance.textures[name] = texture_instance

            cls.instance.current_slot += 1

            return texture_instance.slot
        elif type(data.path) is list:
            assert descriptor.dimention == TextureDimension.CUBE, "Multiple texture paths are only supported for cube dimetion type"

            texture_id = gl.glGenTextures(1)        
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture_id)

            for i, p in enumerate(data.path):
                img = Image.open(p)
                if descriptor.flip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img_bytes = img.convert("RGBA").tobytes("raw", "RGB", 0, -1)

                gl.glTexImage2D(
                    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0, descriptor.internal_format, img.width, img.height, 0, descriptor.format, descriptor.type, img_bytes
                )

                if data.path is not None:
                    data.path[i] = Path(os.path.relpath(p, TEXTURES_PATH))

            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)

            texture_instance : TextureInstance = TextureInstance(texture_id, cls.instance.current_slot, name, data, descriptor)
            cls.instance.textures[name] = texture_instance

            cls.instance.current_slot += 1

            return texture_instance.slot

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
        texture: TextureInstance = cls.instance.textures.get(name)

        if texture == None:
            logger.error(f"No such texture exists: '{name}'")
            return

        return float(texture.slot)
    
    def bind(cls, name: str):
        """Binds the texture with the given name.

        Args:
            name (str): The name of the texture to bind.
        """
        texture: TextureInstance = cls.instance.textures.get(name)
        target = None

        if texture == None:
            logger.error(f"No such texture exists: '{name}'")
            return

        match texture.descriptor.dimention:
            case TextureDimension.D2:
                target = gl.GL_TEXTURE_2D
            case TextureDimension.CUBE:
                target = gl.GL_TEXTURE_CUBE_MAP

        gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
        gl.glBindTexture(target, cls.instance.get_id(name))

    def unbind(cls, name: str):
        """Unbinds the texture with the given name.

        Args:
            name (str): The name of the texture to unbind.
        """
        texture: TextureInstance = cls.instance.textures.get(name)
        target = None

        if texture == None:
            logger.error(f"No such texture exists: '{name}'")
            return

        match texture.descriptor.dimention:
            case TextureDimension.D2:
                target = gl.GL_TEXTURE_2D
            case TextureDimension.CUBE:
                target = gl.GL_TEXTURE_CUBE_MAP

        gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
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
    
    def get_textures(cls) -> dict[str, TextureInstance]:
        """Returns a dictionary the holds all the textures. As the key is the name of the texture, as the value is the texture data.

        Returns:
            dict[str, TextureInstance]: A dictionary the holds all the textures.
        """
        return cls.instance.textures