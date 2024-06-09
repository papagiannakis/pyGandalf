struct Uniforms {
    reset: f32,
}

@group(0) @binding(0) var inputTexture: texture_2d<f32>;
@group(0) @binding(1) var outputTexture: texture_storage_2d<rgba8unorm, write>;
@group(0) @binding(2) var<uniform> u_Uniforms: Uniforms;

@compute @workgroup_size(8, 8, 1)
fn computeSobelX(@builtin(global_invocation_id) id: vec3<u32>) {
    var color = vec3f(1.0);

    if (u_Uniforms.reset == 0.0)
    {
        color = abs(
            1 * textureLoad(inputTexture, vec2<u32>(id.x - 1, id.y - 1), 0).rgb
            + 2 * textureLoad(inputTexture, vec2<u32>(id.x - 1, id.y + 0), 0).rgb
            + 1 * textureLoad(inputTexture, vec2<u32>(id.x - 1, id.y + 1), 0).rgb
            - 1 * textureLoad(inputTexture, vec2<u32>(id.x + 1, id.y - 1), 0).rgb
            - 2 * textureLoad(inputTexture, vec2<u32>(id.x + 1, id.y + 0), 0).rgb
            - 1 * textureLoad(inputTexture, vec2<u32>(id.x + 1, id.y + 1), 0).rgb
        );
    }

    textureStore(outputTexture, id.xy, vec4f(color, 1.0));
}