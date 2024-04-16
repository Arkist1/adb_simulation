from math import sqrt, atan2, degrees
import math
from .agent import Agent
from utils import Globals
from utils.logger import EnemyDetection, EnemyChangeState
import utils

import random
import pygame


class Enemy(Agent):
    """
    Represents an enemy agent in the game.

    Attributes:
        screen (pygame.Surface): The screen surface where the enemy is rendered.
        start_pos (list): The starting position of the enemy. Defaults to [250, 250].
        type (str): The type of the enemy. Defaults to None.
        colour (tuple): The colour of the enemy. Defaults to (255, 0, 0).
        weapon (object): The weapon object associated with the enemy.
        speed (float): The speed of the enemy.
    """

    def __init__(
        self,
        screen,
        start_pos=[250, 250],
        control_type=None,
        colour=(255, 0, 0),
        health=100,
        **kwargs
    ) -> None:
        super().__init__(
            screen,
            start_pos,
            control_type=control_type,
            colour=colour,
            health=health,
            **kwargs
        )
        self.weapon = None
        self.sound_circle = None
        self.poi = self.pos  # Point Of Interest (POI)

        self.speed = self.speed / 2
        self.alertspeed = self.speed / 3
        self.wanderspeed = self.speed / 4

        self.moving = False
        self.move_timer = 0
        self.blocked_timer = 0
        self.attack_cd = 1
        self.state = "wandering"  # states are ["wandering", "alert", "chasing"]
        self.vision_cone.vision_range = 300
        self.detected_agent = []

        self.damage = 25

    def get_move(self, inputs, entities):
        """
        Determines the movement of the enemy based on the inputs.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
        if self.controltype == "human":
            self.get_human_move(inputs, entities)

        if self.controltype == "enemy":
            self.get_enemy_move(inputs, entities)

    def get_enemy_move(self, inputs, entities):
        """
        Calculates the movement of the enemy towards the nearest player.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
        self.vision_cone.rotation = utils.angle_to(self.poi, self.pos)

        # if self.state == "chasing":
        #     self.poi = self.detected_agent

        if self.move_timer > 0:
            self.move_timer -= inputs["dt"] * Globals.SIM_SPEED

        elif self.state == "chasing":
            delta = self.get_move_delta(self.poi) * inputs["dt"] * Globals.SIM_SPEED

            self.attack_cd -= inputs["dt"] * Globals.SIM_SPEED
            # print("DELTA", delta)

            self.move(delta, entities)
            return

        # elif self.state == "alert":
        #     pass

        elif self.state in ["wandering", "alert"]:
            self.blocked_timer -= inputs["dt"] * Globals.SIM_SPEED

            sdelta = utils.abs_distance_to(self.pos, self.poi)
            # print("max delta", sdelta, self.wanderspeed)

            if (
                sdelta < self.speed * inputs["dt"] * 2 * Globals.SIM_SPEED
                or self.blocked_timer <= 0
            ):  # detect if poi position is within reach
                self.moving = False
                self.move_timer = random.random() * 4 + 2

            if not sdelta == 0:
                # calculate delta
                delta = self.get_move_delta(self.poi) * inputs["dt"] * Globals.SIM_SPEED

                self.move(delta, entities)
                return

        self.move(pygame.Vector2([0, 0]), entities)

    def get_move_delta(self, point):
        angle = utils.angle_to(point, self.pos)
        delta = utils.angle_to_direction(math.radians(angle)) * self.speed

        return delta

    def percept(self, tilemanager):
        """
        Checks if the given agent is within the vision cone of this enemy.

        Args:
            agent (Agent): The agent to check for collision.

        Returns:
            bool: True if the agent is within the vision cone, False otherwise.
        """
        visions = []
        sounds = []
        # for entity in entities.get_adjacent_players(self.pos):
        for entity in tilemanager.get_adjacent_players(
            tile_pos=self.current_tilemap_tile
        ):
            # print(entity)
            if self.detect(
                entity, tilemanager.get_tile(self.current_tilemap_tile).walls
            ):
                visions.append(entity)
                if "xander's ballencode" == "goed":
                    Globals.MAIN.logger.log(
                        EnemyDetection("vision", self.__hash__(), entity.__hash__())
                    )

            if self.hear(entity):
                sounds.append(entity)
                if "xander's ballencode" == "goed":
                    Globals.MAIN.logger.log(
                        EnemyDetection("sound", self.__hash__(), entity.__hash__())
                    )
                # print("sound")
            # if (entity.radius + self.radius + 10) > utils.dist(
            #     self.pos, entity.pos
            # ) and self.attack_cd <= 0:
            #     entity.health -= self.damage
            #     self.attack_cd = 1

        if visions:
            # print("vision detection has been made")
            # print(detections[0].pos)
            if self.state != "chasing":
                Globals.MAIN.logger.log(
                    EnemyChangeState(self.__hash__(), self.state, "chasing")
                )
            self.state = "chasing"
            self.poi = visions[0].pos.copy()
            self.last_agent = visions[0]
            self.last_agent.chasing_enemies.add(self)
            self.moving = True

        elif sounds:
            # print("sound detection has been made")
            if self.state != "alert":
                Globals.MAIN.logger.log(
                    EnemyChangeState(self.__hash__(), self.state, "alert")
                )
            self.state = "alert"
            self.poi = sounds[0].pos.copy()

            self.move_timer = 0
            self.moving = True
            self.blocked_timer = 3

        else:
            if self.state == "chasing":
                if self in self.last_agent.chasing_enemies:
                    self.last_agent.chasing_enemies.remove(self)
                Globals.MAIN.logger.log(
                    EnemyChangeState(self.__hash__(), self.state, "alert")
                )
                self.state = "alert"

            elif (
                not self.moving and self.move_timer <= 0
            ):  # Only get new poi if old one has been reached
                if self.state != "wandering":
                    Globals.MAIN.logger.log(
                        EnemyChangeState(self.__hash__(), self.state, "wandering")
                    )
                self.state = "wandering"

                self.poi = pygame.Vector2(
                    max(
                        min(
                            random.randrange(
                                round(self.pos[0]) - 200, round(self.pos[0]) + 200
                            ),
                            Globals.MAP_WIDTH - self.hitbox * 1.5,
                        ),
                        0 + self.hitbox * 1.5,
                    ),
                    max(
                        min(
                            random.randrange(
                                round(self.pos[1]) - 200, round(self.pos[1]) + 200
                            ),
                            Globals.MAP_HEIGHT - self.hitbox * 1.5,
                        ),
                        0 + self.hitbox * 1.5,
                    ),
                )
                self.moving = True
                self.blocked_timer = 3

        self.vision_detections = visions
        self.sound_detections = sounds

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed * Globals.SIM_SPEED,
            "POI": self.poi,
            "Blocked_timer": self.blocked_timer,
            "Move_timer": self.move_timer,
            "Visions_amt": len(self.vision_detections),
            "Sounds_amt": len(self.sound_detections),
            "State": self.state,
            "Health": self.health,
            "Pushable": self.is_pushable,
            "Curr_tilemap_tile": self.current_tilemap_tile,
        }
