#version 330 core
out vec4 FragColor;

uniform sampler2D u_AlbedoMap;
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

    textureColor = texture(u_AlbedoMap,  v_TexCoord).rgb;

    float ambientCoefficient = 0.1;
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

    FragColor = vec4(final * u_Color, 1.0);
}