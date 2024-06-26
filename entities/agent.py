from .gun import Gun
from .sword import Sword
from .vision_cone import VisionCone
from .sound_circle import SoundCircle
from utils import Globals, Object, dist, angle_to_direction
from utils.logger import AgentDetection
import utils
import math
import numpy
import pygame
import random


class Agent(Object):
    """An agent instance"""

    def __init__(
        self,
        screen: pygame.Surface,
        start_pos: pygame.Vector2 = pygame.Vector2(200, 200),
        control_type: str = None,
        colour: tuple[int] = (0, 0, 255),
        size: int = 30,
        crouchspeed: int = 150,
        walkspeed: int = 300,
        sprintspeed: int = 450,
        base_sound_range: int = 200,
        stamina: int = 250,
        food: int = 250,
        health: int = 250,
        battle_type: str = "helper",
        battle_miss_chance: int = 0.1,
        **kwargs,
    ) -> None:
        super().__init__(pos=start_pos, radius=size)
        if control_type:
            self.controltype = control_type
        else:
            self.controltype = Globals.CONTROL_TYPE
        self.speeds = {
            "sprinting": sprintspeed,
            "walking": walkspeed,
            "crouching": crouchspeed,
        }
        self.speed = self.speeds["walking"]
        self.hitbox = size
        self.colour = colour
        self.screen = screen

        self.base_sound_range = base_sound_range

        self.weapon = Sword(owner=self, screen=self.screen)
        # self.weapon = Gun(pos=self.pos, screen=self.screen)
        self.vision_cone = VisionCone(vision_range=700, screen=self.screen, owner=self)
        self.sound_circle = SoundCircle(
            sound_range=self.base_sound_range, screen=self.screen, owner=self
        )

        # hp
        self.health = health
        self.max_health = health

        # food/hunger
        self.food = food
        self.max_food = food
        self.hunger_rate = 2500
        self.hunger_rates = {"high": 600, "low": 300}

        # staminda
        self.stamina = stamina
        self.max_stamina = stamina
        self.stamina_cooldown = 1000
        self.wait_for_stamina = 5000

        # is moving flags
        self.is_crouching = False
        self.is_running = False

        self.cd = {
            "stamina_regen": 0,
            "food": 0,
            "stamina_wait": 0,
            "stuck": 0,
            "unstuck": 0,
            "fleeing": 0,
        }

        self.is_moving = False

        self.vision_detections = []
        self.pickup_detections = []
        self.poi = None
        self.visited_tiles = set()
        self.searched_tiles = set()
        self.search_angle = -180
        self.tile_dict = {}
        self.tile_pickups = set()
        self.current_tile = None
        self.state = "explore"

        self.flee_angle = None
        self.flee_cd = 1500

        self.chasing_enemies = set()
        self.target_pickup = None

        self.lifetime = 0
        self.current_tilemap_tile = []

        self.battle_type = battle_type
        self.miss_chance = battle_miss_chance
        self.agents_history = {}

        # detective code
        self.detective_history = {}
        self.detective_sequence = [True, False, True, True]

        # kitten code
        self.kitten_cheat = 0

        # simpleton code
        self.simpleton_last_move = True

        # unstuck vars
        self.unstuck_angle = None
        self.last_pos = 0

    def memory(self, tilemanager, pickups):
        curr_tile = tilemanager.get_tile(
            self.current_tilemap_tile
        )  # tilemanager(self.pos)
        if curr_tile in self.visited_tiles and self.current_tile != curr_tile:
            self.tile_pickups = self.tile_dict[curr_tile]
        if self.current_tile == curr_tile:
            for p in pickups:
                self.tile_pickups.add(p)
            self.tile_dict[curr_tile] = self.tile_pickups
        else:
            self.tile_pickups = set()

        if curr_tile not in self.visited_tiles and self.current_tile:
            self.visited_tiles.add(self.current_tile)
            self.tile_dict[curr_tile] = []

        self.current_tile = curr_tile

    def remove_pickup_from_memory(self, pu):
        for tile, pickups in self.tile_dict.items():
            if pu in pickups:
                self.tile_dict[tile].remove(pu)

        # self.tile_dict[tilemanager.get_tile(self.current_tilemap_tile)].remove(pu)

        # self.tile_pickups = set(p for p in self.tile_pickups if p != pu)

    def get_move(self, inputs: dict[str, bool], entities, bullets, mortals) -> None:
        """
        Returns the move for the agent based on the given inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the inputs for the agent.

        Returns:
            pygame.Vector2: The move for the agent.
        """
        # print(self.current_tilemap_tile)
        self.lifetime += inputs["dt_mili"]
        # generic move code
        for key, value in self.cd.items():
            if self.cd[key] >= 0:
                self.cd[key] = max(0, value - inputs["dt_mili"] * Globals.SIM_SPEED)

        if type(self.weapon) == Sword and self.weapon.duration_cd >= 0:
            self.weapon.duration_cd -= inputs["dt_mili"] * Globals.SIM_SPEED
        else:
            self.weapon.size = 0
            self.weapon.did_damage = False

        ### stamina regen ###
        if self.cd["stamina_regen"] <= 0 and self.stamina < self.max_stamina:
            self.hunger_rate = self.hunger_rates["low"]
            self.stamina = min(0.75 + self.stamina, self.max_stamina)

        else:
            self.hunger_rate = self.hunger_rates["high"]

        ### hunger depletion ###
        if self.cd["food"] <= 0:
            self.cd["food"] = self.hunger_rate
            self.food -= 1
            if self.food <= 0:
                self.food = 0
                self.health -= 0.5

        if self.weapon and self.weapon.cd > 0:
            self.weapon.cd -= inputs["dt_mili"] * Globals.SIM_SPEED

        if self.controltype == "human":
            return self.get_human_move(inputs, entities, bullets, mortals)

        if self.controltype == "random":
            return self.get_random_move(inputs, entities)

        if self.controltype == "agent":
            self.get_agent_move(inputs, entities)
            target = None
            hit = False
            for entity in mortals:

                if self.weapon.hit(entity) and not self.weapon.did_damage:
                    # change for normal battle
                    # entity.health -= self.weapon.damage

                    target = entity
                    hit = True

            if hit and type(target) != type(self):
                self.battle_init(target, mortals)
            self.weapon.did_damage = True

    def standing(self):
        self.speed = self.speeds["walking"]
        self.sound_circle.sound_range = 0

    def walk(self):
        self.speed = self.speeds["walking"]
        self.sound_circle.sound_range = self.base_sound_range

    def sprint(self):
        self.stamina -= 1
        self.cd["stamina_regen"] = self.stamina_cooldown
        self.speed = self.speeds["sprinting"]

        self.hunger_rate = self.hunger_rates["low"]
        self.is_running = True
        self.sound_circle.sound_range = self.base_sound_range * 2

    def crouch(self):
        self.stamina -= 0.5
        self.cd["stamina_regen"] = self.stamina_cooldown
        self.speed = self.speeds["crouching"]

        self.hunger_rate = self.hunger_rates["low"]
        self.is_crouching = True
        self.sound_circle.sound_range = self.base_sound_range / 3

    def get_agent_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
        action_taken = False

        if self.vision_detections and not action_taken:
            action_taken = True
        action_taken = False

        
        if self.vision_detections and not action_taken:
            action_taken = True
            closest_enemy = None
            closest_dist = 0
            for en in self.vision_detections:
                if (
                    dist_ := utils.dist(self.pos, en.pos)
                ) < closest_dist or not closest_dist:
                    closest_dist = dist_
                    closest_enemy = en
            if (
                self.health >= (self.max_health * 0.5)
                and closest_enemy.state != "chasing"
                and self.stamina >= (self.max_stamina * 0.50)
            ):
                self.state = "sneak"
                self.sneak(inputs, entities, closest_enemy, closest_dist)
            elif self.health >= (self.max_health * 0.5) and self.stamina >= (
                self.max_stamina * 0.25
            ):
                self.state = "fight"
                self.fight(inputs, entities, closest_enemy, closest_dist)
            else:
                action_taken = False
            # TODO
            # else:
            #     self.state = "flee"
            #     self.flee(inputs, entities, self.vision_detections)

        if self.chasing_enemies and not action_taken:
            action_taken = True
            closest_enemy = None
            closest_dist = 0

            for en in self.chasing_enemies:
                if (
                    dist_ := utils.dist(self.pos, en.pos)
                ) < closest_dist or not closest_dist:
                    closest_dist = dist_
                    closest_enemy = en

            if self.health >= (self.max_health * 0.5) and (
                closest_dist < 130
                or self.food <= (self.max_food * 0.3)
                and self.stamina >= (self.max_stamina * 0.25)
            ):
                self.state = "fight"
                self.fight(inputs, entities, closest_enemy, closest_dist)
            else:
                self.state = "flee"
                self.flee(inputs, entities, self.chasing_enemies)

        if self.cd["fleeing"] > 0:
            self.flee(inputs, entities, None)
            action_taken = True
        if not action_taken:  # stucky states
            if self.cd["unstuck"] > 0:
                self.remove_pickup_from_memory(self.target_pickup)
                self.state = "unstuck"
                self.poi = None
                self.unstuck(inputs, entities)
            else:
                last_state = self.state
                if self.health <= (self.max_health * 0.5) and self.has_health_pickup():
                    self.state = "low_health"
                    self.low_health(inputs, entities)
                elif self.food < (self.max_food * 0.3) and self.has_food_pickup():
                    self.state = "low_food"
                    self.low_food(inputs, entities)
                else:
                    self.state = "explore"
                    self.explore(inputs, entities)

                if last_state != self.state:
                    self.cd["stuck"] = (random.random() + 1) * 1000 + 5000

                elif self.cd["stuck"] <= 0:
                    if self.last_pos:
                        if (
                            dist(self.last_pos, self.pos)
                            <= self.speed * inputs["dt"] * Globals.SIM_SPEED / 5
                        ):
                            if not self.state == "unstuck":
                                self.cd["unstuck"] = 1000
                                self.unstuck_angle = int(random.random() * 360) - 180

                        else:
                            self.cd["stuck"] = (random.random() + 1) * 1000 + 4000

        self.last_pos = self.pos.copy()
        self.chasing_enemies = set()
        # self.get_random_move(inputs, entities)

    def explore(self, inputs, entities):
        # Xander's ballencode
        self.target_pickup = None
        self.walk()
        if self.current_tile not in self.searched_tiles:
            tx = (self.pos.x // 1000) * 1000 + 500
            ty = (self.pos.y // 700) * 700 + 350
            center = pygame.Vector2(tx, ty)
            self.vision_cone.rotation = utils.angle_to(center, self.pos)
            if dist(self.pos, center) > (5 * Globals.SIM_SPEED):

                s = self.speed * inputs["dt"] * Globals.SIM_SPEED
                vec = center - self.pos
                vec = vec.normalize() * s
                self.move(vec, entities)

            else:
                self.poi = None
                self.standing()
                if self.search_angle < 180:
                    self.search_angle += 3 * Globals.SIM_SPEED

                else:
                    self.search_angle = -180
                    self.searched_tiles.add(self.current_tile)
                self.vision_cone.rotation = self.search_angle
        else:
            if not self.poi:
                tx = (self.pos.x // 1000) * 1000 + 500
                ty = (self.pos.y // 700) * 700 + 350
                directions = [0, 1, 2, 3]
                random.shuffle(directions)
                visit = 1
                for r in directions:
                    if visit == 0 or r == directions[3]:
                        # print("break")
                        break

                    direction = [[1000, 0], [-1000, 0], [0, 700], [0, -700]][r]
                    cent_point = [tx + direction[0], ty + direction[1]]

                    if cent_point[0] <= 0.0:
                        cent_point[0] += 1000
                    if cent_point[0] >= Globals.MAP_WIDTH:
                        cent_point[0] -= 1000
                    if cent_point[1] <= 0.0:
                        cent_point[1] += 700
                    if cent_point[1] >= Globals.MAP_HEIGHT:
                        cent_point[1] -= 700

                    center = pygame.Vector2(cent_point[0], cent_point[1])
                    self.poi = center.copy()

                    for tile in self.searched_tiles:
                        # print(
                        #     tile.pos,
                        #     tile.rect.center,
                        #     self.poi,
                        #     tile.rect.collidepoint(self.poi),
                        # )
                        if tile.rect.collidepoint(self.poi):
                            visit = 1
                            # print(visit)
                            break

                        else:
                            visit = 0
                            # print(visit)

                self.vision_cone.rotation = utils.angle_to(self.poi, self.pos)

            if dist(self.pos, self.poi) > (5 * Globals.SIM_SPEED):

                s = self.speed * inputs["dt"] * Globals.SIM_SPEED
                vec = self.poi - self.pos
                vec = vec.normalize() * s
                self.move(vec, entities)

            else:
                self.poi = None

    def fight(self, inputs, entities, closest_enemy, closest_dist):
        if closest_dist >= 100 and self.stamina >= (self.max_stamina * 0.5):
            self.sprint()
        else:
            self.walk()
        self.target_pickup = None
        self.poi = closest_enemy.pos.copy()
        if closest_dist <= 100:
            self.swing(self.poi)

        s = self.speed * inputs["dt"] * Globals.SIM_SPEED
        vec = self.poi - self.pos
        vec = vec.normalize() * s
        self.move(vec, entities)
        self.vision_cone.rotation = vec.angle_to([0, 0])

    def sneak(self, inputs, entities, closest_enemy, closest_dist):
        if closest_dist >= 250:
            self.walk()
        else:
            self.crouch()
        self.target_pickup = None
        self.poi = closest_enemy.pos.copy()
        if closest_dist <= 100:
            self.swing(self.poi)

        s = self.speed * inputs["dt"] * Globals.SIM_SPEED
        vec = self.poi - self.pos
        vec = vec.normalize() * s
        self.move(vec, entities)
        self.vision_cone.rotation = vec.angle_to([0, 0])

    def flee(self, inputs, entities, chasing_enemies):
        self.target_pickup = None
        self.poi = None
        if self.cd["fleeing"] > 0:
            self.walk()
            self.vision_cone.rotation = self.flee_angle.angle_to([0, 0])
            self.move((self.flee_angle * self.speed * inputs["dt"] * Globals.SIM_SPEED), entities)
            return
        if self.stamina >= 25 and self.cd["stamina_wait"] <= 0:
            self.sprint()
        else:
            self.wait_for_stamina = 5000
            self.walk()
        
        
        
        # calculating best angle to flee at
        self.flee_angle = pygame.Vector2([0, 0])
        for en in chasing_enemies:
            self.flee_angle += utils.angle_to_direction(
                math.radians(utils.angle_to(self.pos, en.pos))
            )

        self.flee_angle = self.flee_angle / len(chasing_enemies) + pygame.Vector2(
            random.random() / 5, random.random() / 5
        )
        self.vision_cone.rotation = self.flee_angle.angle_to([0, 0])
        self.move((self.flee_angle * self.speed * inputs["dt"] * Globals.SIM_SPEED), entities)
        self.cd["fleeing"] = self.flee_cd

    def low_health(self, inputs, entities):
        self.walk()
        # if (self.target_pickup):
        #     print(self.target_pickup.pos, self.pos)
        if not self.target_pickup or utils.dist(self.target_pickup.pos, self.pos) < 10:
            self.target_pickup = None
            closest_dist = 0

            for tile, pickups in self.tile_dict.items():
                for pickup in pickups:
                    if pickup.pickup_type < 2:
                        if (
                            dist_ := utils.dist(self.pos, pickup.pos)
                        ) < closest_dist or not closest_dist:
                            closest_dist = dist_
                            self.target_pickup = pickup

            # self.poi = target_tile.pos + (target_tile.size / 2)
            self.poi = self.target_pickup.pos.copy()
            self.vision_cone.rotation = utils.angle_to(self.poi, self.pos)

        # print(self.target_pickup, self.poi)
        if self.poi:
            if dist(self.pos, self.poi) > 5:
                s = self.speed * inputs["dt"] * Globals.SIM_SPEED
                vec = self.poi - self.pos
                vec = vec.normalize() * s
                self.move(vec, entities)

    def low_food(self, inputs, entities):
        self.walk()
        if not self.target_pickup or utils.dist(self.target_pickup.pos, self.pos) < 5:
            print("getting new target pickup")
            self.target_pickup = None
            closest_dist = 0

            for _, pickups in self.tile_dict.items():
                for pickup in pickups:
                    if pickup.pickup_type >= 2:
                        if (
                            dist_ := utils.dist(self.pos, pickup.pos)
                        ) < closest_dist or not closest_dist:
                            closest_dist = dist_
                            self.target_pickup = pickup

            # self.poi = target_tile.pos + (target_tile.size / 2)
            self.poi = self.target_pickup.pos.copy()
            self.vision_cone.rotation = utils.angle_to(self.poi, self.pos)

        if self.poi:
            if dist(self.pos, self.poi) > 5:
                s = self.speed * inputs["dt"] * Globals.SIM_SPEED
                vec = self.poi - self.pos
                vec = vec.normalize() * s
                self.move(vec, entities)

    def unstuck(self, inputs, entities):
        s = self.speed * inputs["dt"] * Globals.SIM_SPEED
        vec = angle_to_direction(math.radians(self.unstuck_angle)) * s
        # print(vec)
        self.vision_cone.rotation = self.unstuck_angle
        self.move(vec, entities)

    def has_health_pickup(self):
        for _, pickups in self.tile_dict.items():
            for pickup in pickups:
                if pickup.pickup_type < 2:
                    return True

        return False

    def has_food_pickup(self):
        for _, pickups in self.tile_dict.items():
            for pickup in pickups:
                if pickup.pickup_type >= 2:
                    return True

        return False

    def get_random_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
        s = self.speed * inputs["dt"] * Globals.SIM_SPEED
        vec = pygame.Vector2(
            random.randint(-100, 100) / 100 * s, random.randint(-100, 100) / 100 * s
        )
        self.move(vec, entities)
        self.vision_cone.rotation += random.randint(-5, 5)

    def get_human_move(
        self, inputs: dict[str, bool], entities, bullets, mortals
    ) -> pygame.Vector2:
        """
        Calculates the movement vector based on the user inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the user inputs.
                The keys represent the input types, and the values represent
                whether the input is active or not.

        Returns:
            pygame.Vector2: The movement vector calculated based on the user inputs.
        """
        moving = inputs["up"] or inputs["down"] or inputs["left"] or inputs["right"]

        if inputs["sprint"] and self.stamina > 0 and moving:
            self.stamina -= 1
            self.speed = self.speeds["sprinting"]
            self.cd["stamina_regen"] = self.stamina_cooldown

            self.hunger_rate = self.hunger_rates["low"]
            self.is_running = True
            self.sound_circle.sound_range = self.base_sound_range * 2

        elif inputs["crouch"] and self.stamina > 0 and moving:
            self.stamina -= 0.5
            self.speed = self.speeds["crouching"]
            self.hunger_rate = self.hunger_rates["low"]

            self.cd["stamina_regen"] = self.stamina_cooldown
            self.is_crouching = True
            self.sound_circle.sound_range = self.base_sound_range / 3

        elif moving:
            self.speed = self.speeds["walking"]
            self.sound_circle.sound_range = self.base_sound_range

        else:
            self.speed = self.speeds["walking"]
            self.sound_circle.sound_range = 0

        if inputs["attack"]:
            if type(self.weapon) == Gun:
                self.shoot(inputs["mouse_pos"], bullets)
            elif type(self.weapon) == Sword:
                self.swing(inputs["mouse_pos"])
                for entity in mortals:
                    if self.weapon.hit(entity) and not self.weapon.did_damage:
                        entity.health -= self.weapon.damage
                self.weapon.did_damage = True

        s = self.speed * inputs["dt"] * Globals.SIM_SPEED
        vec = pygame.Vector2(0, 0)

        if inputs["up"]:
            vec.y -= s
        if inputs["down"]:
            vec.y += s
        if inputs["left"]:
            vec.x -= s
        if inputs["right"]:
            vec.x += s

        if vec.x != 0 and vec.y != 0:
            vec.x /= Globals().SQR2
            vec.y /= Globals().SQR2

        # self.pos = self.pos + vec

        self.move(vec, entities)
        if type(self.weapon) == Gun:
            self.weapon.get_move(inputs, center_pos=self.pos)

        self.vision_cone.rotation = utils.angle_to(inputs["mouse_pos"], self.pos)

    def shoot(self, location, bullets):
        if self.weapon.cd <= 0:
            self.sound_circle.sound_range = self.base_sound_range * 4
            bullets.append(self.weapon.fire(from_pos=self.pos, to_pos=location))
            self.weapon.cd = self.weapon.fire_rate

    def swing(self, location):
        if self.weapon.cd <= 0 and self.stamina > 15:
            self.stamina -= 5
            self.cd["stamina_regen"] = self.stamina_cooldown
            self.weapon.swing(location)
            self.weapon.cd = self.weapon.fire_rate
            self.weapon.size = self.weapon.sword_size
            self.weapon.duration_cd = self.weapon.duration

    def take_damage(self, damage):
        self.health -= damage
        self.health = max(0, self.health)

    def do_battle(self, battle_summary):
        other_move = None
        for agent, move in battle_summary.agent_history.items():
            if agent is not self:
                other_move = move
                other_agent = agent
                if agent in self.agents_history:
                    self.agents_history[agent].append(move)
                else:
                    self.agents_history[agent] = [move]

        choice = True

        if self.battle_type == "cheater":
            choice = False

        elif self.battle_type == "helper":
            choice = True

        elif self.battle_type == "copycat":
            if other_move:
                choice = other_move

        elif self.battle_type == "copykitten":  # meow :3
            if not other_move:
                self.kitten_cheat += 1
            else:
                self.kitten_cheat = 0

            if self.kitten_cheat >= 2:
                choice = False

        elif self.battle_type == "simpleton":
            if other_move:
                choice = self.simpleton_last_move
            else:
                choice = not self.simpleton_last_move

        elif self.battle_type == "random":
            choice = True if random.random() > 0.5 else False

        elif self.battle_type == "grudger":
            if False in self.agents_history[other_agent]:
                choice = False

        elif self.battle_type == "detective":
            if other_agent not in self.detective_history:
                self.detective_history[other_agent] = []

            if not len(self.detective_history[other_agent]) < 4:
                choice = self.detective_sequence[
                    len(self.detective_history[other_agent])
                ]
            else:
                if False not in self.detective_history[other_agent]:
                    choice = False
                else:
                    choice = other_move

        if random.random() < self.miss_chance:
            choice = not choice

        self.simpleton_last_move = choice
        return choice

    def draw(self, cam):
        """
        Draw the agent on the screen.

        This method draws a circle representing the agent on the screen using the specified colour and position.
        If the agent has a weapon, it also calls the `draw` method of the weapon to draw it on the screen.
        """
        pygame.draw.circle(
            self.screen,
            self.colour,
            self.pos * cam.zoom - cam.position,
            self.hitbox * cam.zoom,
        )  # circle (player)

        if self.weapon:
            self.weapon.draw(cam, self.pos)

        if self.vision_cone:
            self.vision_cone.draw(cam)

        if self.sound_circle:
            self.sound_circle.draw(cam)

        if self.poi:
            pygame.draw.line(
                self.screen,
                (255, 100, 100),
                self.pos * cam.zoom - cam.position,
                self.poi * cam.zoom - cam.position,
            )

        for en in self.vision_detections:
            pygame.draw.line(
                self.screen,
                (100, 200, 200),
                self.pos * cam.zoom - cam.position,
                en.pos * cam.zoom - cam.position,
            )

        for en in self.pickup_detections:
            pygame.draw.line(
                self.screen,
                (200, 100, 200),
                self.pos * cam.zoom - cam.position,
                en.pos * cam.zoom - cam.position,
            )

    def percept(self, tilemanager):
        self.vision_detections = []
        self.pickup_detections = []
        for entity in tilemanager.get_adjacent_mortals(
            tile_pos=self.current_tilemap_tile
        ):
            if entity == self or type(entity) == type(self):
                continue
            if self.detect(
                entity, tilemanager.get_tile(self.current_tilemap_tile).walls
            ):
                self.vision_detections.append(entity)
                if "xander's ballencode" == "goed":
                    Globals.MAIN.logger.log(
                        AgentDetection("vision", self.__hash__(), entity.__hash__())
                    )

        # tile = tilemanager(self.pos)
        for entity in tilemanager.get_adjacent_pickups(
            tile_pos=self.current_tilemap_tile
        ):
            if self.detect(
                entity, tilemanager.get_tile(self.current_tilemap_tile).walls
            ):
                self.pickup_detections.append(entity)
                if "xander's ballencode" == "goed":
                    Globals.MAIN.logger.log(
                        AgentDetection("pickup", self.__hash__(), entity.__hash__())
                    )

        self.memory(tilemanager, self.pickup_detections)
        # print(self.pickup_detections)

    def detect(self, entity, objects):

        agent_direction = utils.angle_to(entity.pos, self.pos)
        agent_distance = utils.abs_distance_to(self.pos, entity.pos)

        vision_range, rotation, vision_angle = self.vision_cone.get_vision_cone_info()

        # print(
        #     f"{rotation + vision_angle / 2} > {agent_direction} > {rotation - vision_angle / 2}"
        # )

        if agent_distance <= vision_range:
            left_rotation = rotation + vision_angle / 2
            right_rotation = rotation - vision_angle / 2

            # print(f"{left_rotation=}, {right_rotation=}, {agent_direction=}")

            if (
                left_rotation > agent_direction > right_rotation
                or (
                    (180 < agent_direction < right_rotation)
                    or (-180 + (left_rotation % 180) > agent_direction > -180)
                    and left_rotation > 180
                )
                or (
                    (left_rotation < agent_direction < -180)
                    or (180 > agent_direction > 180 + (right_rotation % -180))
                    and -180 > right_rotation
                )
            ):
                vision_line = (self.pos, entity.pos)
                for object in objects:
                    wall = object.get_rect()
                    if wall.clipline(vision_line):
                        return False

                return True

        return False

    def hear(self, entity):
        return entity.sound_circle.sound_range > utils.dist(self.pos, entity.pos)

    def battle_init(self, target, mortals):
        self_team = self.help(mortals)
        enemy_team = target.help(mortals)
        battle = utils.Battle(self_team, enemy_team)
        battle.run_battle()
        battle_sum = utils.BattleSummary(battle)
        # print(battle_sum)
        return

    def ambush(self, target, mortals):
        self_team = target.help(mortals)
        enemy_team = self.help(mortals)
        battle = utils.Battle(self_team, enemy_team)
        battle.run_battle()
        battle_sum = utils.BattleSummary(battle)
        print(battle_sum)
        return
   
    def help(self, mortals):
        team = [self]

        for entity in mortals:

            if (
                1000 > utils.dist(self.pos, entity.pos)
                and entity != self
                and type(self) == type(entity)
            ):
                team.append(entity)
                return team
        return team

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed * Globals.SIM_SPEED,
            "Crouching": self.is_crouching,
            "Running": self.is_running,
            "Food": self.food,
            "Health": self.health,
            "Stamina": self.stamina,
            "Pushable": self.is_pushable,
            "Hunger rate": self.hunger_rate,
            "Visions_amt": len(self.vision_detections),
            "Chasers_amt": len(self.chasing_enemies),
            "Pickups_amt": len(self.pickup_detections),
            "State": self.state,
            "Has_hp_pickup": self.has_health_pickup(),
            "Has_food_pickup": self.has_food_pickup(),
            "Visited_tiles_amt": len(self.visited_tiles),
            "Searched_tiles_amt": len(self.searched_tiles),
            "Curr_tilemap_tile": self.current_tilemap_tile,
            "Poi": self.poi,
            "Stuck_timer": self.cd["stuck"],
            "Lifetime": self.lifetime,
        }
