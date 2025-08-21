import glm
import math
from .BaseCamera import BaseCamera

class FirstPersonCamera(BaseCamera):
    def __init__(self, position=glm.vec3(0.0, 0.0, 5.0), world_up=glm.vec3(0.0, 1.0, 0), yaw=-90.0, pitch=0.0):
        super().__init__(position, world_up, yaw, pitch)
        self.fov = 45.0
        self.update_camera_vectors()

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        # Scale the mouse offset by sensitivity
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity
        
        # Update yaw and pitch angles
        self.yaw += x_offset
        self.pitch -= y_offset
        
        # Clamp the pitch to prevent the camera from flipping over (gimbal lock)
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

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

    def handle_input():
        return