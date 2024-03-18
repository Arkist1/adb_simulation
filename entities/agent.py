from .gun import Gun
from .sword import Sword
from .vision_cone import VisionCone
from .sound_circle import SoundCircle
from utils import Globals, Object
import utils
from math import sqrt, cos, radians
import numpy
import pygame


class Agent(Object):
    """An agent instance"""

    def __init__(
        self,
        screen: pygame.Surface,
        start_pos: list[int] = [300, 300],
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
    ) -> None:
        super().__init__(pos=pygame.Vector2(start_pos[0], start_pos[1]), radius=size)
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

        # is moving flags
        self.is_crouching = False
        self.is_running = False

        self.cd = {"stamina_regen": 0, "food": 0}

        self.is_moving = False

        self.vision_detections = []
        self.pickup_detections = []
        self.poi = None

    def get_move(
        self, inputs: dict[str, bool], entities, bullets, mortals
    ) -> pygame.Vector2:
        """
        Returns the move for the agent based on the given inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the inputs for the agent.

        Returns:
            pygame.Vector2: The move for the agent.
        """
        # generic move code
        for key, value in self.cd.items():
            if self.cd[key] >= 0:
                self.cd[key] = max(0, value - inputs["dt_mili"])

        ### sprint and crouch ###
        self.is_crouching = False
        self.is_running = False
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

        if type(self.weapon) == Sword and self.weapon.duration_cd >= 0:
            self.weapon.duration_cd -= inputs["dt_mili"]
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
            self.weapon.cd -= inputs["dt_mili"]

        if self.controltype == "human":
            return self.get_human_move(inputs, entities)

        if self.controltype == "random":
            return self.get_random_move()

    def get_human_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
        """
        Calculates the movement vector based on the user inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the user inputs.
                The keys represent the input types, and the values represent
                whether the input is active or not.

        Returns:
            pygame.Vector2: The movement vector calculated based on the user inputs.
        """
        s = self.speed * inputs["dt"]
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
        if self.weapon.cd <= 0:
            self.weapon.swing(location)
            self.weapon.cd = self.weapon.fire_rate
            self.weapon.size = self.weapon.sword_size
            self.weapon.duration_cd = self.weapon.duration

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
        for entity in tilemanager.get_mortal():
            if self.detect(entity, tilemanager(self.pos).walls):
                self.vision_detections.append(entity)
        for entity in tilemanager.allpickups:
            if self.detect(entity, tilemanager(self.pos).walls):
                self.pickup_detections.append(entity)
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

            if (
                left_rotation > agent_direction > right_rotation
                or (
                    (180 < agent_direction < right_rotation)
                    or (-180 + (left_rotation % 180) > agent_direction > -180)
                    and left_rotation > 180
                )
                or (
                    (left_rotation < agent_direction < -180)
                    or (180 > agent_direction > 180 + (right_rotation % 180))
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

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed,
            "Crouching": self.is_crouching,
            "Running": self.is_running,
            "Food": self.food,
            "Health": self.health,
            "Stamina": self.stamina,
            "Pushable": self.is_pushable,
            "Hunger rate": self.hunger_rate,
            "Visions": self.vision_detections,
        }
