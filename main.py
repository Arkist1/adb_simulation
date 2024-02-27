import pygame
import agent
import globals
import enemy
import bullet

pygame.init()

screen = pygame.display.set_mode([globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT])

running = True

players = [agent.Agent(screen=screen)]
enemies = []
boxes = []
bullets = []

clock = pygame.time.Clock()

cd = 0
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

    if cd >= 0:
        cd -= clock.get_time()

    if mouse_keys[0]:
        print("spawning bullet")
        bullets.append(bullet.Bullet(mouse_pos, 50, 50, screen))

    if keys[pygame.K_b] and clock.get_time() - cd > 0:
        cd = 1
        enemies.append(enemy.Enemy(screen=screen, type="enemy"))

    for en in enemies:
        en.get_move(inputs={"nearest_player": players[0], "dt": dt})

    for player in players:
        player.get_move(inputs)

    # needs to be implemented

    for bl in bullets:
        bl.move(inputs)
    # for bullet in bullets:
    #     bullet.move()
    #     bullet.draw(screen)

    ################ Drawing cycle ################
    screen.fill((255, 255, 255))  # white background

    for en in enemies:
        en.draw()

    for player in players:
        player.draw()

    for bl in bullets:
        print(bl.pos)
        bl.draw()

    # Flip the display

    pygame.display.flip()


# Done! Time to quit.

pygame.quit()
