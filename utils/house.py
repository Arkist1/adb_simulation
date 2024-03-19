from entities import Wall, Pickup, Enemy
from .entityholder import EntityHolder

import random
import pygame


class House:
    def __init__(self, pos: pygame.Vector2, template, screen=None) -> None:
        self.template = template
        self.screen = screen
        self.pos = pos

        self.walls = []
        self.pickups = []
        self.enemies = []

        self.execute_template()

        self.top = pos + pygame.Vector2(0, -150)
        self.bottom = pos + pygame.Vector2(0, 150)
        self.left = pos + pygame.Vector2(-150, 0)
        self.right = pos + pygame.Vector2(150, 0)

    def execute_template(self):
        n_doors = 0
        total_door_walls = sum(
            [1 for wall in self.template["walls"] if wall["door_chance"] != 0]
        )

        for index, wall in enumerate(self.template["walls"]):
            if (
                random.random() < wall["door_chance"]
                and wall["door_chance"] != 0
                and n_doors < self.template["max_doors"]
                or n_doors == 0
                and total_door_walls - self.template["min_doors"] == index
                and wall["door_chance"] != 0
            ):
                n_doors += 1
                if wall["width"] > wall["door_width"]:
                    self.generate_wall(wall, y_door=True)
                else:
                    self.generate_wall(wall, x_door=True)

            else:
                self.generate_wall(wall)

        for index, pickup in enumerate(self.template["pickups"]):
            if random.random() < pickup["chance"]:
                pickup_type = int(
                    random.choices(
                        list(pickup["type"].keys()),
                        weights=list(pickup["type"].values()),
                    )[0]
                )

                print(pickup["pos"])
                self.generate_pickup(pickup["pos"], pickup_type)

        for index, enemy in enumerate(self.template["enemies"]):
            if random.random() < enemy["chance"]:
                self.generate_enemy(enemy["pos"])

    def generate_wall(self, wall, y_door=False, x_door=False):
        pos = pygame.Vector2(wall["pos"])
        width = wall["width"]
        height = wall["height"]

        door_width = wall["door_width"]

        if y_door:
            w = [
                Wall(
                    self.pos + pos - pygame.Vector2([door_width, 0]),
                    width=width - door_width * 2,
                    height=height,
                    screen=self.screen,
                ),
                Wall(
                    self.pos + pos - pygame.Vector2([-door_width, 0]),
                    width=width - door_width * 2,
                    height=height,
                    screen=self.screen,
                ),
            ]

        elif x_door:
            w = [
                Wall(
                    self.pos + pos - pygame.Vector2([0, door_width]),
                    width=width,
                    height=height - door_width * 2,
                    screen=self.screen,
                ),
                Wall(
                    self.pos + pos - pygame.Vector2([0, -door_width]),
                    width=width,
                    height=height - door_width * 2,
                    screen=self.screen,
                ),
            ]
        else:
            w = [Wall(self.pos + pos, width=width, height=height, screen=self.screen)]

        self.walls += w

    def generate_pickup(self, pos, pickup_type):
        rand = pygame.Vector2(random.randint(-150, 150), random.randint(-105, 105))
        self.pickups.append(Pickup(pickup_type, self.pos + pos + rand, screen=self.screen))

    def generate_enemy(self, pos):
        self.enemies.append(
            Enemy(
                start_pos=self.pos + pygame.Vector2(pos),
                control_type="enemy",
                screen=self.screen,
            )
        )
