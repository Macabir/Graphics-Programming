import glm
import math
from .BaseCamera import BaseCamera

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

