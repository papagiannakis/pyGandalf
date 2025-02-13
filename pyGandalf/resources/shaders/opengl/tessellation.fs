#version 410 core

in float v_Height;

out vec4 FragColor;

void main()
{
    float h = (v_Height + 16.0)/64.0;
    FragColor = vec4(h - 0.25, h - 0.25, h + 0.25, 1.0);
}