struct VertexInput {
    @location(0) a_Position : vec3<f32>,
    @location(1) a_TexCoord: vec2<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>,
    @location(0) v_TexCoord : vec2<f32>,
    @location(1) v_FragPosLightSpace : vec4<f32>,
};

struct UniformData {
    viewMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
    lightSpaceMatrix: mat4x4f,
    objectColor: vec4f,
};

struct ModelData {
    modelMatrix: array<mat4x4f, 512>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;
@group(1) @binding(0) var u_Texture: texture_depth_2d;
@group(1) @binding(1) var u_Sampler: sampler_comparison;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    var mvp: mat4x4f = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID];
    out.v_Position = mvp * vec4<f32>(in.a_Position, 1.0);
    out.v_TexCoord = in.a_TexCoord;
    out.v_FragPosLightSpace = u_UniformData.lightSpaceMatrix * vec4(u_ModelData.modelMatrix[ID] * vec4f(in.a_Position, 1.0));
    return out;
}

const near_plane: f32 = 1.0;
const far_plane: f32 = 7.5;

// required when using a perspective projection matrix
fn LinearizeDepth(depth: f32) -> f32
{
    var z: f32 = depth * 2.0 - 1.0; // Back to NDC 
    return (2.0 * near_plane * far_plane) / (far_plane + near_plane - z * (far_plane - near_plane));	
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // perform perspective divide
    var projCoords: vec3f = in.v_FragPosLightSpace.xyz / in.v_FragPosLightSpace.w;
    // transform to [0,1] range
    projCoords = projCoords * 0.5 + 0.5;
    var depthValue: f32 = textureSampleCompare(u_Texture, u_Sampler, in.v_TexCoord, in.v_Position.z / in.v_Position.w);
    return vec4f(vec3f(LinearizeDepth(depthValue) / far_plane), 1.0); // perspective
}