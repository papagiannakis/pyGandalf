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
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OpenGLTextureLib, cls).__new__(cls)
            cls.instance.textures = {}
            cls.instance.slots = {}
            cls.instance.current_slot = 0
        return cls.instance
    
    def build(cls, name: str, path: Path = None, img_data: tuple[bytes, int, int] = None, flip = False):
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

        if img_data is not None:
            print(img_data[0])
            print([x for x in img_data[0]])
            print(bytes([x for x in img_data[0]]))

        data : TextureData = TextureData(texture_id, cls.instance.current_slot, name, relative_path, img_data)
        cls.instance.textures[name] = data

        cls.instance.current_slot += 1

        return data.slot

    def get_id(cls, name: str):
        return cls.instance.textures.get(name).id
    
    def get_slot(cls, name: str):
        return float(cls.instance.textures.get(name).slot)
    
    def bind(cls, name):
        gl.glActiveTexture(cls.instance.textures.get(name).slot + gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cls.instance.get_id(name))

    def unbind(cls, name):
        gl.glActiveTexture(cls.instance.textures.get(name).slot + gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def bind_textures(cls):
        for texture in cls.instance.textures.values():
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)

    def unbind_textures(cls):
        for texture in cls.instance.textures.values():
            gl.glActiveTexture(texture.slot + gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    
    def get_textures(cls):
        return cls.instance.textures