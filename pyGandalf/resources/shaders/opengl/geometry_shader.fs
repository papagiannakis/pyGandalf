#version 330 core
out vec4 FragColor;

in vec2 v_TexCoords;

uniform sampler2D u_AlbedoMap;

void main()
{
    FragColor = texture(u_AlbedoMap, v_TexCoords);
}