#version 330 core
layout (location = 0) in vec3 a_Pos;

out vec3 TexCoords;

uniform mat4 u_ViewProjection;

void main()
{
    TexCoords = a_Pos;
    vec4 pos = u_ViewProjection * vec4(a_Pos, 1.0);
    gl_Position = pos.xyww;
} 