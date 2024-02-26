from agent import Agent

class Gun:
    def __init__(self):
        self.position = None # inherit from the player location
        self.fire_rate = 1
        self.bullet_damage = 1
        self.bullet_speed = 5

    def fire(self):
        #on pressing left mouse shoot a bullet
        pass

    def draw(self, screen):
        #draw the gun on the screen
        pass
