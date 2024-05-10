#version 330 core
layout(location = 0) in vec3 a_Pos;

uniform mat4 u_ModelViewProjection;
uniform mat4 u_Model;

void main()
{
    gl_Position = u_ModelViewProjection * vec4(a_Pos, 1.0);
}