import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_triangle():
    """Draws a simple red, green, and blue triangle."""
    glBegin(GL_TRIANGLES)
    # Define the vertices and colors for a single triangle
    
    # Top vertex (Red)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)
    
    # Bottom-left vertex (Green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-1.0, -1.0, 0.0)
    
    # Bottom-right vertex (Blue)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(1.0, -1.0, 0.0)
    
    glEnd()

def setup_opengl(window):
    """Initializes the OpenGL settings."""
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST) # Enable depth testing to prevent rendering issues

    # Set up the camera perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5) # Move the camera back to see the triangle

def main():
    """Main function to run the application loop."""
    # Initialize the library
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "PyOpenGL Simple Primitive with GLFW", None, None)
    if not window:
        glfw.terminate()
        return

    setup_opengl(window)
    
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5) # Keep the camera at a fixed position
        
        draw_triangle()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
