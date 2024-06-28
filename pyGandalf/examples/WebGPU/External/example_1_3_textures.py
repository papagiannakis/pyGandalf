import wgpu
from wgpu.gui.auto import WgpuCanvas, run
from PIL import Image

import glm
import numpy as np

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH

def load_from_file(path_to_source):
    with open(path_to_source) as file:
        return file.read()
    
def load_texture(device, path, flip):
    img = Image.open(path)
    if flip:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    img_bytes = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    size = [img.width, img.height, 1]

    texture: wgpu.GPUTexture = device.create_texture(
        size = size,
        usage = wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.RENDER_ATTACHMENT,
        dimension = wgpu.TextureDimension.d2,
        format = wgpu.TextureFormat.rgba8unorm,
        mip_level_count = 1,
        sample_count = 1,
    )

    view = texture.create_view(
        dimension=wgpu.TextureViewDimension.d2,
        aspect=wgpu.TextureAspect.all,
        format=None,
        array_layer_count=1,
    )

    sampler = device.create_sampler(
        address_mode_u=wgpu.AddressMode.clamp_to_edge,
        address_mode_v=wgpu.AddressMode.clamp_to_edge,
        address_mode_w=wgpu.AddressMode.clamp_to_edge,
        min_filter=wgpu.FilterMode.linear,
        mag_filter=wgpu.FilterMode.linear,
        compare=None,
        mipmap_filter=wgpu.FilterMode.nearest,
        max_anisotropy=1,
    )

    device.queue.write_texture(
        {
            "texture": texture,
            "mip_level": 0,
            "origin": (0, 0, 0)
        },
        img_bytes,
        {
            "offset": 0,
            "bytes_per_row": img.width * 4,
            "rows_per_image": img.height,
        },
        size
    )

    return texture, view, sampler, img, img_bytes

def main(canvas, power_preference="high-performance", limits=None):
    """Regular function to setup a viz on the given canvas."""
    adapter = wgpu.gpu.request_adapter(power_preference=power_preference)
    device = adapter.request_device(required_limits={})
    return _main(canvas, device)


def _main(canvas, device: wgpu.GPUDevice):
    shader_source = load_from_file(SHADERS_PATH/'webgpu'/'unlit_textured_no_storage.wgsl')
    shader: wgpu.GPUShaderModule = device.create_shader_module(code=shader_source)

    present_context : wgpu.GPUCanvasContext = canvas.get_context()
    render_texture_format = present_context.get_preferred_format(device.adapter)
    present_context.configure(device=device, format=render_texture_format)

    texture, texture_view, sampler, img, img_bytes = load_texture(device, TEXTURES_PATH/'bricks2.jpg', False)

    uniform_dtype = np.dtype([
        ("proj", np.float32, (4, 4)),
        ("view", np.float32, (4, 4)),
        ("model", np.float32, (4, 4)),
    ])

    T = glm.translate(glm.mat4(1.0), glm.vec3(0, 0, 0))
    R = glm.quat(glm.vec3(glm.radians(0.0), glm.radians(0.0), glm.radians(0.0)))
    S = glm.scale(glm.mat4(1.0), glm.vec3(1, 1, 1))
    
    model = T * glm.mat4(R) * S
    view = glm.translate(glm.mat4(1.0), glm.vec3(0, 0, 3))
    proj = glm.perspectiveLH(glm.radians(40), 1.778, 0.1, 1000)

    uniform_data = np.array((
        np.asarray(glm.transpose(proj)),
        np.asarray(glm.transpose(view)),
        np.asarray(glm.transpose(model))
    ), dtype=uniform_dtype)

    # Vertices of the quad
    vertex_data = np.array([
        [-0.5, -0.5, 0.0], # 0 - Bottom left
        [ 0.5, -0.5, 0.0], # 1 - Bottom right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [ 0.5,  0.5, 0.0], # 2 - Top right
        [-0.5,  0.5, 0.0], # 3 - Top left
        [-0.5, -0.5, 0.0]  # 0 - Bottom left
    ], dtype=np.float32)

    # Texture coordinates of the quad
    texture_coordinate_data = np.array([
        [0.0, 1.0], # 0
        [1.0, 1.0], # 1
        [1.0, 0.0], # 2
        [1.0, 0.0], # 2
        [0.0, 0.0], # 3
        [0.0, 1.0]  # 0
    ], dtype=np.float32)

    # Create buffer for vertex positions
    vertex_buffer : wgpu.GPUBuffer = device.create_buffer_with_data(
        data=vertex_data,
        usage=wgpu.BufferUsage.VERTEX
    )

    # Create buffer for texture coordinates
    texture_coordinate_buffer : wgpu.GPUBuffer = device.create_buffer_with_data(
        data=texture_coordinate_data,
        usage=wgpu.BufferUsage.VERTEX
    )

    # Create uniform buffer - data is uploaded each frame
    uniform_buffer = device.create_buffer(
        size=uniform_data.nbytes, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
    )

    # create 2 bind groups, one for the uniform buffer and one for the texture and sampler
    bind_groups_entries = [[], []]
    bind_groups_layout_entries = [[], []]

    # Uniform buffer binding
    bind_groups_entries[0].append(
        {
            "binding": 0,
            "resource": {
                "buffer": uniform_buffer,
                "offset": 0,
                "size": uniform_buffer.size,
            },
        }
    )
    bind_groups_layout_entries[0].append(
        {
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX,
            "buffer": {
                "type": wgpu.BufferBindingType.uniform
            },
        }
    )

    # Texture binding
    bind_groups_entries[1].append(
        {
            "binding": 0,
            "resource": texture_view,
        }
    )
    bind_groups_layout_entries[1].append(
        {
            "binding": 0,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "texture": {  
                "sample_type": wgpu.TextureSampleType.float,
                "view_dimension": wgpu.TextureViewDimension.d2,
            },
        }
    )

    # Sampler binding
    bind_groups_entries[1].append(
        {
            "binding": 1,
            "resource": sampler,
        }
    )
    bind_groups_layout_entries[1].append(
        {
            "binding": 1,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "sampler": {
                "type": wgpu.SamplerBindingType.filtering
            },
        }
    )

    # Create the wgou binding objects
    bind_group_layouts = []
    bind_groups = []

    for entries, layout_entries in zip(bind_groups_entries, bind_groups_layout_entries):
        bind_group_layout = device.create_bind_group_layout(entries=layout_entries)
        bind_group_layouts.append(device.create_bind_group_layout(entries=layout_entries))
        bind_groups.append(
            device.create_bind_group(layout=bind_group_layout, entries=entries)
        )

    # No bind group and layout, we should not create empty ones.
    pipeline_layout : wgpu.GPUPipelineLayout = device.create_pipeline_layout(bind_group_layouts=bind_group_layouts)

    render_pipeline : wgpu.GPURenderPipeline = device.create_render_pipeline(
        layout=pipeline_layout,
        vertex={
            "module": shader,
            "entry_point": "vs_main",
            "buffers": [
                {
                    "array_stride": 4 * 3,
                    "step_mode": wgpu.VertexStepMode.vertex,
                    "attributes": [
                        {
                            "format": wgpu.VertexFormat.float32x3,
                            "offset": 0,
                            "shader_location": 0,
                        }
                    ],
                },
                {
                    "array_stride": 4 * 2,
                    "step_mode": wgpu.VertexStepMode.vertex,
                    "attributes": [
                        {
                            "format": wgpu.VertexFormat.float32x2,
                            "offset": 0,
                            "shader_location": 1,
                        }
                    ],
                }
            ],
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
            "module": shader,
            "entry_point": "fs_main",
            "targets": [
                {
                    "format": render_texture_format,
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

    depth_texture : wgpu.GPUTexture = device.create_texture(
        label="depth_texture",
        size=[1280, 720, 1],
        mip_level_count=1,
        sample_count=1,
        dimension="2d",
        format=wgpu.TextureFormat.depth24plus,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT
    )

    depth_texture_view : wgpu.GPUTextureView = depth_texture.create_view(
        label="depth_texture_view",
        format=wgpu.TextureFormat.depth24plus,
        dimension="2d",
        aspect=wgpu.TextureAspect.depth_only,
        base_mip_level=0,
        mip_level_count=1,
        base_array_layer=0,
        array_layer_count=1,
    )

    def draw_frame():
        current_texture : wgpu.GPUTexture = present_context.get_current_texture()
        command_encoder : wgpu.GPUCommandEncoder = device.create_command_encoder()

        render_pass : wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": current_texture.create_view(),
                    "resolve_target": None,
                    "clear_value": (0.25, 0.25, 0.25, 1),
                    "load_op": wgpu.LoadOp.clear,
                    "store_op": wgpu.StoreOp.store,
                }
            ],
            depth_stencil_attachment={
                "view": depth_texture_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store,
                "depth_read_only": False,
                "stencil_clear_value": 0,
                "stencil_load_op": wgpu.LoadOp.clear,
                "stencil_store_op": wgpu.StoreOp.store,
                "stencil_read_only": True,
            },
        )

        # Update uniform buffer here
        # ...

        # Write uniform buffer
        device.queue.write_buffer(uniform_buffer, 0, uniform_data, 0)

        render_pass.set_pipeline(render_pipeline)
        render_pass.set_vertex_buffer(0, vertex_buffer)
        render_pass.set_vertex_buffer(1, texture_coordinate_buffer)
        for index, bind_group in enumerate(bind_groups):
            render_pass.set_bind_group(index, bind_group, [], 0, 1)

        render_pass.draw(6, 1, 0, 0)
        render_pass.end()
        device.queue.submit([command_encoder.finish()])

        canvas.request_draw()

    canvas.request_draw(draw_frame)
    return device

if __name__ == "__main__":
    canvas = WgpuCanvas(size=(1280, 720), title="wgpu triangle")
    main(canvas)
    run()