#version 330 core
out vec4 FragColor;

uniform sampler2D u_Textures[16];
uniform float u_TextureId;

in vec2 v_TexCoord;

void main()
{
    int id = int(u_TextureId);
    FragColor = texture(u_Textures[id], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
}