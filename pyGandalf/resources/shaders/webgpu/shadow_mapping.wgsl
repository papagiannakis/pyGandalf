struct VertexInput {
    @location(0) a_Position : vec3<f32>,
    @location(1) a_Normal: vec3<f32>,
    @location(2) a_TexCoord: vec2<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>,
    @location(0) v_Normal : vec3<f32>,
    @location(1) v_TexCoord : vec2<f32>,
    @location(2) v_WorldPosition : vec3<f32>,
    @location(2) v_FragPosLightSpace : vec3<f32>,
};

struct UniformData {
    viewMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
    lightSpaceMatrix: mat4x4f,
    objectColor: vec4f,
    viewPosition: vec4<f32>,
    lightPositions: array<vec4f, 16>,
    lightColors: array<vec4f, 16>,
    lightIntensities: array<vec4f, 16>,
    lightCount: f32,
};

struct ModelData {
    modelMatrix: array<mat4x4f, 512>,
    inverseModelMatrix: array<mat4x4f, 512>,
};

@group(0) @binding(0) var<uniform> u_UniformData: UniformData;
@group(0) @binding(1) var<storage, read> u_ModelData: ModelData;
@group(1) @binding(0) var u_AlbedoMap: texture_2d<f32>;
@group(1) @binding(1) var u_AlbedoSampler: sampler;
@group(1) @binding(2) var u_ShadowMap: texture_2d<f32>;
@group(1) @binding(3) var u_ShadowSampler: sampler;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    var mvp: mat4x4f = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID];
    out.v_Position = mvp * vec4<f32>(in.a_Position, 1.0);
    out.v_WorldPosition = (u_ModelData.modelMatrix[ID] * vec4f(in.a_Position, 1.0)).xyz;
    out.v_Normal = (transpose(u_ModelData.inverseModelMatrix[ID]) * vec4f(in.a_Normal, 0.0)).xyz;
    out.v_FragPosLightSpace = u_UniformData.lightSpaceMatrix * vec4(out.v_WorldPosition, 1.0);
    out.v_TexCoord = in.a_TexCoord;
    return out;
}

fn ShadowCalculation(fragPosLightSpace: vec4f) -> f32
{
    // perform perspective divide
    var projCoords: vec3f = fragPosLightSpace.xyz / fragPosLightSpace.w;
    // transform to [0,1] range
    projCoords = projCoords * 0.5 + 0.5;
    // get closest depth value from light's perspective (using [0,1] range fragPosLight as coords)
    var closestDepth: f32 = texture(u_ShadowMap, projCoords.xy).r; 
    // get depth of current fragment from light's perspective
    var currentDepth: f32 = projCoords.z;

    // calculate bias (based on depth map resolution and slope)
    var normal: vec3f = normalize(v_Normal);
    var lightDir: vec3f = normalize(u_LightPositions[u_LightCount - 1] - v_Position);
    var bias: f32 = max(0.005 * (1.0 - dot(normal, lightDir)), 0.001);

    // PCF
    var shadow: f32 = 0.0;
    var texelSize: vec2f = 1.0 / textureSize(u_ShadowMap, 0);
    for(var x: i32 = -1; x <= 1; x = x + 1)
    {
        for(var y: i32 = -1; y <= 1; y = y + 1)
        {
            var pcfDepth: f32 = textureSample(u_ShadowMap, u_ShadowSampler, projCoords.xy + vec2f(x, y) * texelSize).r; 
            shadow += currentDepth - bias > pcfDepth  ? 1.0 : 0.0;        
        }    
    }
    shadow /= 9.0;

    if (projCoords.z > 1.0)
        shadow = 0.0;
    
    return shadow;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var textureColor: vec4<f32> = textureSample(u_AlbedoMap, u_AlbedoSampler, in.v_TexCoord);

    var normal: vec3<f32> = normalize(in.v_Normal);
    var camDir: vec3<f32> = normalize(u_UniformData.viewPosition - vec4<f32>(in.v_WorldPosition, 1.0)).xyz;
    var diffuse: vec3<f32> = vec3<f32>(0.0);
    var specular: vec3<f32> = vec3<f32>(0.0);
    var ambient: vec3<f32> = vec3<f32>(0.0);

    var ambientCoefficient: f32 = 0.1;
    var u_Glossiness: f32 = 5.0;

    for (var f: f32 = 0.0; f < u_UniformData.lightCount; f = f + 1.0) {
        var i: i32 = i32(f);

        // ambient
        ambient = ambient + u_UniformData.lightColors[i].rgb * u_UniformData.lightIntensities[i].x;

        // diffuse
        var lightDir: vec3<f32> = normalize(u_UniformData.lightPositions[i].xyz - in.v_WorldPosition);
        var diff: f32 = max(dot(lightDir, normal), 0.0);
        var D: vec3<f32> = diff * u_UniformData.lightColors[i].rgb * u_UniformData.lightIntensities[i].x;
        diffuse = diffuse + D;

        // specular
        var halfwayDir: vec3<f32> = normalize(lightDir + camDir);
        var spec: f32 = pow(max(dot(normal, halfwayDir), 0.0), 32.0) * u_Glossiness;
        var S: vec3<f32> = u_UniformData.lightColors[i].rgb * spec * u_UniformData.lightIntensities[i].x;
        specular = specular + S;
    }

    ambient = ambientCoefficient * ambient;

    var shadow: f32 = ShadowCalculation(in.v_FragPosLightSpace); 

    var BlinnPhong: vec3<f32> = (ambient + (1.0 - shadow) * (diffuse + specular));
    var finalColor: vec3<f32> = textureColor.rgb * BlinnPhong;
    finalColor = pow(finalColor, vec3<f32>(1.0 / 1.2));

    // gamma correct
    let physicalColor = pow(finalColor * u_UniformData.objectColor.rgb, vec3<f32>(2.2));
    
    return vec4f(physicalColor.r, physicalColor.g, physicalColor.b, textureColor.a);
}