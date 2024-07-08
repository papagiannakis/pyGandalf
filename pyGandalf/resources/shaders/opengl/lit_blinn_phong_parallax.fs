#version 330 core
out vec4 FragColor;

uniform sampler2D u_AlbedoMap;
uniform sampler2D u_NormalMap;
uniform sampler2D u_DisplacementMap;

uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec2 v_TexCoord;
in vec3 v_TangentLightPos[16];
in vec3 v_TangentViewPos;
in vec3 v_TangentFragPos;
flat in int v_LightCount;

// Light properties
uniform vec3 u_LightColors[16];
uniform float u_LightIntensities[16];

// Material properties
uniform float u_Glossiness = 5.0f;
uniform float u_Metalicness = 5.0f;

float heightScale = 0.1;

vec2 ParallaxMapping(vec2 texCoords, vec3 viewDir)
{
    float height = texture(u_DisplacementMap, texCoords).r;     
    return texCoords - viewDir.xy * (height * heightScale);
}

void main()
{
    vec3 camDir = normalize(v_TangentViewPos - v_TangentFragPos);
	vec2 offsetTexCoord = ParallaxMapping(v_TexCoord, camDir);

	if (offsetTexCoord.x > 1.0 || offsetTexCoord.y > 1.0 || offsetTexCoord.x < 0.0 || offsetTexCoord.y < 0.0)
    	discard;

    vec3 textureColor;
    textureColor = texture(u_AlbedoMap, offsetTexCoord).rgb;

    vec3 normal;
    normal = texture(u_NormalMap, offsetTexCoord).rgb;

    float ambientCoefficient = 0.1;
    normal = normalize(normal);
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    vec3 ambient = vec3(0.0);
    
    for (int i = 0; i < v_LightCount; i++)
    {
        // diffuse
        vec3 lightDir = normalize(v_TangentLightPos[i] - v_TangentFragPos);
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

    FragColor = vec4(final * u_Color, 1.0);
}