import glm

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

    

    
