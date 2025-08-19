#version 330 core

// 'in' variables receive data from the previous shader stage (the vertex shader)
// 'FragColor' is the color interpolated from the vertices
in vec3 FragColor;

// 'out' variables are written to the screen buffer
// 'color' is the final output color for the fragment
out vec4 color;

void main() {
    // The core of the fragment shader:
    // Set the final output color. The vec4 takes the RGB color and a transparency (alpha) value.
    color = vec4(FragColor, 1.0);
}