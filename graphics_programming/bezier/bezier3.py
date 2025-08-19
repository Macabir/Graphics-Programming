import glfw
from OpenGL.GL import *
import numpy as np
import ctypes

# --- 1. Control Points ---
# These are the four points that define the curve.
# The curve starts at P0 and ends at P3, and is "pulled" by P1 and P2.
control_points = np.array([
    [-0.2, -0.8, 0.0],  # P0 (Start point)
    [-0.4,  0.8, 0.0],  # P1 (Control point)
    [ 0.4, -0, 0.0],  # P2 (Control point)
    [ 0.2,  0.8, 0.0]   # P3 (End point)
], dtype=np.float32)

# --- 2. Shaders ---
# The Vertex Shader: This is where the calculus happens.
# It uses the cubic Bezier formula to calculate the position for each point on the curve.
# The `gl_VertexID` is an integer from 0 to N-1, and we convert it to a float `t` from 0 to 1.
vertex_shader_source = """
#version 330 core

// The 4 control points
uniform vec3 control_points[4];

// `gl_VertexID` gives us an integer from 0 to NUM_POINTS-1.
// This is converted to `t`, which iterates from 0.0 to 1.0 along the curve.
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

    window = glfw.create_window(800, 600, "Bezier Curve", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Compile the shaders
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # Link the shaders into a program
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # --- FIX ---
    # Create and bind a VAO. This is required for modern OpenGL
    # even when not using a VBO, as it maintains the state.
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # We still need a dummy VBO to keep the state valid, even if it's empty
    # Some older drivers might have issues without this
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    # We don't need to pass any data because it's generated in the shader
    
    # Get the uniform location for the control points array in the shader
    control_points_loc = glGetUniformLocation(shader_program, "control_points")

    glClearColor(0.2, 0.3, 0.3, 1.0)
    glUseProgram(shader_program)
    
    # Main render loop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        # Re-bind the VAO before drawing
        glBindVertexArray(VAO)
        
        # Set the uniform value for the control points
        # `control_points` is a 4x3 array, so we use a 4fv command.
        glUniform3fv(control_points_loc, 4, control_points)

        # Draw the curve by rendering 1000 points connected by a line strip.
        # This tells OpenGL to run our vertex shader 1000 times,
        # with gl_VertexID going from 0 to 999.
        glDrawArrays(GL_LINE_STRIP, 0, 1000)
        
        # Unbind the VAO
        glBindVertexArray(0)


        glfw.swap_buffers(window)
        glfw.poll_events()

    # --- FIX ---
    # Delete the VAO and VBO before terminating
    glDeleteBuffers(1, VBO)
    glDeleteVertexArrays(1, VAO)

    glfw.terminate()

if __name__ == "__main__":
    main()

