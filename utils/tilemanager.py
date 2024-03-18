from typing import Any
import pygame
from . import Tile
from . import House
from . import Globals
from . import EntityHolder

import random


class TileManager(EntityHolder):
    def __init__(self, tilesize: pygame.Vector2, mapsize: pygame.Vector2) -> None:
        super().__init__()

        self.tile_width = tilesize.x
        self.tile_height = tilesize.y

        self.tiles = []

        for xtile in range(0, int(mapsize.x / tilesize.x)):
            self.tiles.append([])
            for ytile in range(0, int(mapsize.y / tilesize.y)):
                self.tiles[xtile].append(
                    Tile(
                        pygame.Vector2(xtile * tilesize.x, ytile * tilesize.y),
                        tilesize.x,
                        tilesize.y,
                    )
                )

    def __call__(self, pos: pygame.Vector2) -> Tile:
        for xindex in range(0, len(self.tiles)):
            if (
                self.tiles[xindex][0].pos.x
                < pos.x
                < self.tiles[xindex][0].pos.x + self.tile_width
            ):
                for yindex in range(0, len(self.tiles[0])):
                    if (
                        self.tiles[xindex][yindex].pos.y
                        < pos.y
                        < self.tiles[xindex][yindex].pos.y + self.tile_height
                    ):
                        return self.tiles[xindex][yindex]

                break

    @property
    def allwalls(self):
        res = []
        for yindex in range(0, len(self.tiles[0]) - 1):
            for xindex in range(0, len(self.tiles) - 1):
                for wall in self.tiles[xindex][yindex].walls:
                    res.append(wall)

        return res

    @property
    def allpickups(self):
        res = []
        for yindex in range(0, len(self.tiles[0]) - 1):
            for xindex in range(0, len(self.tiles) - 1):
                for pickup in self.tiles[xindex][yindex].pickups:
                    res.append(pickup)

        return res

    def generate_terrain(self, templates, screen):
        for yindex in range(0, len(self.tiles[0]) - 1):
            for xindex in range(0, len(self.tiles) - 1):
                if random.random() < templates["house_chance"]:
                    h = House(
                        self.tiles[xindex][yindex].pos + pygame.Vector2(500, 500),
                        template=templates["simple_house"],
                        screen=screen,
                    )

                    self.tiles[xindex][yindex].walls = h.walls
                    self.tiles[xindex][yindex].pickups = h.pickups
                    self.enemies += h.enemies

    def get_tiled_items(self, pos: pygame.Vector2):
        tile = self(pos)
        return (
            self.players
            + self.boxes
            + self.bullets
            + self.enemies
            + tile.walls
            + tile.pickups
        )

    def get_items(self):
        return (
            self.players + self.boxes + self.bullets + self.enemies + self.allwalls,
            self.allpickups,
        )[0]
