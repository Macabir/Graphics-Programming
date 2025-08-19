import pygame
from camera import OrbitalCamera, ThirdPersonCamera


# Event handling
def handle_input(camera_manager, active_camera):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            get_grab = pygame.event.set_grab(False)
            return False, active_camera
        if event.type == pygame.KEYDOWN:
            # Toggle camera mode
            if event.key == pygame.K_c:
                camera_manager.switch_camera()
                active_camera = camera_manager.get_active_camera()
            # Toggle Mouse Grab and Visibility
            if event.key == pygame.K_ESCAPE:
                # Toggle mouse grab and visibility
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
        elif event.type == pygame.MOUSEBUTTONDOWN:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)

        if event.type == pygame.MOUSEWHEEL:
            y_offset = event.y
            if isinstance(active_camera, (OrbitalCamera, ThirdPersonCamera)):
                active_camera.process_mouse_scroll(y_offset)

    return True, camera_manager.get_active_camera()