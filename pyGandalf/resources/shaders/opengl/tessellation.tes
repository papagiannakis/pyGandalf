// tessellation evaluation shader
#version 410 core

layout (quads, fractional_odd_spacing, ccw) in;

uniform sampler2D u_HeightMap;  // the texture corresponding to our height map
uniform mat4 u_Model;           // the model matrix
uniform mat4 u_View;            // the view matrix
uniform mat4 u_Projection;      // the projection matrix

// received from Tessellation Control Shader - all texture coordinates for the patch vertices
in vec2 v_TextureCoord[];

// send to Fragment Shader for coloring
out float v_Height;

void main()
{
    // get patch coordinate
    float u = gl_TessCoord.x;
    float v = gl_TessCoord.y;

    // ----------------------------------------------------------------------
    // retrieve control point texture coordinates
    vec2 t00 = v_TextureCoord[0];
    vec2 t01 = v_TextureCoord[1];
    vec2 t10 = v_TextureCoord[2];
    vec2 t11 = v_TextureCoord[3];

    // bilinearly interpolate texture coordinate across patch
    vec2 t0 = (t01 - t00) * u + t00;
    vec2 t1 = (t11 - t10) * u + t10;
    vec2 texCoord = (t1 - t0) * v + t0;

    // lookup texel at patch coordinate for height and scale + shift as desired
    v_Height = texture(u_HeightMap, texCoord).y * 64.0 - 16.0;

    // ----------------------------------------------------------------------
    // retrieve control point position coordinates
    vec4 p00 = gl_in[0].gl_Position;
    vec4 p01 = gl_in[1].gl_Position;
    vec4 p10 = gl_in[2].gl_Position;
    vec4 p11 = gl_in[3].gl_Position;

    // compute patch surface normal
    vec4 uVec = p01 - p00;
    vec4 vVec = p10 - p00;
    vec4 normal = normalize( vec4(cross(vVec.xyz, uVec.xyz), 0) );

    // bilinearly interpolate position coordinate across patch
    vec4 p0 = (p01 - p00) * u + p00;
    vec4 p1 = (p11 - p10) * u + p10;
    vec4 p = (p1 - p0) * v + p0;

    // displace point along normal
    p += normal * v_Height;

    // ----------------------------------------------------------------------
    // output patch point position in clip space
    gl_Position = u_Projection * u_View * u_Model * p;
}