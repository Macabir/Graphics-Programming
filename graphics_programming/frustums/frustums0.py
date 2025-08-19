#
# A basic PyOpenGL script demonstrating frustum culling, using GLFW for window management.
# This program sets up a 3D scene and only renders objects within the camera's view frustum.
#
# Required libraries:
#   pip install glfw PyOpenGL PyOpenGL_accelerate numpy
#
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import sys

# --- Main Program Setup ---
def main():
    # --- GLFW Initialization ---
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    # Create a windowed mode window and its OpenGL context
    window_width, window_height = 800, 600
    window = glfw.create_window(window_width, window_height, "PyOpenGL Frustum Culling (GLFW)", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create GLFW window")
        return

    glfw.make_context_current(window)

    # --- Camera and Scene Initialization ---
    init_gl(window_width, window_height)

    # Create a list of cubes to be culled
    cubes = create_cubes(100, 100, 10)  # 10x10 grid of cubes, 20 units apart

    # Initial camera position
    camera_pos = np.array([0.0, 50.0, 150.0])
    
    # Set the viewport to match the window size initially
    glViewport(0, 0, window_width, window_height)

    # Main loop
    while not glfw.window_should_close(window):
        
        # --- Input Handling ---
        handle_input(window, camera_pos)

        # Clear the screen and reset the view
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position the camera
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],  # Eye position
                  0, 0, 0,  # Look-at position
                  0, 1, 0)  # Up vector

        # --- Frustum Culling Logic ---
        
        # Get the combined projection-modelview matrix
        # This is the key to defining the frustum planes
        projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX).T
        modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX).T
        mvp_matrix = np.dot(projection_matrix, modelview_matrix)

        # Extract the six frustum planes from the combined matrix
        planes = extract_frustum_planes(mvp_matrix)

        # --- Rendering Loop with Culling ---
        culled_count = 0
        total_count = len(cubes)

        for cube in cubes:
            # Check if the cube's bounding box is inside the frustum
            # This is the core culling check
            if is_in_frustum(planes, cube['bounding_box']):
                draw_cube(cube['position'], cube['color'])
            else:
                culled_count += 1
                
        # Draw a simple ground plane
        draw_ground_plane()

        # Print culling statistics to the console
        sys.stdout.write(f"\rObjects Culled: {culled_count}/{total_count}")
        sys.stdout.flush()

        # Swap front and back buffers
        glfw.swap_buffers(window)
        
        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

# --- Input Handling ---
def handle_input(window, camera_pos):
    """Handles keyboard input for camera movement."""
    # Speed of camera movement
    speed = 5.0

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos[0] -= speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos[0] += speed
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos[2] -= speed
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos[2] += speed
    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        camera_pos[1] -= speed
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        camera_pos[1] += speed

# --- OpenGL Initialization ---
def init_gl(width, height):
    """Sets up the OpenGL environment and projection matrix."""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Perspective projection matrix. This defines our frustum's shape.
    gluPerspective(45, (width / height), 0.1, 200.0)
    
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

# --- Frustum Plane Extraction ---
def extract_frustum_planes(mvp_matrix):
    """
    Extracts the six frustum planes from the combined model-view-projection matrix.
    This is based on the "plane extraction" method, which is a standard technique.
    A plane is represented by a normal vector (a,b,c) and a distance from the origin (d).
    
    Plane equation: Ax + By + Cz + D = 0
    """
    planes = []
    
    # Left Plane
    a = mvp_matrix[0][3] + mvp_matrix[0][0]
    b = mvp_matrix[1][3] + mvp_matrix[1][0]
    c = mvp_matrix[2][3] + mvp_matrix[2][0]
    d = mvp_matrix[3][3] + mvp_matrix[3][0]
    planes.append(normalize_plane_equation(a, b, c, d))
    
    # Right Plane
    a = mvp_matrix[0][3] - mvp_matrix[0][0]
    b = mvp_matrix[1][3] - mvp_matrix[1][0]
    c = mvp_matrix[2][3] - mvp_matrix[2][0]
    d = mvp_matrix[3][3] - mvp_matrix[3][0]
    planes.append(normalize_plane_equation(a, b, c, d))
    
    # Bottom Plane
    a = mvp_matrix[0][3] + mvp_matrix[0][1]
    b = mvp_matrix[1][3] + mvp_matrix[1][1]
    c = mvp_matrix[2][3] + mvp_matrix[2][1]
    d = mvp_matrix[3][3] + mvp_matrix[3][1]
    planes.append(normalize_plane_equation(a, b, c, d))
    
    # Top Plane
    a = mvp_matrix[0][3] - mvp_matrix[0][1]
    b = mvp_matrix[1][3] - mvp_matrix[1][1]
    c = mvp_matrix[2][3] - mvp_matrix[2][1]
    d = mvp_matrix[3][3] - mvp_matrix[3][1]
    planes.append(normalize_plane_equation(a, b, c, d))
    
    # Near Plane
    a = mvp_matrix[0][3] + mvp_matrix[0][2]
    b = mvp_matrix[1][3] + mvp_matrix[1][2]
    c = mvp_matrix[2][3] + mvp_matrix[2][2]
    d = mvp_matrix[3][3] + mvp_matrix[3][2]
    planes.append(normalize_plane_equation(a, b, c, d))
    
    # Far Plane
    a = mvp_matrix[0][3] - mvp_matrix[0][2]
    b = mvp_matrix[1][3] - mvp_matrix[1][2]
    c = mvp_matrix[2][3] - mvp_matrix[2][2]
    d = mvp_matrix[3][3] - mvp_matrix[3][2]
    planes.append(normalize_plane_equation(a, b, c, d))

    return planes

def normalize_plane_equation(a, b, c, d):
    """Normalizes the plane equation to simplify distance calculations."""
    magnitude = math.sqrt(a*a + b*b + c*c)
    return [a / magnitude, b / magnitude, c / magnitude, d / magnitude]

# --- Culling Check ---
def is_in_frustum(planes, bounding_box):
    """
    Checks if a bounding box is inside the frustum.
    A bounding box is defined by its min and max coordinates (min_x, min_y, min_z, max_x, max_y, max_z).
    This is an "outside" check: if the bounding box is completely on the outside of any single plane,
    it is considered culled. Otherwise, it is rendered.
    """
    for plane in planes:
        # Check all 8 vertices of the bounding box against the current plane
        is_outside = True
        
        # Check if any vertex is on the "inside" side of the plane
        # If any vertex is inside, the bounding box is not completely outside this plane
        if dot_product(plane, [bounding_box[0], bounding_box[1], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[1], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[4], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[4], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[1], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[1], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[4], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[4], bounding_box[5], 1.0]) > 0: is_outside = False
        
        if is_outside:
            # The entire bounding box is outside this plane, so we can immediately cull it.
            return False
            
    # If the bounding box is not completely outside any of the six planes, it's considered in the frustum.
    return True

def dot_product(plane, vertex):
    """Calculates the dot product for a plane equation with a vertex."""
    return plane[0] * vertex[0] + plane[1] * vertex[1] + plane[2] * vertex[2] + plane[3] * vertex[3]

# --- Scene and Object Generation ---
def create_cubes(rows, cols, spacing):
    """Generates a grid of cubes with random colors."""
    cubes = []
    size = 5
    for x in range(rows):
        for z in range(cols):
            pos_x = (x - rows / 2) * spacing
            pos_z = (z - cols / 2) * spacing
            pos_y = 0

            color = [math.sin(x) * 0.5 + 0.5, 
                     math.cos(z) * 0.5 + 0.5, 
                     (x + z) / (rows + cols) * 0.5 + 0.5]
            
            cubes.append({
                'position': [pos_x, pos_y, pos_z],
                'color': color,
                'bounding_box': [
                    pos_x - size, pos_y - size, pos_z - size, # min_x, min_y, min_z
                    pos_x + size, pos_y + size, pos_z + size  # max_x, max_y, max_z
                ]
            })
    return cubes

# --- Drawing Utilities ---
def draw_cube(position, color):
    """Draws a single cube at the given position."""
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glColor3f(color[0], color[1], color[2])
    
    # Cube vertex data
    vertices = (
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
    )
    edges = (
        (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
        (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
    )
    surfaces = (
        (0,1,2,3), (3,2,7,6), (6,7,5,4),
        (4,5,1,0), (1,5,7,2), (4,0,3,6)
    )

    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

    glPopMatrix()
    
def draw_ground_plane():
    """Draws a simple ground plane."""
    glPushMatrix()
    glTranslatef(0, -5, 0)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(100.0, 0.0, -100.0)
    glVertex3f(-100.0, 0.0, -100.0)
    glVertex3f(-100.0, 0.0, 100.0)
    glVertex3f(100.0, 0.0, 100.0)
    glEnd()
    glPopMatrix()

if __name__ == '__main__':
    main()
