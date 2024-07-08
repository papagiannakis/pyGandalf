struct VertexInput {
    @location(0) a_Position : vec3<f32>
};
struct VertexOutput {
    @builtin(position) v_Position: vec4<f32>
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    out.v_Position = vec4<f32>(in.a_Position, 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // gamma correct
    let physical_color = pow(vec3<f32>(1.0, 1.0, 1.0), vec3<f32>(2.2));
    return vec4<f32>(physical_color, 1.0);
}