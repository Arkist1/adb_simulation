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

    # Colors
    stamina_yellow = (255, 255, 10)
    food_green = (90, 255, 140)
    health_red = (255, 30, 70)
    bar_grey = (75, 75, 75)

    hunger_rate = 2500
    stamina_cooldown = 1000

    cd = {"spawn": 0, "bullet": 0, "food": 0, "stamina_regen": 0, "cam_switch": 0}

    cam1 = camera.Camera(pygame.Vector2([0, 0]), pygame.Vector2([1000, 700]))
    cam2 = camera.Camera(pygame.Vector2([200, 200]), pygame.Vector2([1000, 700]))

    cams = {"cam1": cam1, "cam2": cam2}
    cameracontroller = camera.Camera_controller(
        cams=cams, window=Window.from_display_module()
    )

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
            "sprint": keys[pygame.K_LSHIFT],
            "crouch": keys[pygame.K_LCTRL],
            "shoot": mouse_keys[0],
            "block": mouse_keys[2],
            "mouse_pos": mouse_pos + cameracontroller.get_current_cam_pos(),
            "dt": dt,
        }

        if cd["bullet"] >= 0:
            cd["bullet"] -= dt_mili
        if cd["spawn"] >= 0:
            cd["spawn"] -= dt_mili
        if cd["food"] <= hunger_rate:
            cd["food"] += dt_mili
        if cd["stamina_regen"] >= 0:
            cd["stamina_regen"] -= dt_mili
        if cd["cam_switch"] >= 0:
            cd["cam_switch"] -= dt_mili

        if mouse_keys[0] and dt_mili - cd["bullet"] > 0:
            # players[0].food += 1
            cd["bullet"] = 75
            bullets.append(
                bullet.Bullet(
                    players[0].pos,
                    inputs["mouse_pos"],
                    775,
                    50,
                    screen,
                    owner=players[0].weapon,
                )
            )

        if inputs["sprint"] and players[0].stamina > 0:
            players[0].stamina -= 0.5
            players[0].speed = 450
            cd["stamina_regen"] = stamina_cooldown
        elif inputs["crouch"] and players[0].stamina > 0:
            players[0].stamina -= 0.25
            players[0].speed = 150
            cd["stamina_regen"] = stamina_cooldown
        else:
            players[0].speed = 300

        if cd["stamina_regen"] <= 0 and players[0].stamina < players[0].max_stamina:
            players[0].stamina += 0.25

        if cd["food"] >= hunger_rate:
            cd["food"] = 0
            players[0].food -= 1
            if players[0].food <= 0:
                players[0].food = 0
                players[0].health -= 0.5

        if mouse_keys[2] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 1000
            (
                cameracontroller.change_cam("cam2")
                if cameracontroller.curr_cam_name == "cam1"
                else cameracontroller.change_cam("cam1")
            )

        if keys[pygame.K_b] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 100
            enemies.append(enemy.Enemy(screen=screen, type="enemy"))

        for en in enemies:
            en.get_move(inputs={"nearest_player": players[0], "dt": dt})

        for player in players:
            player.get_move(inputs)

            cam1.position = (
                player.pos
                - pygame.Vector2(globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT) / 2
            )

        # needs to be implemented

        for bl in bullets:
            bl.move(inputs)

        # for bullet in bullets:
        #     bullet.move()
        #     bullet.draw(screen)

        ################ Drawing cycle ################

        screen.fill((255, 255, 255))  # white background

        curr_cam_pos = cameracontroller.get_current_cam_pos()

        for bl in bullets:
            if bl.pos[0] >= globals.SCREEN_WIDTH:
                bullets.remove(bl)
            elif bl.pos[0] < 0:
                bullets.remove(bl)
            elif bl.pos[1] >= globals.SCREEN_HEIGHT:
                bullets.remove(bl)
            elif bl.pos[1] < 0:
                bullets.remove(bl)

            bl.draw(cam_pos=curr_cam_pos)

        for en in enemies:
            en.draw(cam_pos=curr_cam_pos)

        for player in players:
            player.draw(cam_pos=curr_cam_pos)

        ######## Map boundary drawing ########
        boundry_rgb = (100, 0, 255)

        origin = pygame.Vector2(0, 0) - curr_cam_pos
        bottom = pygame.Vector2(0, globals.SCREEN_HEIGHT) - curr_cam_pos
        right = pygame.Vector2(globals.SCREEN_WIDTH, 0) - curr_cam_pos
        rightbottom = (
            pygame.Vector2(globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT) - curr_cam_pos
        )

        pygame.draw.line(screen, boundry_rgb, origin, right)
        pygame.draw.line(screen, boundry_rgb, origin, bottom)
        pygame.draw.line(screen, boundry_rgb, right, rightbottom)
        pygame.draw.line(screen, boundry_rgb, bottom, rightbottom)

        stamina_bar2 = pygame.Rect(20, 600, 258, 23)
        pygame.draw.rect(screen, bar_grey, stamina_bar2)
        stamina_bar = pygame.Rect(
            24, 604, int(players[0].stamina / players[0].max_stamina * 250), 15
        )
        pygame.draw.rect(screen, stamina_yellow, stamina_bar)

        food_bar2 = pygame.Rect(20, 630, 258, 23)
        pygame.draw.rect(screen, bar_grey, food_bar2)
        food_bar = pygame.Rect(
            24, 634, int(players[0].food / players[0].max_food * 250), 15
        )
        pygame.draw.rect(screen, food_green, food_bar)

        health_bar2 = pygame.Rect(20, 660, 258, 23)
        pygame.draw.rect(screen, bar_grey, health_bar2)
        health_bar = pygame.Rect(
            24, 664, int(players[0].health / players[0].max_health * 250), 15
        )
        pygame.draw.rect(screen, health_red, health_bar)

        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    # =======================================

    pygame.quit()


if __name__ == "__main__":
    main()
