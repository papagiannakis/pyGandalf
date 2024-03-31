#version 330 core
out vec4 FragColor;

uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);


void main()
{
    FragColor = vec4(u_Color, 1.0);
}