from pygame._sdl2.video import Window
import pygame
import agent
import globals
import enemy
import bullet
import random
import camera


def main():

    pygame.init()

    screen = pygame.display.set_mode([globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    running = True
    players = [agent.Agent(screen=screen)]
    enemies = []
    boxes = []
    bullets = []

    cam1 = camera.Camera(pygame.Vector2([0, 0]), pygame.Vector2([1000, 700]))
    cam2 = camera.Camera(pygame.Vector2([200, 200]), pygame.Vector2([1000, 700]))

    cams = {"cam1": cam1, "cam2": cam2}
    cameracontroller = camera.Camera_controller(
        cams=cams, window=Window.from_display_module()
    )

    cd = {"spawn": 0, "bullet": 0, "cam_switch": 0}
    while running:
        dt = clock.tick(globals.FPS) / 1000
        dt_mili = clock.get_time()
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
        if cd["cam_switch"] >= 0:
            cd["cam_switch"] -= dt_mili

        if mouse_keys[0] and clock.get_time() - cd["bullet"] > 0:
            cd["bullet"] = 1
            bullets.append(
                bullet.Bullet(
                    players[0].pos,
                    mouse_pos,
                    775,
                    50,
                    screen,
                    owner=players[0].weapon,
                )
            )

        if mouse_keys[2] and clock.get_time() - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 1000
            (
                cameracontroller.change_cam("cam2")
                if cameracontroller.curr_cam_name == "cam1"
                else cameracontroller.change_cam("cam1")
            )

        if keys[pygame.K_b] and clock.get_time() - cd["spawn"] > 0:
            cd["spawn"] = 100
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

        curr_view = cameracontroller.get_current_cam_pos()

        for bl in bullets:
            if bl.pos[0] >= globals.SCREEN_WIDTH:
                bullets.remove(bl)
            elif bl.pos[0] < 0:
                bullets.remove(bl)
            elif bl.pos[1] >= globals.SCREEN_HEIGHT:
                bullets.remove(bl)
            elif bl.pos[1] < 0:
                bullets.remove(bl)

            bl.draw(cam_pos=curr_view)

        for en in enemies:
            en.draw(cam_pos=curr_view)

        for player in players:
            player.draw(cam_pos=curr_view)

        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    # =======================================

    pygame.quit()


if __name__ == "__main__":
    main()
