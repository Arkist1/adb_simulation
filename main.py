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
import globals

pygame.init()

screen = pygame.display.set_mode([globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT])

running = True

clock = pygame.time.Clock()
player = agent.Agent(screen=screen)

while running:
    dt = clock.tick(globals.FPS) / 1000
    # check for closing window
    for event in pygame.event.get():  # event loop
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mouse_keys = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    inputs = {
        "up": keys[pygame.K_w],
        "down": keys[pygame.K_s],
        "left": keys[pygame.K_a],
        "right": keys[pygame.K_d],
        "shoot": mouse_keys[0],
        "block": mouse_keys[2],
        "mouse_pos": mouse_pos,
        "dt": dt,
    }

    player.get_move(inputs)

    ################ Drawing cycle ################

    screen.fill((255, 255, 255))  # white background
    pygame.draw.circle(screen, (0, 0, 255), player.position, 75)  # circle

    # Flip the display

    pygame.display.flip()


# Done! Time to quit.

pygame.quit()
