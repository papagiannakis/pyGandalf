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

vec2 SteepParallaxMapping(vec2 texCoords, vec3 viewDir)
{
    // number of depth layers
    const float minLayers = 8;
    const float maxLayers = 32;
    float numLayers = mix(maxLayers, minLayers, abs(dot(vec3(0.0, 0.0, 1.0), viewDir)));  
    
    // calculate the size of each layer
    float layerDepth = 1.0 / numLayers;
    // depth of current layer
    float currentLayerDepth = 0.0;
    // the amount to shift the texture coordinates per layer (from vector P)
    vec2 P = viewDir.xy / viewDir.z * heightScale; 
    vec2 deltaTexCoords = P / numLayers;
  
    // get initial values
    vec2  currentTexCoords = texCoords;
    float currentDepthMapValue = texture(u_DisplacementMap, currentTexCoords).r;
      
    while(currentLayerDepth < currentDepthMapValue)
    {
        // shift texture coordinates along direction of P
        currentTexCoords -= deltaTexCoords;
        // get depthmap value at current texture coordinates
        currentDepthMapValue = texture(u_DisplacementMap, currentTexCoords).r;  
        // get depth of next layer
        currentLayerDepth += layerDepth;  
    }
    
    return currentTexCoords;
}

void main()
{
    vec3 camDir = normalize(v_TangentViewPos - v_TangentFragPos);
	vec2 offsetTexCoord = SteepParallaxMapping(v_TexCoord, camDir);

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