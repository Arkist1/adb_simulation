from gun import Gun


class Bullet:
    def __init__(self):
        self.possition = Gun.position
        self.speed = Gun.bullet_speed

    def move(self):
        self.possition[0] += self.speed
        self.possition[1] += self.speed
        return self.possition

    def draw(self, screen):
        pass