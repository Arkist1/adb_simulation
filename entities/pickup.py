from utils import Object

import pygame


class Pickup(Object):
    def __init__(
        self,
        pickup_type,
        start_pos=[400, 400],
        screen=None,
    ) -> None:
        self.size = [15, 25, 15, 25][pickup_type]
        super().__init__(
            pos=pygame.Vector2(start_pos[0], start_pos[1]), radius=self.size
        )
        self.screen = screen
        # 0 = health->small, 1 = health->large, 2 = food->small, 3 = food->large
        self.pickup_type = pickup_type
        self.color = [(200, 0, 0), (150, 0, 0), (0, 200, 0), (0, 150, 0)][pickup_type]

    def picked_up(self):
        if self.pickup_type == 0 or self.pickup_type == 2:
            return 25
        elif self.pickup_type == 1 or self.pickup_type == 3:
            return 50

    def draw(self, cam):
        pygame.draw.circle(
            self.screen,
            self.color,
            self.pos * cam.zoom - cam.position,
            self.size * cam.zoom,
        )

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "pickup_type": self.pickup_type,
        }
