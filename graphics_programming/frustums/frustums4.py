import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
from typing import List

# --- Axis-Aligned Bounding Box (AABB) Class ---
class AABB:
    """A simple Axis-Aligned Bounding Box."""
    def __init__(self, min_point: List[float], max_point: List[float]):
        self.min = np.array(min_point, dtype=np.float32)
        self.max = np.array(max_point, dtype=np.float32)
    
    @staticmethod
    def from_aabbs(aabbs: List['AABB']) -> 'AABB':
        """Creates a new AABB that encloses a list of other AABBs."""
        if not aabbs:
            return AABB([0, 0, 0], [0, 0, 0])
        
        min_p = np.copy(aabbs[0].min)
        max_p = np.copy(aabbs[0].max)
        
        for aabb in aabbs[1:]:
            min_p = np.minimum(min_p, aabb.min)
            max_p = np.maximum(max_p, aabb.max)
            
        return AABB(min_p, max_p)

# --- Frustum Culling Implementation ---
class Frustum:
    """Represents the 6 planes of the camera's view frustum."""
    def __init__(self):
        self.planes = [np.zeros(4, dtype=np.float32) for _ in range(6)]

    def extract_planes(self, mvp_matrix: np.ndarray):
        """
        Extracts the 6 frustum planes from the model-view-projection matrix.
        These planes define the viewing volume in world space.
        """
        # Right plane
        self.planes[0][0] = mvp_matrix[3][0] - mvp_matrix[0][0]
        self.planes[0][1] = mvp_matrix[3][1] - mvp_matrix[0][1]
        self.planes[0][2] = mvp_matrix[3][2] - mvp_matrix[0][2]
        self.planes[0][3] = mvp_matrix[3][3] - mvp_matrix[0][3]
        self.normalize_plane(self.planes[0])

        # Left plane
        self.planes[1][0] = mvp_matrix[3][0] + mvp_matrix[0][0]
        self.planes[1][1] = mvp_matrix[3][1] + mvp_matrix[0][1]
        self.planes[1][2] = mvp_matrix[3][2] + mvp_matrix[0][2]
        self.planes[1][3] = mvp_matrix[3][3] + mvp_matrix[0][3]
        self.normalize_plane(self.planes[1])

        # Bottom plane
        self.planes[2][0] = mvp_matrix[3][0] + mvp_matrix[1][0]
        self.planes[2][1] = mvp_matrix[3][1] + mvp_matrix[1][1]
        self.planes[2][2] = mvp_matrix[3][2] + mvp_matrix[1][2]
        self.planes[2][3] = mvp_matrix[3][3] + mvp_matrix[1][3]
        self.normalize_plane(self.planes[2])

        # Top plane
        self.planes[3][0] = mvp_matrix[3][0] - mvp_matrix[1][0]
        self.planes[3][1] = mvp_matrix[3][1] - mvp_matrix[1][1]
        self.planes[3][2] = mvp_matrix[3][2] - mvp_matrix[1][2]
        self.planes[3][3] = mvp_matrix[3][3] - mvp_matrix[1][3]
        self.normalize_plane(self.planes[3])

        # Near plane
        self.planes[4][0] = mvp_matrix[3][0] + mvp_matrix[2][0]
        self.planes[4][1] = mvp_matrix[3][1] + mvp_matrix[2][1]
        self.planes[4][2] = mvp_matrix[3][2] + mvp_matrix[2][2]
        self.planes[4][3] = mvp_matrix[3][3] + mvp_matrix[2][3]
        self.normalize_plane(self.planes[4])

        # Far plane
        self.planes[5][0] = mvp_matrix[3][0] - mvp_matrix[2][0]
        self.planes[5][1] = mvp_matrix[3][1] - mvp_matrix[2][1]
        self.planes[5][2] = mvp_matrix[3][2] - mvp_matrix[2][2]
        self.planes[5][3] = mvp_matrix[3][3] - mvp_matrix[2][3]
        self.normalize_plane(self.planes[5])

    def normalize_plane(self, plane: np.ndarray):
        """Normalizes a plane equation."""
        length = np.sqrt(plane[0]**2 + plane[1]**2 + plane[2]**2)
        plane /= length

    def is_aabb_in_frustum(self, aabb: AABB) -> bool:
        """
        Checks if an AABB is inside the frustum using the separating axis theorem.
        Returns true if the AABB is inside or intersects the frustum.
        """
        for plane in self.planes:
            p_vertex = np.array([
                aabb.max[0] if plane[0] >= 0 else aabb.min[0],
                aabb.max[1] if plane[1] >= 0 else aabb.min[1],
                aabb.max[2] if plane[2] >= 0 else aabb.min[2]
            ], dtype=np.float32)
            
            dist_p = np.dot(plane[:3], p_vertex) + plane[3]

            if dist_p < 0:
                return False
        return True

# --- Camera Class ---
class Camera:
    """Manages the camera's position, rotation, and matrices."""
    def __init__(self, position=[0, 0, 5], rotation=[0, 0, 0]):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.fov = 45
        self.near = 0.1
        self.far = 100.0

    def get_view_matrix(self) -> np.ndarray:
        """
        Computes the view matrix from the camera's position and rotation.
        The view matrix is the inverse of the camera's world transform.
        """
        rot_x_rad = np.radians(self.rotation[0])
        rot_y_rad = np.radians(self.rotation[1])
        
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, np.cos(rot_x_rad), -np.sin(rot_x_rad), 0],
            [0, np.sin(rot_x_rad), np.cos(rot_x_rad), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        rot_y = np.array([
            [np.cos(rot_y_rad), 0, np.sin(rot_y_rad), 0],
            [0, 1, 0, 0],
            [-np.sin(rot_y_rad), 0, np.cos(rot_y_rad), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        rotation_matrix = rot_y @ rot_x
        
        # Translate matrix is the inverse of the camera's position
        translate_matrix = np.identity(4, dtype=np.float32)
        translate_matrix[0, 3] = -self.position[0]
        translate_matrix[1, 3] = -self.position[1]
        translate_matrix[2, 3] = -self.position[2]
        
        # The view matrix is inverse(T*R) = inverse(R) * inverse(T)
        # For rotation matrices, inverse is the transpose
        return rotation_matrix.T @ translate_matrix

# --- Cube Class (Primitive) ---
class Cube:
    def __init__(self, position: List[float], size: float = 1.0):
        self.position = np.array(position, dtype=np.float32)
        self.size = size
        min_p = self.position - size
        max_p = self.position + size
        self.aabb = AABB(min_p, max_p)

    def draw(self):
        """Draws a complete cube at its position."""
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glBegin(GL_QUADS)
        # Front face (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(1.0, 1.0, 1.0); glVertex3f(-1.0, 1.0, 1.0); glVertex3f(-1.0, -1.0, 1.0); glVertex3f(1.0, -1.0, 1.0)
        # Back face (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, -1.0); glVertex3f(-1.0, -1.0, -1.0); glVertex3f(-1.0, 1.0, -1.0); glVertex3f(1.0, 1.0, -1.0)
        # Top face (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0); glVertex3f(-1.0, 1.0, -1.0); glVertex3f(-1.0, 1.0, 1.0); glVertex3f(1.0, 1.0, 1.0)
        # Bottom face (yellow)
        glColor3f(1.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0); glVertex3f(-1.0, -1.0, 1.0); glVertex3f(-1.0, -1.0, -1.0); glVertex3f(1.0, -1.0, -1.0)
        # Right face (cyan)
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0); glVertex3f(1.0, 1.0, 1.0); glVertex3f(1.0, -1.0, 1.0); glVertex3f(1.0, -1.0, -1.0)
        # Left face (magenta)
        glColor3f(1.0, 0.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0); glVertex3f(-1.0, 1.0, -1.0); glVertex3f(-1.0, -1.0, -1.0); glVertex3f(-1.0, -1.0, 1.0)
        glEnd()
        glPopMatrix()

# --- BVH Node Class ---
class BVHNode:
    """A node in the Bounding Volume Hierarchy."""
    def __init__(self, aabb: AABB, children: List[any]):
        self.aabb = aabb
        self.children = children

# --- Functions to build and render the BVH ---
def build_bvh(objects: List[any], leaf_size: int = 4) -> BVHNode:
    """
    Recursively builds a BVH tree from a list of objects.
    Each object must have an `aabb` attribute.
    """
    if len(objects) <= leaf_size:
        # This is a leaf node, return a node containing the objects
        aabbs = [obj.aabb for obj in objects]
        return BVHNode(AABB.from_aabbs(aabbs), objects)

    # Find the axis with the largest extent
    aabbs = [obj.aabb for obj in objects]
    root_aabb = AABB.from_aabbs(aabbs)
    extent = root_aabb.max - root_aabb.min
    split_axis = np.argmax(extent)
    
    # Sort objects along the split axis
    objects.sort(key=lambda obj: obj.aabb.min[split_axis])
    
    # Split into two halves
    mid_index = len(objects) // 2
    left_children = build_bvh(objects[:mid_index], leaf_size)
    right_children = build_bvh(objects[mid_index:], leaf_size)

    return BVHNode(root_aabb, [left_children, right_children])

def draw_aabb(aabb: AABB):
    """Draws a wireframe representation of an AABB."""
    min_x, min_y, min_z = aabb.min
    max_x, max_y, max_z = aabb.max

    glBegin(GL_LINES)
    # Bottom face
    glVertex3f(min_x, min_y, min_z); glVertex3f(max_x, min_y, min_z)
    glVertex3f(max_x, min_y, min_z); glVertex3f(max_x, min_y, max_z)
    glVertex3f(max_x, min_y, max_z); glVertex3f(min_x, min_y, max_z)
    glVertex3f(min_x, min_y, max_z); glVertex3f(min_x, min_y, min_z)

    # Top face
    glVertex3f(min_x, max_y, min_z); glVertex3f(max_x, max_y, min_z)
    glVertex3f(max_x, max_y, min_z); glVertex3f(max_x, max_y, max_z)
    glVertex3f(max_x, max_y, max_z); glVertex3f(min_x, max_y, max_z)
    glVertex3f(min_x, max_y, max_z); glVertex3f(min_x, max_y, min_z)

    # Connecting lines
    glVertex3f(min_x, min_y, min_z); glVertex3f(min_x, max_y, min_z)
    glVertex3f(max_x, min_y, min_z); glVertex3f(max_x, max_y, min_z)
    glVertex3f(max_x, min_y, max_z); glVertex3f(max_x, max_y, max_z)
    glVertex3f(min_x, min_y, max_z); glVertex3f(min_x, max_y, max_z)
    glEnd()

def draw_bvh(node: BVHNode, frustum: Frustum, visible_count_ptr):
    """
    Traverses the BVH and draws only the visible objects using frustum culling.
    """
    global draw_bvh_aabbs
    
    if not frustum.is_aabb_in_frustum(node.aabb):
        # The entire node is outside the frustum, so we can stop
        return
    
    if draw_bvh_aabbs:
        glColor3f(0.5, 0.5, 0.5) # Grey color for the bounding boxes
        draw_aabb(node.aabb)
        
    for child in node.children:
        if isinstance(child, BVHNode):
            # It's an internal node, recursively draw its children
            draw_bvh(child, frustum, visible_count_ptr)
        else:
            # It's a leaf node (a Cube), draw the object
            child.draw()
            visible_count_ptr[0] += 1

# --- GLFW Callbacks and Main Window Logic ---
mouse_pos = (0, 0)
mouse_down = False
camera = Camera(position=[0, 20, 40], rotation=[-25, 0, 0])
draw_bvh_aabbs = False # New global variable to toggle BVH AABB visualization

def cursor_position_callback(window, xpos, ypos):
    global mouse_pos, mouse_down, camera
    if mouse_down:
        dx = xpos - mouse_pos[0]
        dy = ypos - mouse_pos[1]
        camera.rotation[1] += dx * 0.1
        camera.rotation[0] += dy * 0.1
    mouse_pos = (xpos, ypos)

def mouse_button_callback(window, button, action, mods):
    global mouse_down
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_down = True
        elif action == glfw.RELEASE:
            mouse_down = False

def key_callback(window, key, scancode, action, mods):
    global draw_bvh_aabbs
    if action == glfw.PRESS:
        if key == glfw.KEY_V:
            draw_bvh_aabbs = not draw_bvh_aabbs

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(800, 600, "Simple Frustum Culling with BVH", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # --- Change this variable to control the number of cubes ---
    num_cubes_per_side = 40
    
    # Generate a grid of cubes
    cubes = []
    spacing = 5.0
    start_x = -(num_cubes_per_side * spacing) / 2
    start_z = -(num_cubes_per_side * spacing) / 2

    for i in range(num_cubes_per_side):
        for j in range(num_cubes_per_side):
            x = start_x + i * spacing
            y = 0.0  # Cubes on a flat plane
            z = start_z + j * spacing
            cubes.append(Cube(position=[x, y, z], size=2.0))
    
    # Build the BVH from the list of cubes
    bvh_root = build_bvh(cubes)
    
    frustum = Frustum()

    while not glfw.window_should_close(window):
        # Handle camera movement with keyboard
        yaw = np.radians(camera.rotation[1])
        pitch = np.radians(camera.rotation[0])
        forward_vector = np.array([np.sin(yaw), -np.sin(pitch), np.cos(yaw)])
        right_vector = np.array([np.sin(yaw - np.pi/2), 0, np.cos(yaw - np.pi/2)])

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camera.position += forward_vector * 0.5
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camera.position -= forward_vector * 0.5
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camera.position += right_vector * 0.5
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            camera.position -= right_vector * 0.5

        # Update the viewport and aspect ratio if the window is resized
        width, height = glfw.get_framebuffer_size(window)
        glViewport(0, 0, width, height)
        aspect = width / height if height > 0 else 1.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Get matrices and combine them for frustum plane extraction
        view_matrix = camera.get_view_matrix()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(camera.fov, aspect, camera.near, camera.far)
        projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        
        # We need the model-view-projection matrix for frustum culling
        # np.matmul expects row-major matrices, so we transpose.
        mvp_matrix = np.matmul(projection_matrix.T, view_matrix).T

        # Extract frustum planes from the combined matrix
        frustum.extract_planes(mvp_matrix)

        # Draw only the objects that are inside the frustum by traversing the BVH
        visible_count = [0] # Use a list to pass by reference for the recursive function
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(view_matrix.T) # Load the view matrix once
        draw_bvh(bvh_root, frustum, visible_count)
        
        # Update window title to show visible objects count
        glfw.set_window_title(window, f"Visible Objects: {visible_count[0]}")
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == '__main__':
    main()
