struct VertexInput {
    @location(0) a_Position : vec3<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>,
};

struct UniformData {
    lightSpaceMatrix: mat4x4f,
};

struct ModelData {
    modelMatrix: array<mat4x4f>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    out.v_Position = u_UniformData.lightSpaceMatrix * u_ModelData.modelMatrix[ID] * vec4<f32>(in.a_Position, 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // Noop
}