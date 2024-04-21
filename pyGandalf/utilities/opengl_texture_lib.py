from pyGandalf.utilities.definitions import TEXTURES_PATH

import os
import OpenGL.GL as gl
from PIL import Image
from pathlib import Path

class TextureData:
    def __init__(self, id, slot, name: str, path: Path, data: tuple[bytes, int, int] = None):
        self.id = id
        self.slot = slot
        self.name = name
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
    
    def build(cls, name: str, path: Path = None, img_data: tuple[bytes, int, int] = None, flip = False):
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

        img_bytes = img_data[0] if img_data is not None else None
        img = None

        if path is not None:
            img = Image.open(path)
            if flip:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        texture_id = gl.glGenTextures(1)        
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,                               #Target
            0,                                              # Level
            gl.GL_RGBA8,                                    # Internal Format
            img.width if img is not None else img_data[1],  # Width
            img.height if img is not None else img_data[2], # Height
            0,                                              # Border
            gl.GL_RGBA,                                     # Format
            gl.GL_UNSIGNED_BYTE,                            # Type
            img_bytes                                       # Data
        )

        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        relative_path = None
        if path is not None:
            relative_path = Path(os.path.relpath(path, TEXTURES_PATH))

        data : TextureData = TextureData(texture_id, cls.instance.current_slot, name, relative_path, img_data)
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
        gl.glActiveTexture(cls.instance.textures.get(name).slot + gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cls.instance.get_id(name))

    def unbind(cls, name: str):
        """Unbinds the texture with the given name.

        Args:
            name (str): The name of the texture to unbind.
        """
        gl.glActiveTexture(cls.instance.textures.get(name).slot + gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def bind_textures(cls):
        """Binds all the available textures.
        """
        for texture in cls.instance.textures.values():
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)

    def unbind_textures(cls):
        """Unbinds all the available textures.
        """
        for texture in cls.instance.textures.values():
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    
    def get_textures(cls) -> dict[str, TextureData]:
        """Returns a dictionary the holds all the textures. As the key is the name of the texture, as the value is the texture data.

        Returns:
            dict[str, TextureData]: A dictionary the holds all the textures.
        """
        return cls.instance.textures