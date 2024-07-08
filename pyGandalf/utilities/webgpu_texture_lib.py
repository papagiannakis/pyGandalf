from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

import wgpu
from PIL import Image

from pathlib import Path
from dataclasses import dataclass

@dataclass
class TextureDescriptor:
    flip: bool = False
    dimention: wgpu.TextureDimension = wgpu.TextureDimension.d2
    view_aspect: wgpu.TextureAspect = wgpu.TextureAspect.all
    view_format: wgpu.TextureFormat = None
    view_dimention: wgpu.TextureViewDimension = wgpu.TextureViewDimension.d2
    usage: wgpu.TextureUsage = wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.RENDER_ATTACHMENT
    format: wgpu.TextureFormat = wgpu.TextureFormat.rgba8unorm
    address_mode_u: wgpu.AddressMode = wgpu.AddressMode.clamp_to_edge
    address_mode_v: wgpu.AddressMode = wgpu.AddressMode.clamp_to_edge
    address_mode_w: wgpu.AddressMode = wgpu.AddressMode.clamp_to_edge
    min_filter: wgpu.FilterMode = wgpu.FilterMode.linear
    mag_filter: wgpu.FilterMode = wgpu.FilterMode.linear
    sampler_compare: wgpu.CompareFunction = None
    array_layer_count: int = 1

@dataclass
class TextureData:
    path: Path | list[Path] = None
    width: int = 0
    height: int = 0
    image_bytes: bytes = None

@dataclass
class TextureInstance:
    texture: wgpu.GPUTexture = None
    view: wgpu.GPUTextureView = None
    sampler: wgpu.GPUSampler = None
    data: TextureData = None
    descriptor: TextureDescriptor = None

class WebGPUTextureLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebGPUTextureLib, cls).__new__(cls)
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
            return cls.instance.textures.get(name)

        if data.path is not None:
            if type(data.path) is not list:
                img = Image.open(data.path)
                if descriptor.flip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                data.image_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
                data.width = img.width
                data.height = img.height
            else:
                cubemap_data = []
                for p in data.path:
                    img = Image.open(p)
                    if descriptor.flip:
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)
                    cubemap_data.append(img.convert("RGBA").tobytes("raw", "RGBA", 0, -1))
                    data.width = img.width
                    data.height = img.height                

                data.image_bytes = bytes()
                for cubemap in cubemap_data:
                    data.image_bytes += cubemap

        size = [data.width, data.height, descriptor.array_layer_count]

        texture: wgpu.GPUTexture = WebGPURenderer().get_device().create_texture(
            size = size,
            usage = descriptor.usage,
            dimension = descriptor.dimention,
            format = descriptor.format,
            mip_level_count = 1,
            sample_count = 1,
        )

        view = texture.create_view(
            dimension=descriptor.view_dimention,
            aspect=descriptor.view_aspect,
            format=descriptor.view_format,
            array_layer_count=descriptor.array_layer_count,
        )

        sampler = WebGPURenderer().get_device().create_sampler(
            address_mode_u=descriptor.address_mode_u,
            address_mode_v=descriptor.address_mode_v,
            address_mode_w=descriptor.address_mode_w,
            min_filter=descriptor.min_filter,
            mag_filter=descriptor.mag_filter,
            compare=descriptor.sampler_compare,
            mipmap_filter=wgpu.FilterMode.nearest,
            max_anisotropy=1,
        )

        if data.image_bytes != None:
            WebGPURenderer().get_device().queue.write_texture(
                {
                    "texture": texture,
                    "mip_level": 0,
                    "origin": (0, 0, 0)
                },
                data.image_bytes,
                {
                    "offset": 0,
                    "bytes_per_row": data.width * 4,
                    "rows_per_image": data.height,
                },
                size
            )

        cls.instance.textures[name] = TextureInstance(texture, view, sampler, data, descriptor)
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