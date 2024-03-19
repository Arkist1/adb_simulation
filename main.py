from camera import Camera, Camera_controller

from entities import Bullet, Agent, Wall, Pickup, Enemy
from utils import Object, Hitbox, Globals, EntityHolder, House, TileManager

import random
import pygame
import json
import math

from pygame._sdl2.video import Window


def main():
    pygame.init()
    pygame.font.init()

    FONT = pygame.font.SysFont("Bahnschrift", 20)

    screen = pygame.display.set_mode([Globals.SCREEN_WIDTH, Globals.SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    running = True

    # tilemanager init
    tilemanager = TileManager(Globals.TILE_SIZE, Globals.MAP_SIZE)
    middle_x = math.floor(len(tilemanager.tiles) / 2)
    middle_y = math.floor(len(tilemanager.tiles[0]) / 2)
    middle_tile = tilemanager.tiles[middle_x][middle_y]
    middle_pos = middle_tile.pos + middle_tile.size / 2

    tilemanager.players.append(Agent(screen=screen, start_pos=middle_pos.copy()))

    # Colors
    stamina_yellow = (255, 255, 10)
    food_green = (90, 255, 140)
    health_red = (255, 30, 70)
    bar_grey = (75, 75, 75)

    cd = {
        "spawn": 0,
        "bullet": 0,
        "cam_switch": 0,
        "target_cd": 0,
        "zoom": 0,
        "draw_switch": 0,
        "fps": 0,
    }

    playercam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)
    followcam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)
    mapcam = Camera(pygame.Vector2([0, 0]), Globals.MAP_SIZE)
    freecam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)
    simcam = Camera(pygame.Vector2([0, 0]), Globals.MAP_SIZE)
    memecam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)

    cams = {
        "playercam": playercam,
        "mapcam": mapcam,
        "followcam": followcam,
        "freecam": freecam,
        "simcam": simcam,
        "memecam": memecam,
    }
    cameracontroller = Camera_controller(cams=cams, window=Window.from_display_module())
    cameracontroller.curr_cam = memecam

    camera_target = tilemanager.players[0]
    vectors = []

    # MAP GEN
    templates = json.load(open("no_houses_templates.json", "r"))
    tilemanager.generate_terrain(templates, screen=screen)

    while running:
        dt = clock.tick(Globals.FPS) / 1000
        dt_mili = clock.get_time()
        fps = clock.get_fps()
        fps_position = (0, 0)

        # check for closing pygame._sdl2.video.Window
        for event in pygame.event.get():  # event loop
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_keys = pygame.mouse.get_pressed()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        current_player = tilemanager.players[0]

        inputs = {
            "up": keys[pygame.K_w],
            "down": keys[pygame.K_s],
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
            "sprint": keys[pygame.K_LSHIFT],
            "crouch": keys[pygame.K_LCTRL],
            "attack": mouse_keys[0],
            "block": mouse_keys[2],
            "mouse_pos": mouse_pos / cameracontroller.curr_cam.zoom
            + cameracontroller.curr_cam.position / cameracontroller.curr_cam.zoom,
            "dt": dt,
            "dt_mili": dt_mili,
        }

        ### RESTART SIM ###
        if keys[pygame.K_r]:
            running = False
            Globals.RESTART = True
            break

        # if keys[pygame.K_p]:
        #     Globals.PAUSE =

        ### cooldowns ###
        for key, item in cd.items():
            if cd[key] >= 0:
                cd[key] = max(0, item - dt_mili)

        if cd["fps"] <= 0:
            cd["fps"] = 1000
            print(len(tilemanager.enemies), "FPS:", fps)

        for player in tilemanager.players:
            if player.health <= 0:
                tilemanager.players.remove(player)
                tilemanager.players.append(
                    Agent(screen=screen, start_pos=middle_pos.copy())
                )
                if (
                    isinstance(camera_target, Agent)
                    and camera_target not in tilemanager.players
                ):
                    camera_target = tilemanager.players[0]

                running = False
                Globals.RESTART = True
                continue
            player.percept(tilemanager)
            player.get_move(
                inputs,
                tilemanager.get_tiled_items(player.pos),
                tilemanager.bullets,
                tilemanager.get_mortal(),
            )

            playercam.position = player.pos - playercam.size / 2
            memecam.position = player.pos - memecam.size / 2

        ### pickup collision detection ###

        for pu in tilemanager(current_player.pos).pickups:
            if current_player.is_colliding(pu):
                tilemanager(current_player.pos).pickups.remove(pu)
                current_player.remove_pickup_from_memory(tilemanager, pu)
                if pu.pickup_type == 0 or pu.pickup_type == 1:
                    current_player.health = min(
                        (current_player.health + pu.picked_up()),
                        current_player.max_health,
                    )
                elif pu.pickup_type == 2 or pu.pickup_type == 3:
                    current_player.food = min(
                        (current_player.food + pu.picked_up()), current_player.max_food
                    )

        ### cam switch ###
        if mouse_keys[2] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 500
            cams = list(cameracontroller.cameras.keys())
            cameracontroller.change_cam(
                cams[(cams.index(cameracontroller.curr_cam_name) + 1) % len(cams)]
            )

        if dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 200
            if keys[pygame.K_1]:
                cameracontroller.change_cam("playercam")
            elif keys[pygame.K_2]:
                cameracontroller.change_cam("mapcam")
            elif keys[pygame.K_3]:
                cameracontroller.change_cam("followcam")
            elif keys[pygame.K_4]:
                cameracontroller.change_cam("freecam")
            elif keys[pygame.K_5]:
                cameracontroller.change_cam("simcam")
            elif keys[pygame.K_6]:
                cameracontroller.change_cam("memecam")
            else:
                cd["cam_switch"] = 0

        ### selector cam targeting ###
        if (mouse_keys[1] or keys[pygame.K_t]) and dt_mili - cd["target_cd"] >= 0:
            cd["target_cd"] = 500
            vectors = []
            closest_obj = None
            closest_dist = None
            for item in tilemanager.get_items():
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

        ###    Draw call switch   ###
        if keys[pygame.K_BACKSPACE] and cd["draw_switch"] <= 0:
            cd["draw_switch"] = 500
            Globals.DRAW = False if Globals.DRAW else True
            print("Drawing state:", Globals.DRAW)

        ### manual enemy spawning ###
        if keys[pygame.K_b] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 100
            tilemanager.enemies.append(
                Enemy(
                    screen=screen, control_type="enemy", start_pos=inputs["mouse_pos"]
                )
            )

        ### manual pickup spawning ###
        if keys[pygame.K_n] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 500
            tilemanager.pickups.append(
                Pickup(
                    pickup_type=random.randint(0, 3),
                    start_pos=inputs["mouse_pos"],
                    screen=screen,
                )
            )

        if keys[pygame.K_f] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 10
            current_player.health -= 25

        ###### Movement #####
        for en in tilemanager.enemies:
            if en.health <= 0:
                tilemanager.enemies.remove(en)
            en.percept(tilemanager)
            en.get_move(
                inputs={"nearest_player": current_player, "dt": dt},
                entities=tilemanager.get_tiled_items(en.pos),
            )

        if camera_target:
            followcam.position = camera_target.pos - followcam.size / 2

        ## free cam position movement
        if keys[pygame.K_UP]:
            freecam.position.y -= Globals.FREECAM_SPEED * dt
        if keys[pygame.K_DOWN]:
            freecam.position.y += Globals.FREECAM_SPEED * dt
        if keys[pygame.K_LEFT]:
            freecam.position.x -= Globals.FREECAM_SPEED * dt
        if keys[pygame.K_RIGHT]:
            freecam.position.x += Globals.FREECAM_SPEED * dt

        ## free cam zoom

        if cd["zoom"] <= 0:
            cd["zoom"] = 100
            if keys[pygame.K_o]:
                freecam.apply_zoom(1 / 0.8)
            elif keys[pygame.K_p]:
                freecam.apply_zoom(1 * 0.8)
            else:
                cd["zoom"] = 0

        for bl in tilemanager.bullets:
            bl.move(inputs)

        ##############################################
        ##              Drawing cycle               ##
        ##############################################

        if not Globals.DRAW:
            continue

        screen.fill((255, 255, 255))  # white background

        # FPS
        cam = cameracontroller.curr_cam
        cols = [(230, 230, 230), (200, 200, 200)]
        cols_searched = [(210, 250, 210), (180, 220, 180)]
        cols_visited = [(230, 210, 210), (200, 180, 180)]
        col_idx = 0

        for tile_row in tilemanager.tiles:
            for tile in tile_row:
                if tile in tilemanager.players[0].searched_tiles:
                    tile.draw(screen, cam, cols_searched[col_idx])
                elif tile in tilemanager.players[0].visited_tiles:
                    tile.draw(screen, cam, cols_visited[col_idx])
                else:
                    tile.draw(screen, cam, cols[col_idx])
                col_idx = 1 - col_idx

        fps_text = FONT.render(f"FPS: {int(fps)}", False, (0, 0, 0))
        screen.blit(fps_text, fps_position)

        # ZOOM
        if cam == freecam:
            txt = FONT.render(
                "x" + str(round(freecam.zoom * 10**3) / 10**3), False, (0, 0, 0)
            )
            screen.blit(txt, (Globals.SCREEN_WIDTH - txt.get_rect().width, 0))

        for bl in tilemanager.bullets:
            if bl.pos[0] >= Globals.MAP_WIDTH:
                tilemanager.bullets.remove(bl)
            elif bl.pos[0] < 0:
                tilemanager.bullets.remove(bl)
            elif bl.pos[1] >= Globals.MAP_HEIGHT:
                tilemanager.bullets.remove(bl)
            elif bl.pos[1] < 0:
                tilemanager.bullets.remove(bl)

            bl.draw(cam=cam)

        for pu in tilemanager.allpickups:
            pu.draw(cam=cam)

        for en in tilemanager.enemies:
            en.draw(cam=cam)

        for player in tilemanager.players:
            player.draw(cam=cam)

        for wall in tilemanager.allwalls:
            wall.draw(cam=cam)

        ######## Map boundary drawing ########
        boundry_rgb = (100, 0, 255)

        origin = pygame.Vector2(0, 0) * cam.zoom - cam.position
        bottom = pygame.Vector2(0, Globals.MAP_HEIGHT) * cam.zoom - cam.position
        right = pygame.Vector2(Globals.MAP_WIDTH, 0) * cam.zoom - cam.position
        rightbottom = (
            pygame.Vector2(Globals.MAP_WIDTH, Globals.MAP_HEIGHT) * cam.zoom
            - cam.position
        )

        pygame.draw.line(screen, boundry_rgb, origin, right)
        pygame.draw.line(screen, boundry_rgb, origin, bottom)
        pygame.draw.line(screen, boundry_rgb, right, rightbottom)
        pygame.draw.line(screen, boundry_rgb, bottom, rightbottom)

        ####### Status bars ######
        if cam in [playercam, simcam]:
            stamina_bar2 = pygame.Rect(20, 600, 258, 23)
            pygame.draw.rect(screen, bar_grey, stamina_bar2)
            stamina_bar = pygame.Rect(
                24,
                604,
                int(current_player.stamina / current_player.max_stamina * 250),
                15,
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
                24,
                664,
                int(current_player.health / current_player.max_health * 250),
                15,
            )
            pygame.draw.rect(screen, health_red, health_bar)

        # debug mode for cam
        if Globals.DEBUG and cam in [followcam, simcam] and camera_target:
            debug_info = camera_target.get_debug_info()

            txt = FONT.render("DEBUG: ", False, (0, 0, 0))
            screen.blit(txt, (0, 20))
            for index, (key, value) in enumerate(debug_info.items()):
                txt = FONT.render(f"{key}: {value}", False, (0, 0, 0))
                screen.blit(txt, (0, index * 18 + 40))

        # debug, draw vectors from mouse to every entity when targetting for target cam
        for en in tilemanager.get_mortal():
            if cd["target_cd"] != 0:
                pygame.draw.line(
                    screen,
                    (100, 200, 200),
                    tilemanager.players[0].pos * cam.zoom - cam.position,
                    en.pos * cam.zoom - cam.position,
                )

        if cam == memecam:
            IMPACT = pygame.font.SysFont("impact", 100)
            fps_text = IMPACT.render("GET REAL", False, (0, 0, 0))
            screen.blit(
                fps_text, (Globals.SCREEN_WIDTH / 2 - fps_text.get_rect().width / 2, 0)
            )

            fps_text = IMPACT.render("BOTTOM TEXT", False, (0, 0, 0))
            screen.blit(
                fps_text,
                (
                    (Globals.SCREEN_WIDTH / 2 - fps_text.get_rect().width / 2),
                    Globals.SCREEN_HEIGHT - fps_text.get_rect().height,
                ),
            )
        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    # =======================================


if __name__ == "__main__":
    while Globals.RESTART:
        print("Starting new simulation")
        Globals.RESTART = False
        main()
    pygame.quit()
