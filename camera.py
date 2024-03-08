from utils import Globals

import pygame


class Camera:
    def __init__(self, position: pygame.Vector2, size: pygame.Vector2) -> None:
        self.position = position
        self.size = size
        self.zoom = sum(Globals().SCREEN_SIZE) / sum(size)

    def move_cam(self, new_pos: pygame.Vector2):
        self.position = new_pos

    def move_cam_delta(self, delta_pos: pygame.Vector2):
        self.position += delta_pos

    def apply_zoom(self, amt):
        newzoom = self.zoom * amt
        self.size = self.size / self.zoom * newzoom
        self.zoom = newzoom

    def get_view(self):
        return [self.position, self.position + self.size]


class Camera_controller:
    def __init__(self, cams: dict[str, Camera], window) -> None:
        self.cameras = cams
        self.curr_cam_name = list(cams.keys())[0]
        self.curr_cam = cams[self.curr_cam_name]
        self.window = window

    def change_cam(self, cam: str):
        print("switching to", cam)
        self.curr_cam_name = cam
        self.curr_cam = self.cameras[cam]

    def get_current_cam_view(self):
        return self.curr_cam.get_view()

    def get_current_cam_pos(self):
        return self.curr_cam.position

    def apply_cam(self):
        self.window.position = self.curr_cam.position

    def add_cam(self, name: str, cam: Camera):
        self.cameras[name] = cam
