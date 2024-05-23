#version 410 core

in float v_Height;

out vec4 FragColor;

void main()
{
    float h = (v_Height + 16)/64.0f;
    FragColor = vec4(h, h, h, 1.0);
}