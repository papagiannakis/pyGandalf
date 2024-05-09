from pyGandalf.renderer.base_renderer import BaseRenderer
from pyGandalf.utilities.logger import logger

from dataclasses import dataclass, field
import wgpu

import glm
import numpy as np

@dataclass
class ColorAttachmentDescription:
    view: wgpu.GPUTextureView = None
    resolve_target: wgpu.GPUTextureView = None
    clear_value: tuple = (0.8, 0.5, 0.3, 1.0)
    color_load_op: wgpu.LoadOp = wgpu.LoadOp.clear
    color_store_op: wgpu.StoreOp = wgpu.StoreOp.store

@dataclass
class RenderPassDescription:
    color_attachment: bool = True
    depth_stencil_attachment: bool = True

    color_attachments: list[ColorAttachmentDescription] = field(default_factory=list[ColorAttachmentDescription]) 

    depth_texture_view: wgpu.GPUTextureView = None
    depth_clear_value: float = 1.0
    depth_load_op: wgpu.LoadOp = wgpu.LoadOp.clear
    depth_store_op: wgpu.StoreOp = wgpu.StoreOp.store
    depth_read_only: bool = False

    stencil_clear_value: float = 0.0
    stencil_load_op: wgpu.LoadOp = wgpu.LoadOp.clear
    stencil_store_op: wgpu.StoreOp = wgpu.StoreOp.store
    stencil_read_only: bool = True

class WebGPURenderer(BaseRenderer):
    def initialize(cls, *kargs):
        cls.instance.canvas = kargs[0]
        power_preference: str = kargs[1]
        cls.instance.adapter = wgpu.gpu.request_adapter(power_preference=power_preference)
        cls.instance.device = cls.instance.adapter.request_device(required_limits={})

        cls.instance.present_context = cls.instance.canvas.get_context()
        cls.instance.render_texture_format = cls.instance.present_context.get_preferred_format(cls.instance.device.adapter)
        cls.instance.present_context.configure(device=cls.instance.device, format=cls.instance.render_texture_format)

        cls.instance.command_queue = []
        cls.instance.command_encoder: wgpu.GPUCommandEncoder = None # type: ignore
        cls.instance.current_render_pass: wgpu.GPURenderPassEncoder = None # type: ignore
        cls.instance.current_texture = None
        cls.instance.depth_texture_view = None

    def begin_frame(cls):
        cls.instance.current_texture = cls.instance.present_context.get_current_texture()

        # base_pass_desc: RenderPassDescription = RenderPassDescription()
        # color_attachment: ColorAttachmentDescription = ColorAttachmentDescription()
        # color_attachment.view = cls.instance.current_texture.create_view()
        # base_pass_desc.depth_stencil_attachment=True
        # base_pass_desc.depth_texture_view = cls.instance.depth_texture_view
        # base_pass_desc.color_attachments.append(color_attachment)

        # cls.instance.begin_render_pass(base_pass_desc)
    
    def end_frame(cls):
        # cls.instance.end_render_pass()
        cls.instance.device.queue.submit([cls.instance.command_encoder.finish()])
        cls.instance.canvas.request_draw()
    
    def resize(cls, width, height):
        pass
    
    def clean(cls):
        pass

    def add_batch(cls, render_data, material):
        # Filter out None from attributes
        render_data.attributes = list(filter(lambda x: x is not None, render_data.attributes))

        buffers = []

        for index, attribute in enumerate(render_data.attributes):
            buffer : wgpu.GPUBuffer = cls.instance.device.create_buffer_with_data(
                data=attribute,
                usage=wgpu.BufferUsage.VERTEX
            )

            render_data.buffers.append(buffer)

            attribute_format = wgpu.VertexFormat.float32
            vertex_length = len(attribute[index])
            match vertex_length:
                case 1:
                    attribute_format = wgpu.VertexFormat.float32
                case 2:
                    attribute_format = wgpu.VertexFormat.float32x2
                case 3:
                    attribute_format = wgpu.VertexFormat.float32x3
                case 4:
                    attribute_format = wgpu.VertexFormat.float32x4

            buffers.append({
                "array_stride": 4 * vertex_length,
                "step_mode": wgpu.VertexStepMode.vertex,
                "attributes": [
                    {
                        "format": attribute_format,
                        "offset": 0,
                        "shader_location": index,
                    }
                ],
            })            

        if render_data.indices is not None:
            index_buffer : wgpu.GPUBuffer = cls.instance.device.create_buffer_with_data(
                data=render_data.indices,
                usage=wgpu.BufferUsage.INDEX
            )
            render_data.index_buffer = index_buffer

        render_pipeline : wgpu.GPURenderPipeline = cls.instance.device.create_render_pipeline(
            layout=material.instance.pipeline_layout,
            vertex={
                "module": material.instance.shader_module,
                "entry_point": "vs_main",
                "buffers": buffers
            },
            primitive={
                "topology": wgpu.PrimitiveTopology.triangle_list,
                "front_face": wgpu.FrontFace.ccw,
                "cull_mode": wgpu.CullMode.none,
            },
            depth_stencil={
                "format": wgpu.TextureFormat.depth24plus,
                "depth_write_enabled": True,
                "depth_compare": wgpu.CompareFunction.less,
                "stencil_front": {
                    "compare": wgpu.CompareFunction.always,
                    "fail_op": wgpu.StencilOperation.keep,
                    "depth_fail_op": wgpu.StencilOperation.keep,
                    "pass_op": wgpu.StencilOperation.keep,
                },
                "stencil_back": {
                    "compare": wgpu.CompareFunction.always,
                    "fail_op": wgpu.StencilOperation.keep,
                    "depth_fail_op": wgpu.StencilOperation.keep,
                    "pass_op": wgpu.StencilOperation.keep,
                },
                "stencil_read_mask": 0,
                "stencil_write_mask": 0,
                "depth_bias": 0,
                "depth_bias_slope_scale": 0.0,
                "depth_bias_clamp": 0.0,
            },
            multisample=None,
            fragment={
                "module": material.instance.shader_module,
                "entry_point": "fs_main",
                "targets": [
                    {
                        "format": cls.instance.render_texture_format,
                        "blend": {
                            "color": (
                                wgpu.BlendFactor.one,
                                wgpu.BlendFactor.zero,
                                wgpu.BlendOperation.add,
                            ),
                            "alpha": (
                                wgpu.BlendFactor.one,
                                wgpu.BlendFactor.zero,
                                wgpu.BlendOperation.add,
                            ),
                        },
                    },
                ],
            },
        )
        render_data.render_pipeline = render_pipeline

        depth_texture : wgpu.GPUTexture = cls.instance.device.create_texture(
            label="depth_texture",
            size=[1280, 720, 1],
            mip_level_count=1,
            sample_count=1,
            dimension="2d",
            format=wgpu.TextureFormat.depth24plus,
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT
        )

        cls.instance.depth_texture_view = depth_texture.create_view(
            label="depth_texture_view",
            format=wgpu.TextureFormat.depth24plus,
            dimension="2d",
            aspect=wgpu.TextureAspect.depth_only,
            base_mip_level=0,
            mip_level_count=1,
            base_array_layer=0,
            array_layer_count=1,
        )

    def begin_render_pass(cls, render_pass_desc: RenderPassDescription):
        assert cls.instance.current_render_pass == None, 'Previous render pass not ended yet, call end_render_pass() first before starting a new one.'
        cls.instance.command_encoder = cls.instance.device.create_command_encoder()

        color_attachments = []

        if render_pass_desc.color_attachment:
            for color_attachment in render_pass_desc.color_attachments:
                color_attachments.append({
                    "view": color_attachment.view,
                    "resolve_target": color_attachment.resolve_target,
                    "clear_value": color_attachment.clear_value,
                    "load_op": color_attachment.color_load_op,
                    "store_op": color_attachment.color_store_op,
                })

        depth_stencil_attachment = None

        if render_pass_desc.depth_stencil_attachment:
            depth_stencil_attachment = {
                "view": render_pass_desc.depth_texture_view,
                "depth_clear_value": render_pass_desc.depth_clear_value,
                "depth_load_op": render_pass_desc.depth_load_op,
                "depth_store_op": render_pass_desc.depth_store_op,
                "depth_read_only": render_pass_desc.depth_read_only,
                "stencil_clear_value": render_pass_desc.stencil_clear_value,
                "stencil_load_op": render_pass_desc.stencil_load_op,
                "stencil_store_op": render_pass_desc.stencil_store_op,
                "stencil_read_only": render_pass_desc.stencil_read_only,
            }
        cls.instance.current_render_pass = cls.instance.command_encoder.begin_render_pass(
            color_attachments=color_attachments,
            depth_stencil_attachment=depth_stencil_attachment,
        )

    def end_render_pass(cls):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        cls.instance.current_render_pass.end()
        cls.instance.current_render_pass = None
    
    def set_pipeline(cls, render_data):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        cls.instance.current_render_pass.set_pipeline(render_data.render_pipeline)

    def set_buffers(cls, render_data):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        if render_data.index_buffer != None:
            cls.instance.current_render_pass.set_index_buffer(render_data.index_buffer, wgpu.IndexFormat.uint32)

        for index, buffer in enumerate(render_data.buffers):
            cls.instance.current_render_pass.set_vertex_buffer(index, buffer)

    def set_bind_groups(cls, material):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        for index, bind_group in enumerate(material.instance.bind_groups):
            cls.instance.current_render_pass.set_bind_group(index, bind_group, [], 0, 1)

    def write_buffer(cls, buffer, uniform_data, size=0):
        cls.instance.device.queue.write_buffer(buffer, 0, uniform_data, 0, size)

    def write_texture(cls, uniform_data):
        cls.instance.device.queue.write_texture(
            {
                "texture": uniform_data.texture,
                "mip_level": 0,
                "origin": (0, 0, 0)
            },
            uniform_data.data.image_bytes,
            {
                "offset": 0,
                "bytes_per_row": uniform_data.data.width * 4,
                "rows_per_image": uniform_data.data.height
            },
            [uniform_data.data.width, uniform_data.data.width, 1]
        )

    def draw(cls, render_data, instance_count=1, first_instance=0):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        cls.instance.current_render_pass.draw(len(render_data.attributes[0]), instance_count, 0, first_instance)

    def draw_indexed(cls, render_data, instance_count=1, first_instance=0):
        assert cls.instance.current_render_pass != None, 'Submiting commands to None render pass, call begin_render_pass() first.'
        cls.instance.current_render_pass.draw_indexed(render_data.indices.size, instance_count, 0, 0, first_instance)

    def get_device(cls) -> wgpu.GPUDevice:
        return cls.instance.device
    
    def get_command_encoder(cls) -> wgpu.GPUCommandEncoder:
        return cls.instance.command_encoder
    
    def get_current_texture(cls) -> wgpu.GPUTexture:
        return cls.instance.current_texture
    
    def get_depth_texture_view(cls) -> wgpu.GPUTextureView:
        return cls.instance.depth_texture_view
