import glm
import math
import pygame

class BaseCamera:
    def __init__(self, position, world_up, yaw, pitch):
        self.position = position
        self.world_up = world_up
        self.yaw = yaw
        self.pitch = pitch

        # Direction vectors
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.right = glm.vec3(0.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 0.0, 0.0)

        # Camera movement
        self.mouse_sensitivity = 0.1
        self.camera_speed = 5.0
            
    # Recalculate the camera's position to reflect the new distance
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)
    

class CameraManager:
    def __init__(self, cameras):
        # cameras is a list of camera objects
        self.cameras = cameras
        self.active_camera_index = 0
    
    def get_active_camera(self):
        # Returns the currently active camera object
        return self.cameras[self.active_camera_index]
        
    def switch_camera(self):
        # Switches to the next camera in the list
        self.active_camera_index = (self.active_camera_index + 1) % len(self.cameras)


class FirstPersonCamera(BaseCamera):
    def __init__(self, position, world_up, yaw, pitch):
        super().__init__(position, world_up, yaw, pitch)
        self.fov = 45.0
        self.update_camera_vectors()

    def process_mouse_movement(self, x_offset, y_offset):
        # Scale the mouse offset by sensitivity
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity
        
        # Update yaw and pitch angles
        self.yaw += x_offset
        self.pitch += y_offset
        
        # Clamp the pitch to prevent the camera from flipping over (gimbal lock))
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Recalculate the camera's direction vectors
        self.update_camera_vectors()

    def process_keyboard(self, direction, delta_time):
        velocity = self.camera_speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity
        if direction == "UP":
            self.position += self.world_up * velocity
        if direction == "DOWN":
            self.position -= self.world_up * velocity    
        
    def update_camera_vectors(self):
        # The math to calculate the front vector from yaw and pitch
        front = glm.vec3()
        front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        front.y = math.sin(glm.radians(self.pitch))
        front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

        # Calculate the right and up vectors
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up = glm.normalize(glm.cross(self.right, self.front))


class OrbitalCamera(BaseCamera):
    def __init__(self, position, world_up, yaw, pitch, target, distance_from_target):
        super().__init__(position, world_up, yaw, pitch)
        self.target = target
        self.distance_from_target = distance_from_target
        self.zoom = 45.0
        self.update_camera_vectors()

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        # Scale mouse movement by sensitivity
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity
        
        # Update yaw and pitch angles
        self.yaw += x_offset
        self.pitch -= y_offset
        
        # Clamp pitch to prevent gimbal lock
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        # Recalculate the camera's position and vectors
        self.update_camera_vectors()

    # For zoom functionality via mouse scroll
    def process_mouse_scroll(self, y_offset):
        # Adjust the distance from the target
        self.distance_from_target -= y_offset
        self.distance_from_target = max(1.0, self.distance_from_target)
        self.update_camera_vectors()

    # Updates the position in the orbit
    def update_camera_vectors(self):
        # Calculate position on a sphere using yaw, pitch, and distance
        x = self.distance_from_target * math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        y = self.distance_from_target * math.sin(glm.radians(self.pitch))
        z = self.distance_from_target * math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        
        # Update the absolute position by offsetting from the target
        self.position = self.target + glm.vec3(x, y, z)
        
        # Calculate the front vector by pointing from the camera's position to the target
        self.front = glm.normalize(self.target - self.position)
        
        # Calculate the right and up vectors from the new front vector
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def get_view_matrix(self):
        # Overridden to create a view matrix that looks from the camera's position to the target
        return glm.lookAt(self.position, self.target, self.up)

    

class ThirdPersonCamera(BaseCamera):
    def __init__(self, position, world_up, yaw, pitch, target, distance_from_target):
        super().__init__(position, world_up, yaw, pitch)
        self.target = target
        self.distance_from_target = distance_from_target
        # Set limits for zooming in and out
        self.min_distance = 1.0
        self.max_distance = 20.0
        # The camera's FOV (Field of View) for projection matrix
        self.fov = 45.0
        
        self.update_camera_vectors()

    def update_camera_vectors(self):
        # Calculate the camera's position on a sphere around the target
        theta = glm.radians(self.yaw)
        phi = glm.radians(self.pitch)
        
        offset_x = self.distance_from_target * math.cos(theta) * math.cos(phi)
        offset_y = self.distance_from_target * math.sin(phi)
        offset_z = self.distance_from_target * math.sin(theta) * math.cos(phi)

        # The camera's position is the target's position plus the offset
        self.position = self.target.position - glm.vec3(offset_x, offset_y, offset_z)

    def get_view_matrix(self):
        # The view matrix for a third-person camera looks at its target
        return glm.lookAt(self.position, self.target.position, self.world_up)

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity
        
        self.yaw -= x_offset  # Reverse yaw for a more intuitive rotation
        self.pitch += y_offset
        
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_camera_vectors()
        
    def process_mouse_scroll(self, y_offset):
        # Zoom in/out by changing the distance from the target
        self.distance_from_target -= y_offset * 0.5
        self.distance_from_target = max(self.min_distance, min(self.max_distance, self.distance_from_target))
        self.update_camera_vectors()