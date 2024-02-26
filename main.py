import pygame
from objects import HitboxType, Object

SQR2 = 1.41421356237

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

def calculate_movement(keys: dict[str, bool], spd: float, dt: float) -> pygame.Vector2:
    s = spd * dt
    vec = pygame.Vector2(0, 0)
    
    if keys["up"]:
        vec.y -= s
    if keys["down"]:
        vec.y += s
    if keys["left"]:
        vec.x -= s
    if keys["right"]:
        vec.x += s
        
    if vec.x != 0 and vec.y != 0:
        vec.x /= SQR2
        vec.y /= SQR2
    
    return vec
        

class Player:
    def __init__(self, size: float, sw: int, sh: int, x: float, y: float) -> None:
        self.size = size
        self.sw = sw
        self.sh = sh
        self.x = x
        self.y = y
        
    def get_vec(self) -> pygame.Vector2:
        if self.x < self.size:
            self.x = self.size
        if self.y < self.size:
            self.y = self.size
        if self.x > self.sw - self.size:
            self.x = self.sw - self.size
        if self.y > self.sh - self.size:
            self.y = self.sh - self.size
            
        return pygame.Vector2(self.x, self.y)    
        
player = Object(screen.get_width(), screen.get_height(), screen.get_width() / 2 - 80, screen.get_height() / 2, 40)#pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player2 = Object(screen.get_width(), screen.get_height(), screen.get_width() / 2 + 80, screen.get_height() / 2, 40)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("gray")

    
    
    spd = 300

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LSHIFT]:
        spd = 600
    
    ks = {
        "up": keys[pygame.K_w],
        "down": keys[pygame.K_s],
        "left": keys[pygame.K_a],
        "right": keys[pygame.K_d]
    }
    velocity = calculate_movement(ks, spd, dt)
    
    player.move(velocity, [player2])
    #player2.move(velocity, [player])
    
    pygame.draw.circle(screen, "blue", player.pos, 40)
    pygame.draw.circle(screen, "red", player2.pos, 40)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()