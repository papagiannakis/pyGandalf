#version 330 core
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec3 a_Normal;
layout(location = 2) in vec2 a_TexCoord;

uniform mat4 u_ViewProjection;
uniform mat4 u_Model;

out vec3 v_Position;
out vec3 v_Normal;
out vec2 v_TexCoord;

void main()
{
    v_Position = a_Position;
    v_Normal = (u_Model * vec4(a_Normal, 0.0)).xyz;
    v_TexCoord = a_TexCoord;

    gl_Position = u_ViewProjection * u_Model * vec4(a_Position, 1.0);
}