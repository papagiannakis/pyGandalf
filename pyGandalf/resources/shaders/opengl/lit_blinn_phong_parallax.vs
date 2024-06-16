#version 330 core
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec3 a_Normal;
layout(location = 2) in vec2 a_TexCoord;
layout(location = 3) in vec3 a_Tangent;
layout(location = 4) in vec3 a_Bitangent;

uniform mat4 u_ModelViewProjection;
uniform mat4 u_Model;
uniform vec3 u_LightPositions[16];
uniform int u_LightCount = 0;
uniform vec3 u_ViewPosition = vec3(0.0, 0.0, 10.0);

out vec2 v_TexCoord;
out vec3 v_TangentLightPos[16];
out vec3 v_TangentViewPos;
out vec3 v_TangentFragPos;
flat out int v_LightCount;

void main()
{
    vec3 T = normalize(mat3(u_Model) * a_Tangent);
    vec3 B = normalize(mat3(u_Model) * a_Bitangent);
    vec3 N = normalize(mat3(u_Model) * a_Normal);

    mat3 TBN = transpose(mat3(T, B, N));

    v_TexCoord = a_TexCoord;

    for (int i = 0; i < u_LightCount; i++)
    {
        v_TangentLightPos[i] = TBN * u_LightPositions[i];
    }

    v_TangentViewPos = TBN * u_ViewPosition;
    v_TangentFragPos = TBN * (u_Model * vec4(a_Position, 1.0)).xyz;

    v_LightCount = u_LightCount;

    gl_Position = u_ModelViewProjection * vec4(a_Position, 1.0);
}