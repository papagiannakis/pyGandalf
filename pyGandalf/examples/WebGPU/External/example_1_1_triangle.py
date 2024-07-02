import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import numpy as np

from pyGandalf.utilities.definitions import SHADERS_PATH

def load_from_file(path_to_source):
    with open(path_to_source) as file:
        return file.read()

def main(canvas, power_preference="high-performance", limits=None):
    adapter = wgpu.gpu.request_adapter(power_preference=power_preference)
    device = adapter.request_device(required_limits={})
    return _main(canvas, device)


def _main(canvas, device: wgpu.GPUDevice):
    shader_source = load_from_file(SHADERS_PATH/'webgpu'/'unlit_no_bindings.wgsl')

    shader: wgpu.GPUShaderModule = device.create_shader_module(code=shader_source)

    pipeline_layout : wgpu.GPUPipelineLayout = device.create_pipeline_layout(bind_group_layouts=[])

    present_context : wgpu.GPUCanvasContext = canvas.get_context()
    render_texture_format = present_context.get_preferred_format(device.adapter)
    present_context.configure(device=device, format=render_texture_format)

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
        depth_stencil=None,
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
        )

        render_pass.set_pipeline(render_pipeline)
        render_pass.set_vertex_buffer(0, vertex_buffer)
        render_pass.draw(3, 1, 0, 0)
        render_pass.end()
        device.queue.submit([command_encoder.finish()])

        canvas.request_draw()

    canvas.request_draw(draw_frame)
    return device

if __name__ == "__main__":
    canvas = WgpuCanvas(size=(1280, 720), title="wgpu triangle")
    main(canvas)
    run()