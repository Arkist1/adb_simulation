from camera import Camera, CameraController

from entities import Bullet, Agent, Wall, Pickup, Enemy
from utils import Object, Hitbox, Globals, EntityHolder, House, TileManager

import random
import pygame
import json
import math

from pygame._sdl2.video import Window


class Main:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.SysFont("Bahnschrift", 20)
        self.screen = pygame.display.set_mode(
            [Globals.SCREEN_WIDTH, Globals.SCREEN_HEIGHT]
        )
        self.clock = pygame.time.Clock()

        self.tile_manager = self.generate_tiles()
        self.camera_controller = self.generate_cameras()

        self.camera_target = self.tile_manager.players[0]
        self.cooldowns = {
            "spawn": 0,
            "bullet": 0,
            "cam_switch": 0,
            "target_self.cooldowns": 0,
            "zoom": 0,
            "draw_switch": 0,
            "fps": 0,
            "pause_switch": 0,
        }

        self.running = True

    def generate_tiles(self) -> TileManager:
        tile_manager = TileManager(Globals.TILE_SIZE, Globals.MAP_SIZE)

        middle_x = math.floor(len(tile_manager.tiles) / 2)
        middle_y = math.floor(len(tile_manager.tiles[0]) / 2)
        middle_tile = tile_manager.tiles[middle_x][middle_y]
        self.middle_pos = middle_tile.pos + middle_tile.size / 2

        tile_manager.players.append(
            Agent(screen=self.screen, start_pos=self.middle_pos.copy())
        )

        templates = json.load(open("no_houses_templates.json", "r"))
        tile_manager.generate_terrain(templates, screen=self.screen)
        return tile_manager

    def generate_cameras(self) -> CameraController:
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
        self.camera_controller = CameraController(
            cams=cams, window=Window.from_display_module()
        )
        self.camera_controller.curr_cam = memecam
        return self.camera_controller

    def start(self) -> None:
        while Globals.RESTART:
            print("Starting new simulation")
            Globals.RESTART = False
            self.run_simulation()
        pygame.quit()

    def run_simulation(self) -> None:
        while self.running:
            self.tick()

    def tick(self) -> None:
        dt = self.clock.tick(Globals.FPS) / 1000
        dt_mili = self.clock.get_time()
        fps = self.clock.get_fps()

        # check for closing pygame._sdl2.video.Window
        for event in pygame.event.get():  # event loop
            if event.type == pygame.QUIT:
                self.running = False

        self.handle_inputs(dt, dt_mili)
        self.handle_cooldowns(dt_mili, fps)

        if Globals.DRAW:
            self.draw(fps)

    def handle_inputs(self, dt, dt_mili) -> None:
        keys = pygame.key.get_pressed()
        mouse_keys = pygame.mouse.get_pressed()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        inputs = {
            "up": keys[pygame.K_w],
            "down": keys[pygame.K_s],
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
            "sprint": keys[pygame.K_LSHIFT],
            "crouch": keys[pygame.K_LCTRL],
            "attack": mouse_keys[0],
            "block": mouse_keys[2],
            "mouse_pos": mouse_pos / self.camera_controller.curr_cam.zoom
            + self.camera_controller.curr_cam.position
            / self.camera_controller.curr_cam.zoom,
            "dt": dt,
            "dt_mili": dt_mili,
        }

        self.handle_sim_state(keys, inputs)
        self.handle_players(inputs)
        self.handle_cams(dt_mili, inputs, keys, mouse_keys)
        self.handle_debug(dt_mili, keys)  # TODO Remove this
        self.handle_entity_movement(dt, inputs)
        self.handle_camera_movement(dt, keys)

    def handle_sim_state(self, keys, inputs):
        if keys[pygame.K_r]:
            self.running = False
            Globals.RESTART = True
            return

        self.cooldowns["pause_switch"] = max(
            0, self.cooldowns["pause_switch"] - inputs["dt_mili"]
        )

        if keys[pygame.K_p] and self.cooldowns["pause_switch"] == 0:
            Globals.PAUSE = not Globals.PAUSE
            print("Pause_state:", Globals.PAUSE)
            self.cooldowns["pause_switch"] = 500

        if Globals.PAUSE:
            return

        if keys[pygame.K_BACKSPACE] and self.cooldowns["draw_switch"] <= 0:
            self.cooldowns["draw_switch"] = 500
            Globals.DRAW = False if Globals.DRAW else True
            print("Drawing state:", Globals.DRAW)

    def handle_players(self, inputs):
        for player in self.tile_manager.players:
            if player.health <= 0:
                self.tile_manager.players.remove(player)
                self.tile_manager.players.append(
                    Agent(screen=self.screen, start_pos=self.middle_pos.copy())
                )
                if (
                    isinstance(self.camera_target, Agent)
                    and self.camera_target not in self.tile_manager.players
                ):
                    self.camera_target = self.tile_manager.players[0]

                self.running = False
                Globals.RESTART = True
                continue
            player.percept(self.tile_manager)
            player.get_move(
                inputs,
                self.tile_manager.get_tiled_items(player.pos),
                self.tile_manager.bullets,
                self.tile_manager.get_mortal(),
            )

            self.camera_controller.cameras["playercam"].position = (
                player.pos - self.camera_controller.cameras["playercam"].size / 2
            )
            self.camera_controller.cameras["memecam"].position = (
                player.pos - self.camera_controller.cameras["memecam"].size / 2
            )

    def handle_cams(self, dt_mili, inputs, keys, mouse_keys):
        if mouse_keys[2] and dt_mili - self.cooldowns["cam_switch"] >= 0:
            self.cooldowns["cam_switch"] = 500
            cams = list(self.camera_controller.cameras.keys())
            self.camera_controller.change_cam(
                cams[(cams.index(self.camera_controller.curr_cam_name) + 1) % len(cams)]
            )

        if dt_mili - self.cooldowns["cam_switch"] >= 0:
            self.cooldowns["cam_switch"] = 200
            if keys[pygame.K_1]:
                self.camera_controller.change_cam("playercam")
            elif keys[pygame.K_2]:
                self.camera_controller.change_cam("mapcam")
            elif keys[pygame.K_3]:
                self.camera_controller.change_cam("followcam")
            elif keys[pygame.K_4]:
                self.camera_controller.change_cam("freecam")
            elif keys[pygame.K_5]:
                self.camera_controller.change_cam("simcam")
            elif keys[pygame.K_6]:
                self.camera_controller.change_cam("memecam")
            else:
                self.cooldowns["cam_switch"] = 0

        if (mouse_keys[1] or keys[pygame.K_t]) and dt_mili - self.cooldowns[
            "target_self.cooldowns"
        ] >= 0:
            self.cooldowns["target_self.cooldowns"] = 500
            closest_obj = None
            closest_dist = None
            for item in self.tile_manager.get_items():
                dist = abs(sum(inputs["mouse_pos"] - item.pos))
                if not closest_dist:
                    closest_dist = dist
                    closest_obj = item
                    continue

                if closest_dist > dist:
                    closest_dist = dist
                    closest_obj = item

            self.camera_target = closest_obj

        if keys[pygame.K_g]:
            self.camera_target = None

    def handle_cooldowns(self, dt_mili, fps):
        for key, item in self.cooldowns.items():
            if self.cooldowns[key] >= 0:
                self.cooldowns[key] = max(0, item - dt_mili)

        if self.cooldowns["fps"] <= 0:
            self.cooldowns["fps"] = 1000
            print(len(self.tile_manager.enemies), "FPS:", fps)

    def handle_pickups(self) -> None:  # TODO Handle multiple agents
        current_player = self.tile_manager.players[0]
        for pu in self.tile_manager(current_player.pos).pickups:
            if current_player.is_colliding(pu):
                self.tile_manager(current_player.pos).pickups.remove(pu)
                current_player.remove_pickup_from_memory(self.tile_manager, pu)
                if pu.pickup_type == 0 or pu.pickup_type == 1:
                    current_player.health = min(
                        (current_player.health + pu.picked_up()),
                        current_player.max_health,
                    )
                elif pu.pickup_type == 2 or pu.pickup_type == 3:
                    current_player.food = min(
                        (current_player.food + pu.picked_up()), current_player.max_food
                    )

    def handle_manual_spawn(self, dt_mili, inputs, keys):

        ### manual enemy spawning ###
        if keys[pygame.K_b] and dt_mili - self.cooldowns["spawn"] > 0:
            self.cooldowns["spawn"] = 100
            self.tile_manager.enemies.append(
                Enemy(
                    screen=self.screen,
                    control_type="enemy",
                    start_pos=inputs["mouse_pos"],
                )
            )
        ### manual pickup spawning ###
        if keys[pygame.K_n] and dt_mili - self.cooldowns["spawn"] > 0:
            self.cooldowns["spawn"] = 500
            self.tile_manager.pickups.append(
                Pickup(
                    pickup_type=random.randint(0, 3),
                    start_pos=inputs["mouse_pos"],
                    screen=self.screen,
                )
            )

    def handle_debug(self, dt_mili, keys) -> None:  # TODO Remove this
        if keys[pygame.K_f] and dt_mili - self.cooldowns["cam_switch"] >= 0:
            self.cooldowns["cam_switch"] = 10
            self.tile_manager.players[0].health -= 25

    def handle_entity_movement(self, dt, inputs):
        for en in self.tile_manager.enemies:
            if en.health <= 0:
                self.tile_manager.enemies.remove(en)
            en.percept(self.tile_manager)
            en.get_move(
                inputs={"nearest_player": self.tile_manager.players[0], "dt": dt},
                entities=self.tile_manager.get_tiled_items(en.pos),
            )

        for bl in self.tile_manager.bullets:
            bl.move(inputs)

    def handle_camera_movement(self, dt, keys):
        if self.camera_target:
            self.camera_controller.cameras["followcam"].position = (
                self.camera_target.pos
                - self.camera_controller.cameras["followcam"].size / 2
            )

        ## free cam position movement
        if keys[pygame.K_UP]:
            self.camera_controller.cameras["freecam"].position.y -= (
                Globals.FREECAM_SPEED * dt
            )
        if keys[pygame.K_DOWN]:
            self.camera_controller.cameras["freecam"].position.y += (
                Globals.FREECAM_SPEED * dt
            )
        if keys[pygame.K_LEFT]:
            self.camera_controller.cameras["freecam"].position.x -= (
                Globals.FREECAM_SPEED * dt
            )
        if keys[pygame.K_RIGHT]:
            self.camera_controller.cameras["freecam"].position.x += (
                Globals.FREECAM_SPEED * dt
            )

        ## free cam zoom

        if self.cooldowns["zoom"] <= 0:
            self.cooldowns["zoom"] = 100
            if keys[pygame.K_o]:
                self.camera_controller.cameras["freecam"].apply_zoom(1 / 0.8)
            elif keys[pygame.K_p]:
                self.camera_controller.cameras["freecam"].apply_zoom(1 * 0.8)
            else:
                self.cooldowns["zoom"] = 0

    def draw(self, fps) -> None:  # TODO Split up in more functions

        self.screen.fill((255, 255, 255))  # white background

        # FPS
        cam = self.camera_controller.curr_cam
        cols = [(230, 230, 230), (200, 200, 200)]
        cols_searched = [(210, 250, 210), (180, 220, 180)]
        cols_visited = [(230, 210, 210), (200, 180, 180)]
        col_idx = 0

        for tile_row in self.tile_manager.tiles:
            for tile in tile_row:
                if (
                    tile in self.tile_manager.players[0].searched_tiles
                ):  # TODO Multiple agents
                    tile.draw(self.screen, cam, cols_searched[col_idx])
                elif (
                    tile in self.tile_manager.players[0].visited_tiles
                ):  # TODO Multiple agents
                    tile.draw(self.screen, cam, cols_visited[col_idx])
                else:
                    tile.draw(self.screen, cam, cols[col_idx])
                col_idx = 1 - col_idx

        fps_text = self.font.render(f"FPS: {int(max(0, fps))}", False, (0, 0, 0))
        self.screen.blit(fps_text, Globals.FPS_POSITION)

        # ZOOM
        if cam == self.camera_controller.cameras["freecam"]:
            txt = self.font.render(
                "x"
                + str(
                    round(self.camera_controller.cameras["freecam"].zoom * 10**3)
                    / 10**3
                ),
                False,
                (0, 0, 0),
            )
            self.screen.blit(txt, (Globals.SCREEN_WIDTH - txt.get_rect().width, 0))

        for bl in self.tile_manager.bullets:
            if bl.pos[0] >= Globals.MAP_WIDTH:
                self.tile_manager.bullets.remove(bl)
            elif bl.pos[0] < 0:
                self.tile_manager.bullets.remove(bl)
            elif bl.pos[1] >= Globals.MAP_HEIGHT:
                self.tile_manager.bullets.remove(bl)
            elif bl.pos[1] < 0:
                self.tile_manager.bullets.remove(bl)

            bl.draw(cam=cam)

        for pu in self.tile_manager.allpickups:
            pu.draw(cam=cam)

        for en in self.tile_manager.enemies:
            en.draw(cam=cam)

        for player in self.tile_manager.players:
            player.draw(cam=cam)

        for wall in self.tile_manager.allwalls:
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

        pygame.draw.line(self.screen, boundry_rgb, origin, right)
        pygame.draw.line(self.screen, boundry_rgb, origin, bottom)
        pygame.draw.line(self.screen, boundry_rgb, right, rightbottom)
        pygame.draw.line(self.screen, boundry_rgb, bottom, rightbottom)

        self.draw_status_bars(cam)

    def draw_status_bars(self, cam):  # TODO Split up in more functions
        if cam in [
            self.camera_controller.cameras["playercam"],
            self.camera_controller.cameras["simcam"],
        ]:
            stamina_bar2 = pygame.Rect(20, 600, 258, 23)
            pygame.draw.rect(self.screen, Globals.COLOR_BAR, stamina_bar2)
            stamina_bar = pygame.Rect(
                24,
                604,
                int(
                    self.tile_manager.players[0].stamina
                    / self.tile_manager.players[0].max_stamina
                    * 250
                ),  # TODO Multiple agents
                15,
            )
            pygame.draw.rect(self.screen, Globals.COLOR_STAMINA, stamina_bar)

            food_bar2 = pygame.Rect(20, 630, 258, 23)
            pygame.draw.rect(self.screen, Globals.COLOR_BAR, food_bar2)
            food_bar = pygame.Rect(
                24,
                634,
                int(
                    self.tile_manager.players[0].food
                    / self.tile_manager.players[0].max_food
                    * 250
                ),
                15,  # TODO Multiple agents
            )
            pygame.draw.rect(self.screen, Globals.COLOR_FOOD, food_bar)

            health_bar2 = pygame.Rect(20, 660, 258, 23)
            pygame.draw.rect(self.screen, Globals.COLOR_BAR, health_bar2)
            health_bar = pygame.Rect(
                24,
                664,
                int(
                    self.tile_manager.players[0].health
                    / self.tile_manager.players[0].max_health
                    * 250
                ),  # TODO Multiple agents
                15,
            )
            pygame.draw.rect(self.screen, Globals.COLOR_HEALTH, health_bar)

        # debug mode for cam
        if (
            Globals.DEBUG
            and cam
            in [
                self.camera_controller.cameras["followcam"],
                self.camera_controller.cameras["simcam"],
            ]
            and self.camera_target
        ):
            debug_info = self.camera_target.get_debug_info()

            txt = self.font.render("DEBUG: ", False, (0, 0, 0))
            self.screen.blit(txt, (0, 20))
            for index, (key, value) in enumerate(debug_info.items()):
                txt = self.font.render(f"{key}: {value}", False, (0, 0, 0))
                self.screen.blit(txt, (0, index * 18 + 40))

        # debug, draw vectors from mouse to every entity when targetting for target cam
        for en in self.tile_manager.get_mortal():
            if self.cooldowns["target_self.cooldowns"] != 0:
                pygame.draw.line(
                    self.screen,
                    (100, 200, 200),
                    self.tile_manager.players[0].pos * cam.zoom - cam.position,
                    en.pos * cam.zoom - cam.position,
                )

        if cam == self.camera_controller.cameras["memecam"]:
            IMPACT = pygame.font.SysFont("impact", 100)
            fps_text = IMPACT.render("GET REAL", False, (0, 0, 0))
            self.screen.blit(
                fps_text, (Globals.SCREEN_WIDTH / 2 - fps_text.get_rect().width / 2, 0)
            )

            fps_text = IMPACT.render("BOTTOM TEXT", False, (0, 0, 0))
            self.screen.blit(
                fps_text,
                (
                    (Globals.SCREEN_WIDTH / 2 - fps_text.get_rect().width / 2),
                    Globals.SCREEN_HEIGHT - fps_text.get_rect().height,
                ),
            )
        # Flip (draw) the display
        pygame.display.flip()


if __name__ == "__main__":
    main = Main()
    main.start()
