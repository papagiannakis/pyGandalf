#version 330 core
out vec4 FragColor;

uniform sampler2D u_Textures[16];
uniform float u_TextureId;
uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec3 v_Position;
in vec3 v_Normal;
in vec2 v_TexCoord;

uniform vec3 lightPos = vec3(0.0, 5.0, 0.0);
uniform vec3 viewPos = vec3(0.0, 0.0, 10.0);

void main()
{
    vec3 color;

    int textureID = int(u_TextureId + 0.1);

    switch (textureID)
	{
	case  0: color = texture(u_Textures[0],  v_TexCoord).rgb; break;
	case  1: color = texture(u_Textures[1],  v_TexCoord).rgb; break;
	case  2: color = texture(u_Textures[2],  v_TexCoord).rgb; break;
	case  3: color = texture(u_Textures[3],  v_TexCoord).rgb; break;
	case  4: color = texture(u_Textures[4],  v_TexCoord).rgb; break;
	case  5: color = texture(u_Textures[5],  v_TexCoord).rgb; break;
	case  6: color = texture(u_Textures[6],  v_TexCoord).rgb; break;
	case  7: color = texture(u_Textures[7],  v_TexCoord).rgb; break;
	case  8: color = texture(u_Textures[8],  v_TexCoord).rgb; break;
	case  9: color = texture(u_Textures[9],  v_TexCoord).rgb; break;
	case 10: color = texture(u_Textures[10], v_TexCoord).rgb; break;
	case 11: color = texture(u_Textures[11], v_TexCoord).rgb; break;
	case 12: color = texture(u_Textures[12], v_TexCoord).rgb; break;
	case 13: color = texture(u_Textures[13], v_TexCoord).rgb; break;
	case 14: color = texture(u_Textures[14], v_TexCoord).rgb; break;
	case 15: color = texture(u_Textures[15], v_TexCoord).rgb; break;
    }

    // ambient
    vec3 ambient = 0.1 * color;

    // diffuse
    vec3 lightDir = normalize(lightPos - v_Position);
    vec3 normal = normalize(v_Normal);
    float diff = max(dot(lightDir, normal), 0.0);
    vec3 diffuse = diff * color;

    // specular
    vec3 viewDir = normalize(viewPos - v_Position);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = 0.0;

    vec3 halfwayDir = normalize(lightDir + viewDir);  
    spec = pow(max(dot(normal, halfwayDir), 0.0), 32.0);

    vec3 specular = vec3(0.65) * spec; // assuming bright white light color

    FragColor = vec4(ambient + diffuse + specular, 1.0) * vec4(u_Color, 1.0);
}