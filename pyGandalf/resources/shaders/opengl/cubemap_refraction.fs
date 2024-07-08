#version 330 core
out vec4 FragColor;

in vec3 v_Normal;
in vec3 v_Position;

uniform vec3 u_ViewPosition;
uniform samplerCube u_Skybox;

void main()
{             
    float ratio = 1.00 / 1.52;
    vec3 I = normalize(v_Position - u_ViewPosition);
    vec3 R = refract(I, normalize(v_Normal), ratio);
    FragColor = vec4(texture(u_Skybox, R).rgb, 1.0);
}