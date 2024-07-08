#version 330 core
layout (location = 0) in vec3 a_Pos;
layout (location = 2) in vec2 a_TexCoords;

out VS_OUT {
    vec2 texCoords;
} vs_out;

uniform mat4 u_ModelViewProjection;

void main()
{
    vs_out.texCoords = a_TexCoords;
    gl_Position = u_ModelViewProjection * vec4(a_Pos, 1.0); 
}