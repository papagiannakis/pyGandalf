#version 330 core
out vec4 FragColor;

uniform sampler2D u_Textures[16];
uniform float u_TextureId;
uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec2 v_TexCoord;

void main()
{
    int textureID = int(u_TextureId + 0.1);

    switch (textureID)
	{
	case  0: FragColor = texture(u_Textures[0],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  1: FragColor = texture(u_Textures[1],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  2: FragColor = texture(u_Textures[2],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  3: FragColor = texture(u_Textures[3],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  4: FragColor = texture(u_Textures[4],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  5: FragColor = texture(u_Textures[5],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  6: FragColor = texture(u_Textures[6],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  7: FragColor = texture(u_Textures[7],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  8: FragColor = texture(u_Textures[8],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case  9: FragColor = texture(u_Textures[9],  v_TexCoord) * vec4(u_Color, 1.0); break;
	case 10: FragColor = texture(u_Textures[10], v_TexCoord) * vec4(u_Color, 1.0); break;
	case 11: FragColor = texture(u_Textures[11], v_TexCoord) * vec4(u_Color, 1.0); break;
	case 12: FragColor = texture(u_Textures[12], v_TexCoord) * vec4(u_Color, 1.0); break;
	case 13: FragColor = texture(u_Textures[13], v_TexCoord) * vec4(u_Color, 1.0); break;
	case 14: FragColor = texture(u_Textures[14], v_TexCoord) * vec4(u_Color, 1.0); break;
	case 15: FragColor = texture(u_Textures[15], v_TexCoord) * vec4(u_Color, 1.0); break;
    }
}