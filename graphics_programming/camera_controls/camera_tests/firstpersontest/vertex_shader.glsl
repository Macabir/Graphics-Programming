#version 330 core

// The 'layout' keyword specifies the location of the vertex attributes
// 'aPos' is the vertex position, 'aColor' is the vertex color
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

// 'out' variables pass data from the vertex shader to the fragment shader
out vec3 FragColor;

// 'uniform' variables are global and read-only, set by the CPU
// We use them here for our transformation matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // The core of the vertex shader:
    // Transform the vertex position by the model, view, and projection matrices.
    // gl_Position is a built-in variable that holds the final transformed position.
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    // Pass the color to the fragment shader for interpolation
    FragColor = aColor;
}