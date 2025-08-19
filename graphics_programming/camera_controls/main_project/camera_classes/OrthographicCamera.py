import glm
import pygame

class OrthographicCamera():
    def __init__(self, left, right, bottom, top, near, far):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.projection_matrix = glm.ortho(self.left, self.right, self.bottom, self.top, self.near, self.far)
        self.view_matrix = glm.mat4(1.0)
        self.view_projection_matrix = self.projection_matrix * self.view_matrix
        self.position.z = 20.0

    def update_view_matrix(self):
        self.view_matrix = glm.translate(glm.mat4(1.0), -self.position)

    def update_camera_vectors(self):
        self.update_view_matrix()
        self.view_projection_matrix = self.projection_matrix * self.view_matrix

    def get_view_matrix(self):
        return self.view_matrix
        
    def move(self, dx, dy, dz):
        self.position.x += dx
        self.position.y += dy
        self.position.z += dz
        self.update_camera_vectors()