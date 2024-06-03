struct VertexInput {
    @location(0) a_Position : vec3<f32>,
    @location(1) a_Normal: vec3<f32>,
    @location(2) a_TexCoord: vec2<f32>,
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>,
    @location(0) v_Normal : vec3<f32>,
    @location(1) v_TexCoord : vec2<f32>,
    @location(2) v_CurrentPosition : vec3<f32>,
};

struct UniformData {
    viewMatrix: mat4x4f,
    projectionMatrix: mat4x4f,
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
@group(1) @binding(2) var u_NormalMap: texture_2d<f32>;
@group(1) @binding(3) var u_NormalSampler: sampler;
@group(1) @binding(4) var u_MetallicMap: texture_2d<f32>;
@group(1) @binding(5) var u_MetallicSampler: sampler;
@group(1) @binding(6) var u_RoughnessMap: texture_2d<f32>;
@group(1) @binding(7) var u_RoughnessSampler: sampler;

@vertex
fn vs_main(@builtin(instance_index) ID: u32, in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    var mvp: mat4x4f = u_UniformData.projectionMatrix * u_UniformData.viewMatrix * u_ModelData.modelMatrix[ID];
    out.v_Position = mvp * vec4<f32>(in.a_Position, 1.0);
    out.v_CurrentPosition = (u_ModelData.modelMatrix[ID] * vec4f(in.a_Position, 1.0)).xyz;
    out.v_Normal = (transpose(u_ModelData.inverseModelMatrix[ID]) * vec4f(in.a_Normal, 0.0)).xyz;
    out.v_TexCoord = in.a_TexCoord;
    return out;
}

const PI = 3.14159265359;

// Easy trick to get tangent-normals to world-space to keep PBR code simplified.
// Don't worry if you don't get what's going on; you generally want to do normal 
// mapping the usual way for performance anyways; I do plan make a note of this 
// technique somewhere later in the normal mapping tutorial.
fn getNormalFromMap(currentPosition: vec3f, texCoord: vec2f, normal: vec3f) -> vec3f
{
    var tangentNormal: vec3f = textureSample(u_NormalMap, u_NormalSampler, texCoord).xyz * 2.0 - 1.0;

    var Q1: vec3f = dpdx(currentPosition);
    var Q2: vec3f = dpdy(currentPosition);
    var st1: vec2f = dpdx(texCoord);
    var st2: vec2f = dpdy(texCoord);

    var N: vec3f = normalize(normal);
    var T: vec3f = normalize(Q1 * st2.y - Q2 * st1.y);
    var B: vec3f = -normalize(cross(N, T));
    var TBN: mat3x3f = mat3x3f(T, B, N);

    return normalize(TBN * tangentNormal);
}

fn DistributionGGX(N: vec3f, H: vec3f, roughness: f32) -> f32
{
    var a: f32 = roughness * roughness;
    var a2: f32 = a * a;
    var NdotH: f32 = max(dot(N, H), 0.0);
    var NdotH2: f32 = NdotH * NdotH;

    var nom: f32   = a2;
    var denom: f32 = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;

    return nom / denom;
}

fn GeometrySchlickGGX(NdotV: f32, roughness: f32) -> f32
{
    var r: f32 = (roughness + 1.0);
    var k: f32 = (r * r) / 8.0;

    var nom: f32   = NdotV;
    var denom: f32 = NdotV * (1.0 - k) + k;

    return nom / denom;
}

fn GeometrySmith(N: vec3f, V: vec3f, L: vec3f, roughness: f32) -> f32
{
    var NdotV: f32 = max(dot(N, V), 0.0);
    var NdotL: f32 = max(dot(N, L), 0.0);
    var ggx2: f32 = GeometrySchlickGGX(NdotV, roughness);
    var ggx1: f32 = GeometrySchlickGGX(NdotL, roughness);

    return ggx1 * ggx2;
}

fn fresnelSchlick(cosTheta: f32, F0: vec3f) -> vec3f
{
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var albedo: vec3f  = pow(textureSample(u_AlbedoMap, u_AlbedoSampler, in.v_TexCoord).rgb, vec3(2.2));
    var metallic: f32  = textureSample(u_MetallicMap, u_MetallicSampler, in.v_TexCoord).r;
    var roughness: f32 = textureSample(u_RoughnessMap, u_RoughnessSampler, in.v_TexCoord).r;

    var N: vec3f = getNormalFromMap(in.v_CurrentPosition, in.v_TexCoord, in.v_Normal);
    var V: vec3f = normalize(u_UniformData.viewPosition.xyz - in.v_CurrentPosition);

    // calculate reflectance at normal incidence; if dia-electric (like plastic) use F0 
    // of 0.04 and if it's a metal, use the albedo color as F0 (metallic workflow)    
    var F0: vec3f = vec3f(0.04); 
    F0 = mix(F0, albedo, metallic);

    // reflectance equation
    var Lo: vec3f = vec3f(0.0);
    for (var f: f32 = 0.0; f < u_UniformData.lightCount; f = f + 1.0) {
        var i: i32 = i32(f);

        // calculate per-light radiance
        var L: vec3f = normalize(u_UniformData.lightPositions[i].xyz - in.v_CurrentPosition);
        var H: vec3f = normalize(V + L);
        var distance: f32 = length(u_UniformData.lightPositions[i].xyz - in.v_CurrentPosition);
        var attenuation: f32 = 1.0 / (distance * distance);
        var radiance: vec3f = u_UniformData.lightColors[i].rgb * attenuation * u_UniformData.lightIntensities[i].x;

        // Cook-Torrance BRDF
        var NDF: f32 = DistributionGGX(N, H, roughness);   
        var G: f32   = GeometrySmith(N, V, L, roughness);      
        var F: vec3f = fresnelSchlick(max(dot(H, V), 0.0), F0);
           
        var numerator: vec3f = NDF * G * F; 
        var denominator: f32 = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001; // + 0.0001 to prevent divide by zero
        var specular: vec3f = numerator / denominator;
        
        // kS is equal to Fresnel
        var kS: vec3f = F;
        // for energy conservation, the diffuse and specular light can't
        // be above 1.0 (unless the surface emits light); to preserve this
        // relationship the diffuse component (kD) should equal 1.0 - kS.
        var kD: vec3f = vec3(1.0) - kS;
        // multiply kD by the inverse metalness such that only non-metals 
        // have diffuse lighting, or a linear blend if partly metal (pure metals
        // have no diffuse light).
        kD *= 1.0 - metallic;	  

        // scale light by NdotL
        var NdotL: f32 = max(dot(N, L), 0.0);        

        // add to outgoing radiance Lo
        Lo += (kD * albedo / PI + specular) * radiance * NdotL;  // note that we already multiplied the BRDF by the Fresnel (kS) so we won't multiply by kS again
    }

    // ambient lighting (note that the next IBL tutorial will replace 
    // this ambient lighting with environment lighting).
    var ambient: vec3f = vec3(0.05) * albedo;
    
    var color: vec3f = ambient + Lo;

    // HDR tonemapping
    color = color / (color + vec3f(1.0));
    // gamma correct
    color = pow(color, vec3f(1.0 / 1.5)); 

    return vec4f(color * u_UniformData.objectColor.xyz, 1.0);
}