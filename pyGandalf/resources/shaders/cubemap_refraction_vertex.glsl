#version 330 core
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec3 a_Normal;
layout(location = 2) in vec2 a_TexCoord;

out vec3 v_Normal;
out vec3 v_Position;

uniform mat4 u_ModelViewProjection;
uniform mat4 u_Model;

void main()
{
    v_Normal = mat3(transpose(inverse(u_Model))) * a_Normal;
    v_Position = vec3(u_Model * vec4(a_Position, 1.0));
    gl_Position = u_ModelViewProjection * vec4(a_Position, 1.0);
}