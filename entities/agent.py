from .gun import Gun
from .vision_cone import VisionCone
from utils import Globals, Object
from math import sqrt, cos, radians
import math
import pygame


class Agent(Object):
    """An agent instance"""

    def __init__(
        self,
        screen: pygame.Surface,
        start_pos: list[int] = [300, 300],
        type: str = "human",
        colour: tuple[int] = (0, 0, 255),
        size: int = 30,
        crouchspeed: int = 150,
        walkspeed: int = 300,
        sprintspeed: int = 450,
        stamina: int = 250,
        food: int = 250,
        health: int = 250,
    ) -> None:
        super().__init__(pos=pygame.Vector2(start_pos[0], start_pos[1]), radius=size)
        self.controltype = type
        self.speeds = {"sprinting": 450, "walking": 300, "crouching": 150}
        self.speed = self.speeds["walking"]
        self.hitbox = size
        self.colour = colour
        self.screen = screen
        self.weapon = Gun(pos=self.pos, screen=self.screen)
        self.vision_cone = VisionCone(vision_range=700, screen=self.screen, owner=self)
        self.sound_detection_circle = None
        self.cos_half_vision_angle = cos(radians(self.vision_cone.vision_angle / 2))

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

    def get_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
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
        if inputs["sprint"] and self.stamina > 0:
            self.stamina -= 1
            self.speed = self.speeds["sprinting"]
            self.cd["stamina_regen"] = self.stamina_cooldown

            self.hunger_rate = self.hunger_rates["low"]
            self.is_running = True

        elif inputs["crouch"] and self.stamina > 0:
            self.stamina -= 0.5
            self.speed = self.speeds["crouching"]
            self.hunger_rate = self.hunger_rates["low"]

            self.cd["stamina_regen"] = self.stamina_cooldown
            self.is_crouching = True

        else:
            self.speed = self.speeds["walking"]

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

        self.weapon.get_move(inputs, center_pos=self.pos)
        self.vision_cone.get_rotate_vision_cone(inputs["mouse_pos"])

    def shoot(self, location):
        if self.weapon:
            return self.weapon.fire(from_pos=self.pos, to_pos=location)

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

        if self.controltype == "human":
            if self.is_crouching:
                self.update_sound_circle(cam, size=100)  # crouching detection circle
                self.is_crouching = False
            elif self.is_running:
                self.update_sound_circle(cam, size=400)  # running detection circle
                self.is_running = False
            else:
                self.update_sound_circle(cam, size=200)  # base detection circle

        if self.weapon:
            self.weapon.draw(cam, self.pos)

        if self.vision_cone:
            self.vision_cone.draw(cam)

    def angle_to(self, other):
        v1 = pygame.math.Vector2(other) - self.pos
        v2 = pygame.math.Vector2([0, 0])

        return v1.angle_to(v2)

    def angle_to_direction(self, angle):
        return pygame.math.Vector2(math.cos(angle), -math.sin(angle))

    def distance_to(self, other):
        dx = other[0] - self.pos[0]
        dy = other[1] - self.pos[1]

        sdelta = sum([abs(dx), abs(dy)])

        return sdelta

    def detect(self, entity):
        agent_direction = self.angle_to(entity.pos)
        agent_distance = self.distance_to(entity.pos)

        vision_range, rotation, vision_angle = self.vision_cone.get_vision_cone_info()

        print(
            f"{rotation + vision_angle / 2} > {agent_direction} > {rotation - vision_angle / 2}"
        )

        if agent_distance <= vision_range:
            left_rotation = rotation + vision_angle / 2
            right_rotation = rotation - vision_angle / 2

            if (
                left_rotation > agent_direction > right_rotation
                or right_rotation > agent_direction
                and left_rotation > 180
                or left_rotation < agent_direction
                and right_rotation < -180
            ):
                return True

        return False

    def update_sound_circle(self, cam, size):
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.pos * cam.zoom - cam.position,
            (self.hitbox + size) * cam.zoom,
            1,
        )
        self.sound_detection_circle = (
            self.pos * cam.zoom - cam.position,
            (self.hitbox + size) * cam.zoom,
        )

    def get_sound_circle(self):
        return self.sound_detection_circle

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
        }
