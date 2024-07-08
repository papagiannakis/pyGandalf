#version 330 core
out vec4 FragColor;

in vec3 v_Normal;
in vec3 v_Position;

uniform vec3 u_ViewPosition;
uniform samplerCube u_Skybox;

void main()
{             
    vec3 I = normalize(v_Position - u_ViewPosition);
    vec3 R = reflect(I, normalize(v_Normal));
    FragColor = vec4(texture(u_Skybox, R).rgb, 1.0);
}