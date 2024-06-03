struct VertexInput {
    @location(0) a_Position : vec3<f32>,
    @location(1) a_Normal : vec3<f32>,
    @location(2) a_TexCoord : vec3<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position : vec4<f32>,
    @location(0) v_Normal : vec3<f32>,
};

struct UniformData {
   viewMatrix: mat4x4f,
   projectionMatrix: mat4x4f,
   viewPosition: vec4<f32>,
};

struct ModelData {
    inverseModelMatrix: array<mat4x4f, 512>,
    modelMatrix: array<mat4x4f, 512>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;
@group(1) @binding(0) var u_SkyTexture: texture_cube<f32>;
@group(1) @binding(1) var u_SkySampler: sampler;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var output : VertexOutput;
    output.v_Normal = (transpose(u_ModelData.inverseModelMatrix[ID]) * vec4(in.a_Normal, 1.0)).xyz;
    output.v_Position = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID] * vec4(in.a_Position, 1.0);
    return output;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var ratio : f32 = 1.00 / 1.52;
    var I : vec3f = normalize(in.v_Position.xyz - u_UniformData.viewPosition.xyz);
    var R : vec3f = refract(I, normalize(in.v_Normal), ratio);
    return vec4f(textureSample(u_SkyTexture, u_SkySampler, R).rgb, 1.0);
}