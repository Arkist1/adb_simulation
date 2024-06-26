from typing import Any
import pygame
from . import Tile
from . import House
from . import Globals
from . import EntityHolder
from .logger import EntityDeath, EntitySpawn

from entities import Agent, Enemy, Pickup

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

        self.max_x = len(self.tiles)
        self.max_y = len(self.tiles[0])

    def get_curr_tile(self, pos: pygame.Vector2) -> list[int, int]:
        for xindex in range(0, self.max_x):
            if (
                self.tiles[xindex][0].pos.x
                <= pos.x
                <= self.tiles[xindex][0].pos.x + self.tile_width
            ):
                for yindex in range(0, self.max_y):
                    if (
                        self.tiles[xindex][yindex].pos.y
                        <= pos.y
                        <= self.tiles[xindex][yindex].pos.y + self.tile_height
                    ):
                        return [xindex, yindex]

    def is_in_tile(self, tile, pos):
        # print("checking if in current tile")
        if tile.pos.x <= pos.x <= tile.pos.x + tile.width:
            if tile.pos.y <= pos.y <= tile.pos.y + tile.height:
                return True

        return False

    def get_correct_tile(self, pos, center, xrange=1, yrange=1):
        # print("checking if in correct tile")
        for x in range(
            max(0, center[0] - xrange), min(self.max_x, center[0] + xrange + 1)
        ):
            for y in range(
                max(0, center[1] - yrange),
                min(self.max_y, center[1] + yrange + 1),
            ):
                if self.is_in_tile(self.tiles[x][y], pos):
                    return [x, y]

    def __call__(self, pos: pygame.Vector2) -> Tile:
        indices = self.get_curr_tile(pos)
        return self.tiles[indices[0]][indices[1]]

    @property
    def allwalls(self):  # DEPRECATED
        # print("getting all walls")
        res = []
        for row in self.tiles:
            for tile in row:
                for wall in tile.walls:
                    res.append(wall)

        return res

    @property
    def allpickups(self):  # DEPRECATED
        # print("getting all pickups")
        res = []
        for row in self.tiles:
            for tile in row:
                for pickup in tile.pickups:
                    res.append(pickup)

        return res

    @property
    def allplayers(self):  # DEPRECATED
        # print("getting all players")
        res = []
        for row in self.tiles:
            for tile in row:
                for player in tile.players:
                    res.append(player)

        return res

    @property
    def allenemies(self):  # DEPRECATED
        # print("getting all enemies")
        res = []
        for row in self.tiles:
            for tile in row:
                for enemy in tile.enemies:
                    res.append(enemy)

        return res

    def generate_terrain(self, templates, screen):
        for yindex in range(0, self.max_y):
            for xindex in range(0, self.max_x):
                if random.random() < templates["house_chance"]:
                    h = House(
                        self.tiles[xindex][yindex].pos
                        + pygame.Vector2(self.tile_width / 2, self.tile_height / 2),
                        template=templates["simple_house"],
                        screen=screen,
                    )

                    self.tiles[xindex][yindex].walls = h.walls
                    self.tiles[xindex][yindex].pickups = h.pickups
                    self.tiles[xindex][yindex].enemies = h.enemies
                    for en in h.enemies:
                        en.current_tilemap_tile = [xindex, yindex]

                    self.walls += h.walls
                    self.pickups += h.pickups
                    self.enemies += h.enemies

    def get_tiled_items(self, pos: pygame.Vector2):
        # print("getting tiled items")
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
        # print("getting all items")
        return (
            self.allplayers
            + self.boxes
            + self.bullets
            + self.allenemies
            + self.allwalls
            + self.allpickups
        )

    def get_adjacent_entities(
        self, pos=None, tile_pos=None, xrange=1, yrange=1, attr=None
    ):
        # print(f"getting all {attr} entities")
        # print(tile_pos)
        if not tile_pos:
            tile_pos = self.get_curr_tile(pos)

        center_x, center_y = tile_pos

        entities = []
        for x in range(
            max(0, center_x - xrange), min(self.max_x, center_x + xrange + 1)
        ):
            for y in range(
                max(0, center_y - yrange),
                min(self.max_y, center_y + yrange + 1),
            ):
                # print(x, y)
                res = getattr(self.tiles[x][y], attr)
                if callable(res):
                    entities += res()
                else:
                    entities += res
        return entities

    def get_adjacent_items(self, pos=None, tile_pos=None, xrange=1, yrange=1):
        return self.get_adjacent_entities(pos, tile_pos, xrange, yrange, "get_items")

    def get_adjacent_mortals(self, pos=None, tile_pos=None, xrange=1, yrange=1):
        return self.get_adjacent_entities(pos, tile_pos, xrange, yrange, "get_mortals")

    def get_adjacent_pickups(self, pos=None, tile_pos=None, xrange=1, yrange=1):
        return self.get_adjacent_entities(pos, tile_pos, xrange, yrange, "pickups")

    def get_adjacent_players(self, pos=None, tile_pos=None, xrange=1, yrange=1):
        return self.get_adjacent_entities(pos, tile_pos, xrange, yrange, "players")

    def update_tiles(self):
        # for x in range(self.max_x):
        #     for y in range(self.max_y):
        #         tile = self.tiles[x][y]
        #         for enemy in tile.enemies:
        #             if not self.is_in_tile(self.tiles[x][y], enemy.pos):
        #                 tile.enemies.remove(enemy)

        #                 new_x, new_y = self.get_correct_tile(enemy.pos, [x, y])
        #                 self.tiles[new_x][new_y].enemies.append(enemy)

        #                 enemy.curr_tilemap_tile = [new_x, new_y]

        #         # for player in tile.players:
        #         #     if not self.is_in_tile(self.tiles[x][y], player.pos):
        #         #         tile.players.remove(player)

        #         #         new_x, new_y = self.get_correct_tile(player.pos, [x, y])
        #         #         self.tiles[new_x][new_y].players.append(player)

        #         #         player.curr_tilemap_tile = [new_x, new_y]
        for enemy in self.enemies:
            if not (
                self.is_in_tile(self.get_tile(enemy.current_tilemap_tile), enemy.pos)
            ):
                self.get_tile(enemy.current_tilemap_tile).enemies.remove(enemy)

                new_tile_coords = self.get_correct_tile(
                    enemy.pos, enemy.current_tilemap_tile
                )
                self.get_tile(new_tile_coords).enemies.append(enemy)

                enemy.current_tilemap_tile = new_tile_coords

        for player in self.players:
            if not (
                self.is_in_tile(self.get_tile(player.current_tilemap_tile), player.pos)
            ):
                self.get_tile(player.current_tilemap_tile).players.remove(player)

                new_tile_coords = self.get_correct_tile(
                    player.pos, player.current_tilemap_tile
                )
                self.get_tile(new_tile_coords).players.append(player)

                player.current_tilemap_tile = new_tile_coords

    def add_entity(self, entity):
        if isinstance(entity, Enemy):
            x, y = self.get_curr_tile(entity.pos)
            self.tiles[x][y].enemies.append(entity)
            self.enemies.append(entity)
            entity.current_tilemap_tile = [x, y]
            Globals.MAIN.logger.log(EntitySpawn("enemy", entity.__hash__(), entity.pos))

        elif isinstance(entity, Agent):
            x, y = self.get_curr_tile(entity.pos)
            self.tiles[x][y].players.append(entity)
            self.players.append(entity)
            entity.current_tilemap_tile = [x, y]
            Globals.MAIN.logger.log(EntitySpawn("agent", entity.__hash__(), entity.pos))

        elif isinstance(entity, Pickup):
            x, y = self.get_curr_tile(entity.pos)
            self.tiles[x][y].pickups.append(entity)
            self.pickups.append(entity)
            entity.current_tilemap_tile = [x, y]
            Globals.MAIN.logger.log(
                EntitySpawn("pickup", entity.__hash__(), entity.pos)
            )

    def remove_entity(self, entity):
        if isinstance(entity, Enemy):
            x, y = entity.current_tilemap_tile
            # print(entity, "tiles:", self.tiles[x][y].enemies)
            self.tiles[x][y].enemies.remove(entity)
            # indices = self.get_curr_tile(entity.pos)
            # self.tiles[indices[0]][indices[1]].enemies.remove(entity)
            self.enemies.remove(entity)
            Globals.MAIN.logger.log(EntityDeath("enemy", entity.__hash__(), entity.pos))

        elif isinstance(entity, Agent):
            indices = self.get_curr_tile(entity.pos)
            self.tiles[indices[0]][indices[1]].players.remove(entity)
            self.players.remove(entity)
            Globals.MAIN.logger.log(EntityDeath("agent", entity.__hash__(), entity.pos))

        elif isinstance(entity, Pickup):
            indices = self.get_curr_tile(entity.pos)
            self.tiles[indices[0]][indices[1]].pickups.remove(entity)
            self.pickups.remove(entity)
            Globals.MAIN.logger.log(
                EntityDeath("pickup", entity.__hash__(), entity.pos)
            )
            
        return entity

    def get_tile(self, tile_pos):
        return self.tiles[tile_pos[0]][tile_pos[1]]
