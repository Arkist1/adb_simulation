import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
import agent

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

root2 = 2**1 / 2

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

running = True

pos = [250, 250]

clock = pygame.time.Clock()

player = agent.Agent()

while running:
    # check for closing window
    for event in pygame.event.get():  # event loop
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    keypresses = {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d}

    inputs = {
        "up": keys[pygame.K_w],
        "down": keys[pygame.K_s],
        "left": keys[pygame.K_a],
        "right": keys[pygame.K_d],
    }

    mov = player.get_move(inputs)
    print(mov)
    pos[0] += mov[0]
    pos[1] += mov[1]

    ################ Drawing cycle ################

    screen.fill((255, 255, 255))  # white background
    pygame.draw.circle(screen, (0, 0, 255), pos, 75)  # circle

    # Flip the display

    pygame.display.flip()

    clock.tick(60) / 1000


# Done! Time to quit.

pygame.quit()
