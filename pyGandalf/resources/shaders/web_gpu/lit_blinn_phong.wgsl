struct VertexInput {
    @location(0) a_Position : vec3<f32>,
    @location(1) a_Normal: vec3<f32>,
    @location(2) a_TexCoord: vec2<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>,
    @location(0) v_Normal : vec3<f32>,
    @location(1) v_TexCoord : vec2<f32>,
};

struct UniformData {
    viewMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
    objectColor: vec4f,
    viewPosition: vec4<f32>,
    lightPositions: array<vec4<f32>, 16>,
    lightColors: array<vec4<f32>, 16>,
    lightIntensities: array<f32, 16>,
    lightCount: f32,
};

struct ModelData {
    modelMatrix: array<mat4x4f>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;
@group(1) @binding(0) var u_Texture: texture_2d<f32>;
@group(1) @binding(1) var u_Sampler: sampler;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    var mvp: mat4x4f = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID];
    out.v_Position = mvp * vec4<f32>(in.a_Position, 1.0);
    out.v_Normal = (u_ModelData.modelMatrix[ID] * vec4f(in.a_Normal, 0.0)).xyz;
    out.v_TexCoord = in.a_TexCoord;
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var textureColor: vec4<f32> = textureSample(u_Texture, u_Sampler, in.v_TexCoord);

    var normal: vec3<f32> = normalize(in.v_Normal);
    var camDir: vec3<f32> = normalize(u_UniformData.viewPosition - in.v_Position).xyz;
    var diffuse: vec3<f32> = vec3<f32>(0.0);
    var specular: vec3<f32> = vec3<f32>(0.0);
    var ambient: vec3<f32> = vec3<f32>(0.0);

    var ambientCoefficient: f32 = 0.1;
    var u_Glossiness: f32 = 3.0;
    var u_LightIntensity: f32 = 1.5;
    var u_LightColor: vec3<f32> = vec3<f32>(1.0, 1.0, 1.0);
    var u_LightPosition: vec3<f32> = vec3<f32>(0.0, 10.0, 0.0);

    for (var i: i32 = 0; i < 1; i = i + 1) {
        // ambient
        ambient = ambient + u_LightColor * u_LightIntensity;

        // diffuse
        var lightDir: vec3<f32> = normalize(u_LightPosition - in.v_Position.xyz);
        var diff: f32 = max(dot(lightDir, normal), 0.0);
        var D: vec3<f32> = diff * u_LightColor * u_LightIntensity;
        diffuse = diffuse + D;

        // specular
        var halfwayDir: vec3<f32> = normalize(lightDir + camDir);
        var spec: f32 = pow(max(dot(normal, halfwayDir), 0.0), 32.0) * u_Glossiness;
        var S: vec3<f32> = u_LightColor * spec * u_LightIntensity;
        specular = specular + S;
    }

    ambient = ambientCoefficient * ambient;

    var BlinnPhong: vec3<f32> = ambient + diffuse + specular;
    var finalColor: vec3<f32> = textureColor.rgb * BlinnPhong;
    finalColor = pow(finalColor, vec3<f32>(1.0 / 1.2));

    // gamma correct
    let physicalColor = pow(finalColor * u_UniformData.objectColor.rgb, vec3<f32>(2.2));
    
    return vec4f(physicalColor.r, physicalColor.g, physicalColor.b, textureColor.a);
}