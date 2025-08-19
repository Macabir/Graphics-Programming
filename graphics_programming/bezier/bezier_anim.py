import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
import math

# --- 1. Shaders ---
# The Vertex Shader: This is where the calculus and animation happen.
# `gl_VertexID` gives us an integer from 0 to NUM_POINTS-1.
# This is converted to `t`, which iterates from 0.0 to 1.0 along the curve.
vertex_shader_source = """
#version 330 core

// The 4 control points
uniform vec3 control_points[4];

void main()
{
    float num_points = 1000.0;
    float t = float(gl_VertexID) / num_points;

    // This is the cubic Bezier formula (Bernstein polynomials):
    // B(t) = (1-t)^3 * P0 + 3 * (1-t)^2 * t * P1 + 3 * (1-t) * t^2 * P2 + t^3 * P3
    vec3 position = pow((1.0 - t), 3.0) * control_points[0] +
                    3.0 * pow((1.0 - t), 2.0) * t * control_points[1] +
                    3.0 * (1.0 - t) * pow(t, 2.0) * control_points[2] +
                    pow(t, 3.0) * control_points[3];

    gl_Position = vec4(position, 1.0);
}
"""

# The Fragment Shader: Just makes every point on the curve a solid color.
fragment_shader_source = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0f, 0.5f, 0.0f, 1.0f); // A solid orange color
}
"""

def main():
    if not glfw.init():
        return

    # Set OpenGL version hints
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(800, 600, "Animated Bezier Curve", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Compile and link shaders
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # Create and bind a VAO.
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # We still need a dummy VBO to keep the state valid, even if it's empty
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    # Get the uniform location for the control points array in the shader
    control_points_loc = glGetUniformLocation(shader_program, "control_points")

    glClearColor(0.2, 0.3, 0.3, 1.0)
    glUseProgram(shader_program)
    
    # Main render loop
    while not glfw.window_should_close(window):
        # Get the current time for animation
        time = glfw.get_time()

        # --- ANIMATION ---
        # We will use sine and cosine to smoothly move the control points
        # The first and last points are static
        p0 = [-0.8, -0.8, 0.0]
        p3 = [0.8, 0.8, 0.0]
        
        # The middle two points move in a circular motion
        p1_x = math.sin(time) * 0.4
        p1_y = math.cos(time) * 0.8
        p1 = [p1_x, p1_y, 0.0]
        
        p2_x = math.cos(time) * 0.6
        p2_y = math.sin(time) * -0.6
        p2 = [p2_x, p2_y, 0.0]

        # Combine the points into an array to pass to the shader
        animated_control_points = np.array([p0, p1, p2, p3], dtype=np.float32)

        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(VAO)
        
        # Pass the animated control points to the shader
        glUniform3fv(control_points_loc, 4, animated_control_points)

        # Draw the curve by rendering 1000 points connected by a line strip.
        glDrawArrays(GL_LINE_STRIP, 0, 1000)
        
        glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteBuffers(1, VBO)
    glDeleteVertexArrays(1, VAO)

    glfw.terminate()

if __name__ == "__main__":
    main()
