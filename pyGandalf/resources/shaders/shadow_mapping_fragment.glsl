#version 330 core
out vec4 FragColor;

uniform sampler2D u_AlbedoMap;
uniform sampler2D u_ShadowMap;
uniform vec3 u_Color = vec3(1.0, 1.0, 1.0);

in vec3 v_Position;
in vec3 v_Normal;
in vec2 v_TexCoord;
in vec4 v_FragPosLightSpace;

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

float ShadowCalculation(vec4 fragPosLightSpace)
{
    // perform perspective divide
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    // transform to [0,1] range
    projCoords = projCoords * 0.5 + 0.5;
    // get closest depth value from light's perspective (using [0,1] range fragPosLight as coords)
    float closestDepth = texture(u_ShadowMap, projCoords.xy).r; 
    // get depth of current fragment from light's perspective
    float currentDepth = projCoords.z;

    // calculate bias (based on depth map resolution and slope)
    vec3 normal = normalize(v_Normal);
    vec3 lightDir = normalize(u_LightPositions[u_LightCount - 1] - v_Position);
    float bias = max(0.01 * (1.0 - dot(normal, lightDir)), 0.0025);

    // PCF
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(u_ShadowMap, 0);
    for(int x = -1; x <= 1; ++x)
    {
        for(int y = -1; y <= 1; ++y)
        {
            float pcfDepth = texture(u_ShadowMap, projCoords.xy + vec2(x, y) * texelSize).r; 
            shadow += currentDepth - bias > pcfDepth  ? 1.0 : 0.0;        
        }    
    }
    shadow /= 9.0;

    if (projCoords.z > 1.0)
        shadow = 0.0;
    
    return shadow;
}

void main()
{
    vec3 textureColor;

    textureColor = texture(u_AlbedoMap, v_TexCoord).rgb;

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

    float shadow = ShadowCalculation(v_FragPosLightSpace); 

    vec3 BlinnPhong = (ambient + (1.0 - shadow) * (diffuse + specular));
    vec3 final = textureColor.rgb * BlinnPhong;
    final = pow(final, vec3(1.0 / 1.2));

    FragColor = vec4(final * u_Color, 1.0);
}