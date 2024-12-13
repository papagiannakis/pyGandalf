#version 330 core
layout(location = 0) in vec3 a_Pos;
layout(location = 1) in vec3 a_Col;

uniform mat4 u_ModelViewProjection;
uniform mat4 u_Model;

out vec3 v_Color;

void main()
{
    gl_Position = u_ModelViewProjection * vec4(a_Pos, 1.0);
    v_Color = a_Col;
}