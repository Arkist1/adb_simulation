import pygame
import agent
import globals
import enemy
import bullet
import random


def main():

    pygame.init()

    screen = pygame.display.set_mode([globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    running = True
    players = [agent.Agent(screen=screen)]
    enemies = []
    boxes = []
    bullets = []

    cd = {"spawn": 0, "bullet": 0}
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

        if cd["bullet"] >= 0:
            cd["bullet"] -= clock.get_time()
        if cd["spawn"] >= 0:
            cd["spawn"] -= clock.get_time()

        if mouse_keys[0] and clock.get_time() - cd["bullet"] > 0:
<<<<<<< HEAD
            cd["bullet"] = 0
=======
            cd["bullet"] = 1
>>>>>>> 1c10aa20e6aab904dd5ecd5304078d46a44aaf3e
            bullets.append(
                bullet.Bullet(
                    players[0].pos,
                    mouse_pos,
<<<<<<< HEAD
                    750,
=======
                    775,
>>>>>>> 1c10aa20e6aab904dd5ecd5304078d46a44aaf3e
                    50,
                    screen,
                    owner=players[0].weapon,
                )
            )

        if keys[pygame.K_b] and clock.get_time() - cd["spawn"] > 0:
            cd["spawn"] = 100
            enemies.append(enemy.Enemy(screen=screen, type="enemy"))

        for en in enemies:
            en.get_move(inputs={"nearest_player": players[0], "dt": dt})

        for player in players:
            player.get_move(inputs)

        # needs to be implemented

        if not mouse_keys[0]:
            for bl in bullets:
                bl.move(inputs)

        # for bullet in bullets:
        #     bullet.move()
        #     bullet.draw(screen)

        ################ Drawing cycle ################
        screen.fill((255, 255, 255))  # white background

        # pygame.draw.line(
        #     screen, (255, 0, 0), players[0].pos, pygame.math.Vector2(mouse_pos)
        # )

        # pygame.draw.line(
        #     screen,
        #     (255, 0, 0),
        #     players[0].pos,
        #     pygame.math.Vector2(players[0].pos[0] + 500, players[0].pos[1]),
        # )

        for en in enemies:
            en.draw()

        for bl in bullets:
            if bl.pos[0] >= globals.SCREEN_WIDTH:
                bullets.remove(bl)
            elif bl.pos[0] < 0:
                bullets.remove(bl)
            elif bl.pos[1] >= globals.SCREEN_HEIGHT:
                bullets.remove(bl)
            elif bl.pos[1] < 0:
                bullets.remove(bl)
            bl.draw()

        for player in players:
            player.draw()

        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    # =======================================

    pygame.quit()


if __name__ == "__main__":
    main()
