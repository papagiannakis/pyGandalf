from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

import wgpu
from PIL import Image
from dataclasses import dataclass, field

@dataclass
class TextureData:
    image_bytes: bytes = None
    width: int = 0
    height: int = 0

@dataclass
class TextureInstance:
    texture: wgpu.GPUTexture = None
    view: wgpu.GPUTextureView = None
    sampler: wgpu.GPUSampler = None
    data: TextureData = None

class WebGPUTextureLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebGPUTextureLib, cls).__new__(cls)
            cls.instance.textures = {}
            cls.instance.slots = {}
            cls.instance.current_slot = 0
        return cls.instance
    
    def build(cls, name: str, path: str = None, img_data: tuple[bytes, int, int] = None, flip = False):
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
            return cls.instance.textures.get(name)

        img_bytes = img_data[0] if img_data is not None else None
        img = None

        if path is not None:
            img = Image.open(path)
            if flip:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        width = img.width if img is not None else img_data[1]
        height = img.height if img is not None else img_data[2]
        size = [width, height, 1]

        texture: wgpu.GPUTexture = WebGPURenderer().get_device().create_texture(
            size = size,
            usage = wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.RENDER_ATTACHMENT,
            dimension = wgpu.TextureDimension.d2,
            format = wgpu.TextureFormat.rgba8unorm,
            mip_level_count = 1,
            sample_count = 1,
        )

        view = texture.create_view()
        sampler = WebGPURenderer().get_device().create_sampler()

        WebGPURenderer().get_device().queue.write_texture(
            {
                "texture": texture,
                "mip_level": 0,
                "origin": (0, 0, 0)
            },
            img_bytes,
            {
                "offset": 0,
                "bytes_per_row": width * 4,
                "rows_per_image": height,
            },
            size
        )

        cls.instance.textures[name] = TextureInstance(texture, view, sampler, TextureData(img_bytes, width, height))
        cls.instance.slots[name] = cls.instance.current_slot

        cls.instance.current_slot += 1

        return cls.instance.slots[name]

    def get_instance(cls, name: str) -> TextureInstance:
        """Returns the instance of the texture with the given name.

        Args:
            name (str): The name of the texture.

        Returns:
            TextureInstance: The instance of the texture with the given name.
        """
        return cls.instance.textures.get(name)
    
    def get_slot(cls, name: str):
        """Returns the slot of texture with the given name.

        Args:
            name (str): The name of the texture.

        Returns:
            float: The texture slot.
        """
        return float(cls.instance.slots.get(name))