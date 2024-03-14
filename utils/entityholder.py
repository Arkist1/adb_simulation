import entities
from .object import Object
from .hitbox import Hitbox


class EntityHolder:
    def __init__(self) -> None:
        self.players: list[entities.Agent] = []
        self.boxes: list[entities.Hitbox] = []
        self.bullets: list[entities.Bullet] = []
        self.pickups: list[entities.Pickup] = []
        self.enemies: list[entities.Enemy] = []
        self.walls: list[entities.Wall] = []

    def get_objects(self) -> list[Object]:
        return self.players + self.enemies + self.walls
    
    def get_mortal(self) -> list[Object]:
        return self.enemies

    def get_items(self) -> list[Hitbox]:
        return (
            self.players
            + self.boxes
            + self.bullets
            + self.pickups
            + self.enemies
            + self.walls
        )
