import glm
import math
from .BaseCamera import BaseCamera

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
    
    def handle_input():
        return
    