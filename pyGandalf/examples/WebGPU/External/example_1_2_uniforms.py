import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import glm
import numpy as np

from pyGandalf.utilities.definitions import SHADERS_PATH

global t


def load_from_file(path_to_source):
    with open(path_to_source) as file:
        return file.read()

def main(canvas, power_preference="high-performance", limits=None):
    adapter = wgpu.gpu.request_adapter(power_preference=power_preference)
    device = adapter.request_device(required_limits={})
    return _main(canvas, device)


def _main(canvas, device: wgpu.GPUDevice):
    shader_source = load_from_file(SHADERS_PATH/'webgpu'/'unlit_no_storage.wgsl')

    shader: wgpu.GPUShaderModule = device.create_shader_module(code=shader_source)

    present_context : wgpu.GPUCanvasContext = canvas.get_context()
    render_texture_format = present_context.get_preferred_format(device.adapter)
    present_context.configure(device=device, format=render_texture_format)

    uniform_dtype = np.dtype([
        ("proj", np.float32, (4, 4)),
        ("view", np.float32, (4, 4)),
        ("model", np.float32, (4, 4)),
    ])

    T = glm.translate(glm.mat4(1.0), glm.vec3(-3, 0, 0))
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

    # Vertices of the triangle
    vertex_data = np.array([
        [-0.5, -0.5, 0.0], # 0 - Bottom left
        [ 0.5, -0.5, 0.0], # 1 - Bottom right
        [ 0.0,  0.5, 0.0], # 2 - Top middle
    ], dtype=np.float32)

    vertex_buffer : wgpu.GPUBuffer = device.create_buffer_with_data(
        data=vertex_data,
        usage=wgpu.BufferUsage.VERTEX
    )

    # Create uniform buffer - data is uploaded each frame
    uniform_buffer = device.create_buffer(
        size=uniform_data.nbytes, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
    )

    bind_groups_entries = [[]]
    bind_groups_layout_entries = [[]]

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
            "buffer": {"type": wgpu.BufferBindingType.uniform},
        }
    )

    # Create the wgpu binding objects
    bind_group_layouts = []
    bind_groups = []

    for entries, layout_entries in zip(bind_groups_entries, bind_groups_layout_entries):
        bind_group_layout = device.create_bind_group_layout(entries=layout_entries)
        bind_group_layouts.append(device.create_bind_group_layout(entries=layout_entries))
        bind_groups.append(
            device.create_bind_group(layout=bind_group_layout, entries=entries)
        )

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

    t = 0

    def draw_frame():
        current_texture : wgpu.GPUTexture = present_context.get_current_texture()
        command_encoder : wgpu.GPUCommandEncoder = device.create_command_encoder()

        render_pass : wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": current_texture.create_view(),
                    "resolve_target": None,
                    "clear_value": (0, 0, 0, 1),
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
        nonlocal t
        t += 0.01
        T = glm.translate(glm.mat4(1.0), glm.vec3(t, 0, 0))
        model = T * glm.mat4(R) * S
        uniform_data["model"] = np.asarray(glm.transpose(model))

        # Write uniform buffer
        device.queue.write_buffer(uniform_buffer, 0, uniform_data, 0)

        render_pass.set_pipeline(render_pipeline)
        render_pass.set_vertex_buffer(0, vertex_buffer)
        render_pass.set_bind_group(0, bind_groups[0], [], 0, 1)

        render_pass.draw(3, 1, 0, 0)
        render_pass.end()
        device.queue.submit([command_encoder.finish()])

        canvas.request_draw()

    canvas.request_draw(draw_frame)
    return device

if __name__ == "__main__":
    canvas = WgpuCanvas(size=(1280, 720), title="wgpu triangle with uniforms")
    main(canvas)
    run()