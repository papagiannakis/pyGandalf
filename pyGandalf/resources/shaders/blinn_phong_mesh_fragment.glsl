#version 330 core
out vec4 FragColor;

uniform sampler2D u_Textures[16];
uniform float u_TextureId;
uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec3 v_Position;
in vec3 v_Normal;
in vec2 v_TexCoord;

// Light properties
uniform int u_LightCount = 0;
uniform vec3 u_LightPositions[16];
uniform vec3 u_LightColors[16];
uniform float u_LightIntensities[16];

// Material properties
uniform float u_Glossiness = 5.0f;
uniform float u_Metalicness = 5.0f;

// Camera properties
uniform vec3 u_ViewPosition = vec3(0.0, 0.0, 10.0);

void main()
{
    vec3 textureColor;

    int textureID = int(u_TextureId + 0.1);

    switch (textureID)
	{
	case  0: textureColor = texture(u_Textures[0],  v_TexCoord).rgb; break;
	case  1: textureColor = texture(u_Textures[1],  v_TexCoord).rgb; break;
	case  2: textureColor = texture(u_Textures[2],  v_TexCoord).rgb; break;
	case  3: textureColor = texture(u_Textures[3],  v_TexCoord).rgb; break;
	case  4: textureColor = texture(u_Textures[4],  v_TexCoord).rgb; break;
	case  5: textureColor = texture(u_Textures[5],  v_TexCoord).rgb; break;
	case  6: textureColor = texture(u_Textures[6],  v_TexCoord).rgb; break;
	case  7: textureColor = texture(u_Textures[7],  v_TexCoord).rgb; break;
	case  8: textureColor = texture(u_Textures[8],  v_TexCoord).rgb; break;
	case  9: textureColor = texture(u_Textures[9],  v_TexCoord).rgb; break;
	case 10: textureColor = texture(u_Textures[10], v_TexCoord).rgb; break;
	case 11: textureColor = texture(u_Textures[11], v_TexCoord).rgb; break;
	case 12: textureColor = texture(u_Textures[12], v_TexCoord).rgb; break;
	case 13: textureColor = texture(u_Textures[13], v_TexCoord).rgb; break;
	case 14: textureColor = texture(u_Textures[14], v_TexCoord).rgb; break;
	case 15: textureColor = texture(u_Textures[15], v_TexCoord).rgb; break;
    }

    float ambientCoefficient = 0.01;
    vec3 normal = normalize(v_Normal);
    vec3 camDir = normalize(u_ViewPosition - v_Position);
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    vec3 ambient = vec3(0.0);
    
    for (int i = 0; i < u_LightCount; i++)
    {
        // diffuse
        vec3 lightDir = normalize(u_LightPositions[i] - v_Position);
        float diff = max(dot(lightDir, normal), 0.0);
        vec3 D = diff * u_LightColors[i] * u_LightIntensities[i];

        // specular
        vec3 halfwayDir = normalize(lightDir + camDir);  
        float spec = pow(max(dot(normal, halfwayDir), 0.0), 32.0) * u_Glossiness;
        vec3 S = u_LightColors[i] * spec * u_LightIntensities[i];

        diffuse += D;
        specular += S;
        ambient += u_LightColors[i] * u_LightIntensities[i];
    }
    
    ambient = ambientCoefficient * ambient;

    vec3 BlinnPhong = ambient + diffuse + specular; 
    vec3 final = textureColor.rgb * BlinnPhong;
    final = pow(final, vec3(1.0 / 1.2));

    FragColor = vec4(final, 1.0);
}