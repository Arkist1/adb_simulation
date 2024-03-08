from pygame._sdl2.video import Window
import pygame
import agent
import globals
import enemy
import bullet
import random
import camera
import pickup


def main():
    pygame.init()

    screen = pygame.display.set_mode([globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    running = True
    players = [agent.Agent(screen=screen)]
    enemies = []
    boxes = []
    bullets = []
    pickups = []

    # Colors
    stamina_yellow = (255, 255, 10)
    food_green = (90, 255, 140)
    health_red = (255, 30, 70)
    bar_grey = (75, 75, 75)

    hunger_rate = 2500
    stamina_cooldown = 1000

    cd = {
        "spawn": 0,
        "bullet": 0,
        "food": 0,
        "stamina_regen": 0,
        "cam_switch": 0,
        "target_cd": 0,
        "zoom": 0,
    }

    playercam = camera.Camera(pygame.Vector2([0, 0]), globals.SCREEN_SIZE)
    followcam = camera.Camera(pygame.Vector2([0, 0]), globals.SCREEN_SIZE)
    mapcam = camera.Camera(pygame.Vector2([0, 0]), globals.MAP_SIZE)
    freecam = camera.Camera(pygame.Vector2([0, 0]), globals.SCREEN_SIZE)

    cams = {
        "playercam": playercam,
        "mapcam": mapcam,
        "followcam": followcam,
        "freecam": freecam,
    }
    cameracontroller = camera.Camera_controller(
        cams=cams, window=Window.from_display_module()
    )

    camera_target = players[0]
    vectors = []

    while running:
        dt = clock.tick(globals.FPS) / 1000
        dt_mili = clock.get_time()

        # check for closing window
        for event in pygame.event.get():  # event loop
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_keys = pygame.mouse.get_pressed()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        current_player = players[0]

        inputs = {
            "up": keys[pygame.K_w],
            "down": keys[pygame.K_s],
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
            "sprint": keys[pygame.K_LSHIFT],
            "crouch": keys[pygame.K_LCTRL],
            "shoot": mouse_keys[0],
            "block": mouse_keys[2],
            "mouse_pos": mouse_pos / cameracontroller.curr_cam.zoom
            + cameracontroller.curr_cam.position,
            "dt": dt,
        }

        # print(
        #     f"{players[0].pos=}, {inputs['mouse_pos']=}, {cameracontroller.curr_cam.position=}"
        # )

        ### cooldowns ###
        for key, item in cd.items():
            if cd[key] >= 0:
                cd[key] = item - dt_mili

        ### kill player ###
        for pl in players:
            if pl.health <= 0:
                players.remove(pl)
                players.append(agent.Agent(screen=screen))

        ### pickup collision detection ###
        for pu in pickups:
            if current_player.is_colliding(pu):
                pickups.remove(pu)
                if pu.pickup_type == 0 or pu.pickup_type == 1:
                    current_player.health = min(
                        (current_player.health + pu.picked_up()),
                        current_player.max_health,
                    )
                elif pu.pickup_type == 2 or pu.pickup_type == 3:
                    current_player.food = min(
                        (current_player.food + pu.picked_up()), current_player.max_food
                    )

        ### sprint and crouch ###
        if inputs["sprint"] and current_player.stamina > 0:
            current_player.stamina -= 1
            current_player.speed = 450
            cd["stamina_regen"] = stamina_cooldown
        elif inputs["crouch"] and current_player.stamina > 0:
            current_player.stamina -= 0.5
            current_player.speed = 150
            cd["stamina_regen"] = stamina_cooldown
        else:
            current_player.speed = 300

        ### stamina regen ###
        if (
            cd["stamina_regen"] <= 0
            and current_player.stamina < current_player.max_stamina
        ):
            hunger_rate = 1000
            current_player.stamina += 0.75
        else:
            hunger_rate = 2500

        ### hunger depletion ###
        if cd["food"] >= hunger_rate:
            cd["food"] = 0
            current_player.food -= 1
            if current_player.food <= 0:
                current_player.food = 0
                current_player.health -= 0.5

        ### cam switch ###
        if mouse_keys[2] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 100
            cams = list(cameracontroller.cameras.keys())
            cameracontroller.change_cam(
                cams[(cams.index(cameracontroller.curr_cam_name) + 1) % len(cams)]
            )

        ### selector cam targeting ###
        if mouse_keys[1] and dt_mili - cd["target_cd"] >= 0:
            cd["target_cd"] = 500
            vectors = []
            closest_obj = None
            closest_dist = None
            for item in enemies + players + bullets + pickups + boxes:
                dist = abs(sum(inputs["mouse_pos"] - item.pos))
                vectors.append([inputs["mouse_pos"], item.pos.copy()])
                if not closest_dist:
                    closest_dist = dist
                    closest_obj = item
                    continue

                if closest_dist > dist:
                    closest_dist = dist
                    closest_obj = item

            camera_target = closest_obj

        if keys[pygame.K_g]:
            camera_target = None

        ### manual enemy spawning ###
        if keys[pygame.K_b] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 100
            enemies.append(
                enemy.Enemy(screen=screen, type="enemy", start_pos=inputs["mouse_pos"])
            )

        ### manual pickup spawning ###
        if keys[pygame.K_n] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 500
            pickups.append(
                pickup.Pickup(
                    pickup_type=random.randint(0, 3),
                    start_pos=[random.randint(200, 600), random.randint(200, 600)],
                    screen=screen,
                )
            )

        if keys[pygame.K_f] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 10
            current_player.health -= 25

        ###### Perceptions #####
        for en in enemies:
            en.percept()

        ###### Movement #####
        for en in enemies:
            en.get_move(inputs={"nearest_player": current_player, "dt": dt})

        for player in players:
            player.get_move(inputs)

            playercam.position = player.pos - playercam.size / 2
            # cam2.position = player.pos - cam2.size / 2

        if camera_target:
            followcam.position = camera_target.pos - followcam.size / 2

        ## free cam position movement
        if keys[pygame.K_UP]:
            freecam.position.y -= globals.FREECAM_SPEED * dt
        if keys[pygame.K_DOWN]:
            freecam.position.y += globals.FREECAM_SPEED * dt
        if keys[pygame.K_LEFT]:
            freecam.position.x -= globals.FREECAM_SPEED * dt
        if keys[pygame.K_RIGHT]:
            freecam.position.x += globals.FREECAM_SPEED * dt

        ## free cam zoom

        if cd["zoom"] <= 0:
            cd["zoom"] = 100
            if keys[pygame.K_o]:
                freecam.apply_zoom(0.80)
            if keys[pygame.K_p]:
                freecam.apply_zoom(1.25)

        for bl in bullets:
            bl.move(inputs)

        ### bullet fire ###
        if mouse_keys[0] and dt_mili - cd["bullet"] > 0:
            # current_player.food += 1
            cd["bullet"] = 75

            bullets.append(current_player.shoot(inputs["mouse_pos"]))

        ################ Drawing cycle ################

        screen.fill((255, 255, 255))  # white background

        cam = cameracontroller.curr_cam

        for bl in bullets:
            if bl.pos[0] >= globals.MAP_WIDTH:
                bullets.remove(bl)
            elif bl.pos[0] < 0:
                bullets.remove(bl)
            elif bl.pos[1] >= globals.MAP_HEIGHT:
                bullets.remove(bl)
            elif bl.pos[1] < 0:
                bullets.remove(bl)

            bl.draw(cam=cam)

        for pu in pickups:
            pu.draw(cam=cam)

        for en in enemies:
            en.draw(cam=cam)

        for player in players:
            player.draw(cam=cam)

        ######## Map boundary drawing ########
        boundry_rgb = (100, 0, 255)

        origin = pygame.Vector2(0, 0) * cam.zoom - cam.position
        bottom = pygame.Vector2(0, globals.MAP_HEIGHT) * cam.zoom - cam.position
        right = pygame.Vector2(globals.MAP_WIDTH, 0) * cam.zoom - cam.position
        rightbottom = (
            pygame.Vector2(globals.MAP_WIDTH, globals.MAP_HEIGHT) * cam.zoom
            - cam.position
        )

        pygame.draw.line(screen, boundry_rgb, origin, right)
        pygame.draw.line(screen, boundry_rgb, origin, bottom)
        pygame.draw.line(screen, boundry_rgb, right, rightbottom)
        pygame.draw.line(screen, boundry_rgb, bottom, rightbottom)

        ####### Status bars ######
        stamina_bar2 = pygame.Rect(20, 600, 258, 23)
        pygame.draw.rect(screen, bar_grey, stamina_bar2)
        stamina_bar = pygame.Rect(
            24, 604, int(current_player.stamina / current_player.max_stamina * 250), 15
        )
        pygame.draw.rect(screen, stamina_yellow, stamina_bar)

        food_bar2 = pygame.Rect(20, 630, 258, 23)
        pygame.draw.rect(screen, bar_grey, food_bar2)
        food_bar = pygame.Rect(
            24, 634, int(current_player.food / current_player.max_food * 250), 15
        )
        pygame.draw.rect(screen, food_green, food_bar)

        health_bar2 = pygame.Rect(20, 660, 258, 23)
        pygame.draw.rect(screen, bar_grey, health_bar2)
        health_bar = pygame.Rect(
            24, 664, int(current_player.health / current_player.max_health * 250), 15
        )
        pygame.draw.rect(screen, health_red, health_bar)

        # debug, draw vectors from mouse to every entity when targetting for target cam
        # for vector in vectors:
        #     if cd["target_cd"] != 0:
        #         pygame.draw.line(
        #             screen,
        #             (100, 200, 200),
        #             vector[0] * cam.zoom - cam.position,
        #             vector[1] * cam.zoom - cam.position,
        #         )

        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    # =======================================

    pygame.quit()


if __name__ == "__main__":
    main()
