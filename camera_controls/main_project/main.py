import pygame
from OpenGL.GL import *
import numpy as np
import glm
import os
from cube_data import cube_vertices
from event_handler import handle_input
from camera_classes.OrbitalCamera import OrbitalCamera
from camera_classes.FirstPersonCamera import FirstPersonCamera
from camera_classes.CameraManager import CameraManager
from camera_classes.ThirdPersonCamera import ThirdPersonCamera
from camera_classes.OrthographicCamera import OrthographicCamera

class Target:
    def __init__(self, position):
        self.position = position

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory
os.chdir(script_dir)

# Window setup
pygame.init()
pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)

# Mouse movement
def get_relative_mouse_movement():
    return pygame.mouse.get_rel()

# Mouse_grab setup
mouse_grabbed = True
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# OpenGL setup
glEnable(GL_DEPTH_TEST)

# Shaders
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    return shader

def create_shader_program(vertex_shader_source, fragment_shader_source):
    # This is the correct way to call the function and store the result
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    return program

with open("vertex_shader.glsl") as f:
    vertex_shader_source = f.read()

with open("fragment_shader.glsl") as f:
    fragment_shader_source = f.read()

shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)

# Cube data (vertices and colors)
vertices = np.array(cube_vertices, dtype=np.float32)

# A cube intended to move, demonstrating differences
# In the third-person and orbital cameras
cube_target = Target(position=glm.vec3(0.0, 0.0, 0.0))

# A cube intended to be still, for point of reference
static_cube_target = Target(position=glm.vec3(-5.0, 0.0, 0.0))

reference_cube_target = Target(position=glm.vec3(-5.0,3.0,0.0))

# VAO and VBO
VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# Position attribute
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)
# Color attribute
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
glEnableVertexAttribArray(1)

# Create the camera objects and manager
first_person_cam = FirstPersonCamera(
    position=glm.vec3(0.0, 0.0, 5.0),
    world_up=glm.vec3(0.0, 1.0, 0),
    yaw=-90.0,
    pitch=0.0
)

orbital_cam = OrbitalCamera(
    position=glm.vec3(0.0, 0.0, 5.0),
    world_up=glm.vec3(0.0, 1.0, 0.0),
    yaw=-90.0,
    pitch=0.0,
    target=glm.vec3(0.0, 0.0, 0.0),
    distance_from_target=5.0
)

third_person_cam = ThirdPersonCamera(
    position=glm.vec3(0.0, 0.0, 5.0),
    world_up=glm.vec3(0.0, 1.0, 0),
    yaw=-90.0, pitch=0.0,
    target=cube_target,
    distance_from_target=5.0
)

orthographic_cam = OrthographicCamera(
    left = 0,
    right = 800,
    bottom = 0,
    top = 600,
    near = -1,
    far = 1
)

camera_manager = CameraManager(
    cameras = [first_person_cam, orbital_cam, third_person_cam, orthographic_cam]
)

active_camera = 0

# Main loop variables
last_frame = 0.0
mouse_x, mouse_y = 400, 300
first_mouse = True

# A vector to store the cube's movement direction
move_direction = glm.vec3(1.0, 0.0, 0.0)
# The maximum x-position the cube should reach before turning around
max_x_position = 3.0
# The speed of the cube
cube_speed = 1.0

# Main loop
running = True
while running:

    running, active_camera = handle_input(camera_manager, active_camera)

    # Time for movement speed
    current_frame = pygame.time.get_ticks() / 1000.0
    delta_time = current_frame - last_frame
    last_frame = current_frame

    # Check if the cube has reached its boundary
    if cube_target.position.x > max_x_position:
        move_direction = -move_direction
    elif cube_target.position.x < -max_x_position:
        move_direction = -move_direction

    # Update the cube's position using the direction and speed
    cube_target.position += move_direction * cube_speed * delta_time

    active_camera = camera_manager.get_active_camera()
    
    # Update the active camera's vectors (its position)
    
    keys = pygame.key.get_pressed()

    if isinstance(active_camera, FirstPersonCamera):
        if keys[pygame.K_w]:
            active_camera.process_keyboard("FORWARD", delta_time)
        if keys[pygame.K_s]:
            active_camera.process_keyboard("BACKWARD", delta_time)
        if keys[pygame.K_a]:
            active_camera.process_keyboard("LEFT", delta_time)
        if keys[pygame.K_d]:
            active_camera.process_keyboard("RIGHT", delta_time)
        if keys[pygame.K_SPACE]:
            active_camera.process_keyboard("UP", delta_time)
        if keys[pygame.K_LSHIFT]:
            active_camera.process_keyboard("DOWN", delta_time)

    active_camera.update_camera_vectors()

    # Frame-by-frame camera controls
    if mouse_grabbed:
        # Takes mouse input
        x_offset, y_offset = get_relative_mouse_movement()
        
        # Updates Camera movement
        if not active_camera == orthographic_cam:
            active_camera.process_mouse_movement(x_offset, -y_offset)

    # Get the active camera
    active_camera = camera_manager.get_active_camera()

    # Use conditional logic to handle different camera attributes
    fov = 45.0 # Default FOV
    aspect_ratio = 800 / 600

    if  not isinstance(active_camera, FirstPersonCamera):
        # Fixes the field of vision
        fov = 45.0
    else:
        # First-person camera uses FOV for "zoom"
        # Assuming you have a 'fov' attribute in your FirstPersonCamera class
        fov = active_camera.fov

 

    # Rendering
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(shader_program)

    view = active_camera.get_view_matrix()
    projection = glm.perspective(glm.radians(fov), aspect_ratio, 0.1, 100.0)

    view_loc = glGetUniformLocation(shader_program, "view")
    projection_loc = glGetUniformLocation(shader_program, "projection"
                                          )
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection))


    model_loc = glGetUniformLocation(shader_program, "model")

    model = glm.mat4(1.0)
    model = glm.translate(model, cube_target.position)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36) 

    # Static Cube Matrix
    static_model = glm.mat4(1.0)
    static_model = glm.translate(static_model, static_cube_target.position)

    static_model_loc = glGetUniformLocation(shader_program, "static_model")

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(static_model))

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)

    # Reference Cube Matrix
    reference_model = glm.mat4(1.0)
    reference_model = glm.translate(reference_model, reference_cube_target.position)

    reference_model_loc = glGetUniformLocation(shader_program, "reference_model")

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(reference_model))

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)

    pygame.display.flip()

pygame.quit()
