#
# An optimized PyOpenGL script demonstrating frustum culling with a Bounding Volume Hierarchy (BVH).
# This program sets up a 3D scene, builds a BVH, and uses it to efficiently render only visible objects.
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
import time

# --- Bounding Volume Hierarchy (BVH) Classes ---
class BVHNode:
    """Represents a node in the BVH tree."""
    def __init__(self, bounding_box, children=None, objects=None):
        self.bounding_box = bounding_box  # [min_x, min_y, min_z, max_x, max_y, max_z]
        self.children = children or []
        self.objects = objects or []

def build_bvh(objects):
    """
    Recursively builds a simple BVH tree from a list of objects.
    A basic implementation splits objects along the longest axis.
    """
    if not objects:
        return None
    
    # Calculate the bounding box for all objects in the current list
    min_coords = np.min([obj['bounding_box'][:3] for obj in objects], axis=0)
    max_coords = np.max([obj['bounding_box'][3:] for obj in objects], axis=0)
    bounding_box = np.concatenate([min_coords, max_coords])

    # If the number of objects is small, this node becomes a leaf
    if len(objects) <= 10:
        return BVHNode(bounding_box, objects=objects)

    # Find the longest axis to split on
    extents = max_coords - min_coords
    split_axis = np.argmax(extents)
    
    # Sort objects along the split axis to divide them
    objects.sort(key=lambda obj: obj['position'][split_axis])
    
    mid_point = len(objects) // 2
    left_objects = objects[:mid_point]
    right_objects = objects[mid_point:]
    
    # Recursively build the child nodes
    left_child = build_bvh(left_objects)
    right_child = build_bvh(right_objects)

    return BVHNode(bounding_box, children=[left_child, right_child])

# --- Main Program Setup ---
def main():
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    window_width, window_height = 800, 600
    window = glfw.create_window(window_width, window_height, "PyOpenGL Frustum Culling with BVH (GLFW)", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create GLFW window")
        return

    glfw.make_context_current(window)

    init_gl(window_width, window_height)

    # Create a list of cubes to be culled
    cubes = create_cubes(100, 100, 10)  # Now 400 cubes for a better performance test
    bvh_root = build_bvh(cubes)  # Build the BVH from the cubes

    camera_pos = np.array([0.0, 50.0, 150.0])
    
    glViewport(0, 0, window_width, window_height)

    while not glfw.window_should_close(window):
        handle_input(window, camera_pos)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
                  0, 0, 0,
                  0, 1, 0)

        # --- Frustum Culling Logic (Optimized with BVH) ---
        projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX).T
        modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX).T
        mvp_matrix = np.dot(projection_matrix, modelview_matrix)
        planes = extract_frustum_planes(mvp_matrix)

        visible_objects = []
        cull_with_bvh(bvh_root, planes, visible_objects) # The new, optimized culling call
        
        # --- Rendering Loop (Optimized) ---
        culled_count = len(cubes) - len(visible_objects)
        total_count = len(cubes)
        
        for cube in visible_objects:
            draw_cube(cube['position'], cube['color'])
        
        draw_ground_plane()

        sys.stdout.write(f"\rObjects Culled: {culled_count}/{total_count} | Visible Objects: {len(visible_objects)}")
        sys.stdout.flush()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

# --- Culling Check (Updated for BVH) ---
def cull_with_bvh(node, planes, visible_objects):
    """
    Recursively culls objects using the BVH tree.
    If a node's bounding box is outside the frustum, its entire subtree is ignored.
    """
    if node is None:
        return
        
    # Check if the node's bounding box is inside the frustum
    if is_in_frustum_check(planes, node.bounding_box):
        
        # If this node is a leaf, add its objects to the visible list
        if node.objects:
            visible_objects.extend(node.objects)
        else:
            # If not a leaf, check the children
            for child in node.children:
                cull_with_bvh(child, planes, visible_objects)

def is_in_frustum_check(planes, bounding_box):
    """
    Checks if a bounding box is inside the frustum (Same logic as before).
    """
    for plane in planes:
        # Check all 8 vertices of the bounding box against the current plane
        is_outside = True
        
        if dot_product(plane, [bounding_box[0], bounding_box[1], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[1], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[4], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[4], bounding_box[2], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[1], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[1], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[0], bounding_box[4], bounding_box[5], 1.0]) > 0: is_outside = False
        if dot_product(plane, [bounding_box[3], bounding_box[4], bounding_box[5], 1.0]) > 0: is_outside = False
        
        if is_outside:
            return False
            
    return True
    
def dot_product(plane, vertex):
    """Calculates the dot product for a plane equation with a vertex."""
    return plane[0] * vertex[0] + plane[1] * vertex[1] + plane[2] * vertex[2] + plane[3] * vertex[3]
    
# --- The rest of the functions are unchanged from the previous version ---

def handle_input(window, camera_pos):
    """Handles keyboard input for camera movement."""
    speed = 5.0
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: camera_pos[0] -= speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: camera_pos[0] += speed
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: camera_pos[2] -= speed
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: camera_pos[2] += speed
    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS: camera_pos[1] -= speed
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS: camera_pos[1] += speed

def init_gl(width, height):
    """Sets up the OpenGL environment and projection matrix."""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

def extract_frustum_planes(mvp_matrix):
    """
    Extracts the six frustum planes from the combined model-view-projection matrix.
    """
    planes = []
    
    a,b,c,d = mvp_matrix[0][3]+mvp_matrix[0][0], mvp_matrix[1][3]+mvp_matrix[1][0], mvp_matrix[2][3]+mvp_matrix[2][0], mvp_matrix[3][3]+mvp_matrix[3][0]
    planes.append(normalize_plane_equation(a, b, c, d))
    a,b,c,d = mvp_matrix[0][3]-mvp_matrix[0][0], mvp_matrix[1][3]-mvp_matrix[1][0], mvp_matrix[2][3]-mvp_matrix[2][0], mvp_matrix[3][3]-mvp_matrix[3][0]
    planes.append(normalize_plane_equation(a, b, c, d))
    a,b,c,d = mvp_matrix[0][3]+mvp_matrix[0][1], mvp_matrix[1][3]+mvp_matrix[1][1], mvp_matrix[2][3]+mvp_matrix[2][1], mvp_matrix[3][3]+mvp_matrix[3][1]
    planes.append(normalize_plane_equation(a, b, c, d))
    a,b,c,d = mvp_matrix[0][3]-mvp_matrix[0][1], mvp_matrix[1][3]-mvp_matrix[1][1], mvp_matrix[2][3]-mvp_matrix[2][1], mvp_matrix[3][3]-mvp_matrix[3][1]
    planes.append(normalize_plane_equation(a, b, c, d))
    a,b,c,d = mvp_matrix[0][3]+mvp_matrix[0][2], mvp_matrix[1][3]+mvp_matrix[1][2], mvp_matrix[2][3]+mvp_matrix[2][2], mvp_matrix[3][3]+mvp_matrix[3][2]
    planes.append(normalize_plane_equation(a, b, c, d))
    a,b,c,d = mvp_matrix[0][3]-mvp_matrix[0][2], mvp_matrix[1][3]-mvp_matrix[1][2], mvp_matrix[2][3]-mvp_matrix[2][2], mvp_matrix[3][3]-mvp_matrix[3][2]
    planes.append(normalize_plane_equation(a, b, c, d))

    return planes

def normalize_plane_equation(a, b, c, d):
    """Normalizes the plane equation to simplify distance calculations."""
    magnitude = math.sqrt(a*a + b*b + c*c)
    return [a / magnitude, b / magnitude, c / magnitude, d / magnitude]
    
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
                'bounding_box': np.array([
                    pos_x - size, pos_y - size, pos_z - size,
                    pos_x + size, pos_y + size, pos_z + size
                ])
            })
    return cubes

def draw_cube(position, color):
    """Draws a single cube at the given position."""
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glColor3f(color[0], color[1], color[2])
    vertices = ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1))
    surfaces = ((0,1,2,3), (3,2,7,6), (6,7,5,4), (4,5,1,0), (1,5,7,2), (4,0,3,6))
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
