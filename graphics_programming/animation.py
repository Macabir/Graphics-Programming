import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time

# --- Global Variables for Animation and Camera ---
# We use a global variable to store the rotation angle, which we'll increment
# in our main loop.
rotation_angle_y = 0.0
rotation_angle_z = 0.0

# Mouse and Camera settings for interaction
mouse_pos = (0, 0)
mouse_down = False
camera_position = np.array([0, 0, 5], dtype=np.float32)
camera_rotation = np.array([0, 0, 0], dtype=np.float32)

# --- GLFW Callbacks for User Interaction ---
def cursor_position_callback(window, xpos, ypos):
    """Handles mouse movement for camera control."""
    global mouse_pos, mouse_down, camera_rotation
    if mouse_down:
        dx = xpos - mouse_pos[0]
        dy = ypos - mouse_pos[1]
        camera_rotation[1] += dx * 0.1
        camera_rotation[0] += dy * 0.1
    mouse_pos = (xpos, ypos)

def mouse_button_callback(window, button, action, mods):
    """Handles mouse button presses for camera control."""
    global mouse_down
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_down = True
        elif action == glfw.RELEASE:
            mouse_down = False

# --- Drawing and Rendering Function ---
def draw_cube():
    """Draws a complete cube with different colors on each face."""
    glPushMatrix()
    glBegin(GL_QUADS)

    # Define vertices for a unit cube
    vertices = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], # Back face
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],   # Front face
        [-1, -1, -1], [-1, 1, -1], [-1, 1, 1], [-1, -1, 1],   # Left face
        [1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1],   # Right face
        [-1, -1, -1], [-1, -1, 1], [1, -1, 1], [1, -1, -1],   # Bottom face
        [-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1]    # Top face
    ], dtype=np.float32)

    # Define colors for each face
    colors = [
        [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, 1.0]
    ]

    # Draw the faces
    for i in range(6):
        glColor3fv(colors[i])
        for j in range(4):
            glVertex3fv(vertices[i*4 + j])

    glEnd()
    glPopMatrix()


# --- Main Application Loop ---
def main():
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "PyOpenGL Simple Animation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # Enable depth test for correct rendering of 3D objects
    glEnable(GL_DEPTH_TEST)

    # Set up the projection matrix once
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800/600, 0.1, 100.0)

    # --- Time variables for animation ---
    # We need to track time to ensure our animation is speed-independent.
    last_time = time.time()

    # The main rendering loop
    while not glfw.window_should_close(window):
        # --- 1. Calculate Delta Time ---
        # Delta time is the time elapsed since the last frame.
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        # --- 2. Update Object State ---
        # Increment the rotation angle based on delta time.
        # Multiplying by delta_time ensures a constant rotation speed regardless of FPS.
        global rotation_angle_y
        global rotation_angle_z
        rotation_speed = 10.0 # degrees per second
        rotation_angle_y += rotation_speed * delta_time
        rotation_angle_z += rotation_speed * delta_time * 2

        # --- 3. Clear Buffers and Set up View ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply camera transformations
        glRotatef(camera_rotation[0], 1, 0, 0)
        glRotatef(camera_rotation[1], 0, 1, 0)
        glTranslatef(-camera_position[0], -camera_position[1], -camera_position[2])

        # --- 4. Apply Object's Transformation and Draw ---
        # Apply the rotation we calculated above to the cube.
        glRotatef(rotation_angle_y, 0, 1, 0)
        glRotatef(rotation_angle_z, 1, 0, 0)
        draw_cube()

        # Swap front and back buffers
        glfw.swap_buffers(window)
        
        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
