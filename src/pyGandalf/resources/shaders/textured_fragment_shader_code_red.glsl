#version 330 core
out vec4 FragColor;

uniform sampler2D u_Textures[16];
uniform float u_TextureId;

in vec2 v_TexCoord;

void main()
{
    if (u_TextureId == 0.0)
    {
        FragColor = texture(u_Textures[0], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 1.0)
    {
        FragColor = texture(u_Textures[1], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 2.0)
    {
        FragColor = texture(u_Textures[2], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 3.0)
    {
        FragColor = texture(u_Textures[3], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 4.0)
    {
        FragColor = texture(u_Textures[4], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 5.0)
    {
        FragColor = texture(u_Textures[5], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 6.0)
    {
        FragColor = texture(u_Textures[6], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 7.0)
    {
        FragColor = texture(u_Textures[7], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 8.0)
    {
        FragColor = texture(u_Textures[8], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 9.0)
    {
        FragColor = texture(u_Textures[9], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 10.0)
    {
        FragColor = texture(u_Textures[10], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 11.0)
    {
        FragColor = texture(u_Textures[11], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 12.0)
    {
        FragColor = texture(u_Textures[12], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 13.0)
    {
        FragColor = texture(u_Textures[13], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 14.0)
    {
        FragColor = texture(u_Textures[14], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
    else if (u_TextureId == 15.0)
    {
        FragColor = texture(u_Textures[15], v_TexCoord) * vec4(1.0, 0.0, 0.0, 0.0);
    }
}