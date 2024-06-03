struct VertexInput {
    @location(0) a_Position : vec3<f32>
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>
};

struct UniformData {
    viewMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
    objectColor: vec4f,
};

struct ModelData {
    modelMatrix: array<mat4x4f>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    var mvp: mat4x4f = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID];
    out.v_Position = mvp * vec4<f32>(in.a_Position, 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // gamma correct
    let physical_color = pow(u_UniformData.objectColor.rgb, vec3<f32>(2.2));
    return vec4<f32>(physical_color, u_UniformData.objectColor.a);
}