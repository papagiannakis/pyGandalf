import OpenGL.GL as gl
from PIL import Image

class TextureLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TextureLib, cls).__new__(cls)
            cls.instance.textures = {}
            cls.instance.slots = {}
            cls.instance.current_slot = 0
        return cls.instance
    
    def build(cls, name: str, path: str = None, img_data: tuple[bytes, int, int] = None):
        if cls.instance.textures.get(name) != None:
            return cls.instance.textures.get(name)

        img_bytes = img_data[0] if img_data is not None else None
        img = None

        if path is not None:
            img = Image.open(path)
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

        cls.instance.textures[name] = texture_id
        cls.instance.slots[name] = cls.instance.current_slot

        cls.instance.current_slot += 1

        return cls.instance.slots[name]

    def get_id(cls, name: str):
        return cls.instance.textures.get(name)
    
    def get_slot(cls, name: str):
        return cls.instance.slots.get(name)
    
    def bind(cls, name):
        gl.glBindTextureUnit(cls.instance.get_slot(name), cls.instance.get_id(name))

    def unbind(cls, name):
        gl.glBindTextureUnit(cls.instance.get_slot(name), 0)

    def bind_textures(cls):
        for slot, id in zip(cls.instance.slots.values(), cls.instance.textures.values()):
            gl.glBindTextureUnit(slot, id)

    def unbind_textures(cls):
        for slot in cls.instance.slots.values():
            gl.glBindTextureUnit(slot, 0)