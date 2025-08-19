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