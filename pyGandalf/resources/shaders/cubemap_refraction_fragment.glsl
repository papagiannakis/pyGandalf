#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 Position;

uniform vec3 u_ViewPosition;
uniform samplerCube u_Skybox;

void main()
{             
    float ratio = 1.00 / 1.52;
    vec3 I = normalize(Position - u_ViewPosition);
    vec3 R = refract(I, normalize(Normal), ratio);
    FragColor = vec4(texture(u_Skybox, R).rgb, 1.0);
}