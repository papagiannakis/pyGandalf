#version 330 core
out vec4 FragColor;

uniform sampler2D u_AlbedoMap;
uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec2 v_TexCoord;

void main()
{
    FragColor = texture(u_AlbedoMap,  v_TexCoord) * vec4(u_Color, 1.0);
}