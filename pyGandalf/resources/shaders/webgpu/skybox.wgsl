struct VertexInput {
    @location(0) a_Position : vec3<f32>
};
struct VertexOutput {
    @builtin(position) v_Position : vec4<f32>,
    @location(0) v_TextureCoords : vec3<f32>,
};

struct UniformData {
   viewProjection: mat4x4f,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(1) @binding(0) var u_SkyTexture: texture_cube<f32>;
@group(1) @binding(1) var u_SkySampler: sampler;

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var position: vec4f = u_UniformData.viewProjection * vec4f(in.a_Position, 1.0);

    var output : VertexOutput;
    output.v_TextureCoords = in.a_Position;
    output.v_Position = position.xyww;
    return output;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> { 
    return textureSample(u_SkyTexture, u_SkySampler, in.v_TextureCoords);
}