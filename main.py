from camera import Camera, CameraController

from entities import Bullet, Agent, Wall, Pickup, Enemy
from utils import (
    Globals,
    Logger,
    TileManager,
    ChangeSimState,
    ChangeDrawState,
    EnemyChangeState,
    ManualSpawn,
    dist,
    EntityPositionUpdate,
)

import pygame
from pygame._sdl2.video import Window

import random
import json
import math


class Main:
    def __init__(
        self, headless=False, self_restart=False, max_ticks=-1, prints=True
    ) -> None:

        self.headless = headless
        self.restart = self_restart
        self.max_ticks = max_ticks
        self.prints = prints

        self.first_sim = True
        self.n_ticks = 0

        if not self.headless:
            pygame.init()
            pygame.font.init()
            self.font = pygame.font.SysFont("Bahnschrift", 20)
            self.screen = pygame.display.set_mode(
                [Globals.SCREEN_WIDTH, Globals.SCREEN_HEIGHT]
            )
        else:
            self.screen = None

        self.clock = pygame.time.Clock()
        self.logger = Logger()
        Globals.MAIN = self

    def init_sim(self):
        self.tile_manager = self.generate_tiles()

        if not self.headless:
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
            "every_second": 0,
        }

        self.running = True

    def generate_tiles(self) -> TileManager:
        tile_manager = TileManager(Globals.TILE_SIZE, Globals.MAP_SIZE)

        if Globals.NUMBER_OF_AGENTS == 1:
            middle_x = math.floor(len(tile_manager.tiles) / 2)
            middle_y = math.floor(len(tile_manager.tiles[0]) / 2)
            middle_tile = tile_manager.get_tile([middle_x, middle_y])
            self.middle_pos = middle_tile.pos + middle_tile.size / 2

            tile_manager.add_entity(
                Agent(screen=self.screen, start_pos=self.middle_pos.copy())
            )
        else:
            for _ in range(Globals.NUMBER_OF_AGENTS):
                tile_manager.add_entity(
                    Agent(
                        screen=self.screen,
                        start_pos=pygame.Vector2(
                            [
                                int(random.random() * Globals.MAP_WIDTH),
                                int(random.random() * Globals.MAP_HEIGHT),
                            ]
                        ),
                    )
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
        self.camera_controller.curr_cam = simcam
        return self.camera_controller

    def start(self) -> None:
        while self.first_sim or self.restart:
            self.first_sim = False
            if self.prints:
                print("Initializing new simulation")
            self.init_sim()

            if self.prints:
                print("Starting new simulation")
            self.restart = False
            self.running = True
            self.run_simulation()

        if not self.headless:
            pygame.quit()

    def run_simulation(self) -> None:
        while self.running and (
            self.n_ticks < self.max_ticks or self.max_ticks < 0
        ):
            self.tick()

        if not self.headless:
            self.save_logs("log.json")

    def save_logs(self, file_location) -> None:
        with open(file_location, "w") as f:
            json.dump([log.dict() for log in self.logger.logs], f)

    def tick(self) -> None:
        self.n_ticks += 1
        dt = self.clock.tick(Globals.FPS) / 1000
        dt_mili = self.clock.get_time()
        fps = self.clock.get_fps()

        # check for closing pygame._sdl2.video.Window
        if not self.headless:
            for event in pygame.event.get():  # event loop
                if event.type == pygame.QUIT:
                    self.running = False

        self.tile_manager.update_tiles()

        self.handle_inputs(dt, dt_mili)

        if not self.running:
            return

        self.handle_cooldowns(dt_mili, fps)
        self.handle_pickups()

        if Globals.DRAW and not self.headless:
            self.draw(fps)

        if self.cooldowns["every_second"] == 0:
            self.every_second()
            self.cooldowns["every_second"] = 1000

    def every_second(self) -> None:
        self.logger.log(EntityPositionUpdate(self.tile_manager.players))

    def handle_inputs(self, dt, dt_mili) -> None:
        inputs = {"dt": dt, "dt_mili": dt_mili}

        if not self.headless:
            keys = pygame.key.get_pressed()
            mouse_keys = pygame.mouse.get_pressed()
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

            if keys[pygame.K_o] and self.cooldowns["pause_switch"] == 0:
                print(self.logger)
                self.cooldowns["pause_switch"] = 500

            inputs = inputs | {
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
            }

            self.handle_sim_state(keys, inputs)
            if not self.running:
                return

        self.handle_players(inputs)
        if not self.headless:
            self.handle_cams(dt_mili, inputs, keys, mouse_keys)
            self.handle_debug(dt_mili, keys)  # TODO Remove this
            self.handle_camera_movement(dt, keys)

        self.handle_entity_movement(dt, inputs)

    def handle_sim_state(self, keys, inputs):
        if keys[pygame.K_r]:
            self.running = False
            self.restart = True
            self.logger.log(ChangeSimState("restart"))
            return

        self.cooldowns["pause_switch"] = max(
            0, self.cooldowns["pause_switch"] - inputs["dt_mili"]
        )

        if keys[pygame.K_p] and self.cooldowns["pause_switch"] == 0:
            Globals.PAUSE = not Globals.PAUSE
            print("Pause_state:", Globals.PAUSE)
            self.logger.log(ChangeSimState(f"pause={Globals.PAUSE}"))
            self.cooldowns["pause_switch"] = 500

        if Globals.PAUSE:
            return

        if keys[pygame.K_BACKSPACE] and self.cooldowns["draw_switch"] <= 0:
            self.cooldowns["draw_switch"] = 500
            Globals.DRAW = False if Globals.DRAW else True
            ChangeDrawState(Globals.DRAW)
            print("Drawing state:", Globals.DRAW)

    def handle_players(self, inputs):
        for player in self.tile_manager.players:
            if player.health <= 0:
                self.tile_manager.remove_entity(player)
                # self.tile_manager.add_entity(
                #     Agent(screen=self.screen, start_pos=self.middle_pos.copy())
                # )

                self.running = False
                self.restart = True
                continue

            player.percept(self.tile_manager)
            player.get_move(
                inputs,
                self.tile_manager.get_adjacent_items(
                    tile_pos=player.current_tilemap_tile
                ),
                self.tile_manager.bullets,
                self.tile_manager.get_adjacent_mortals(
                    tile_pos=player.current_tilemap_tile
                ),
            )

            if not self.headless:
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
            for entity in self.tile_manager.get_items():
                distance = dist(inputs["mouse_pos"], entity.pos)
                if not closest_dist:
                    closest_dist = distance
                    closest_obj = entity
                    continue

                if closest_dist > distance:
                    closest_dist = distance
                    closest_obj = entity

            self.camera_target = closest_obj
            if isinstance(closest_obj, Agent) and self.prints:
                print(closest_obj.state)

        if keys[pygame.K_g]:
            self.camera_target = None

    def handle_cooldowns(self, dt_mili, fps):
        for key, item in self.cooldowns.items():
            if self.cooldowns[key] >= 0:
                self.cooldowns[key] = max(0, item - dt_mili)

        if self.cooldowns["fps"] <= 0:
            self.cooldowns["fps"] = 1000
            if self.prints:
                print(len(self.tile_manager.enemies), "FPS:", fps)

    def handle_pickups(self) -> None:  # TODO Handle multiple agents
        # current_player = self.tile_manager.allplayers[0]
        for player in self.tile_manager.players:
            for pu in self.tile_manager.get_adjacent_pickups(
                tile_pos=player.current_tilemap_tile
            ):
                if player.is_colliding(pu):
                    self.tile_manager.remove_entity(pu)
                    player.remove_pickup_from_memory(self.tile_manager, pu)
                    if pu.pickup_type == 0 or pu.pickup_type == 1:
                        player.health = min(
                            (player.health + pu.picked_up()),
                            player.max_health,
                        )
                    elif pu.pickup_type == 2 or pu.pickup_type == 3:
                        player.food = min(
                            (player.food + pu.picked_up()), player.max_food
                        )

    def handle_manual_spawn(self, dt_mili, inputs, keys):

        ### manual enemy spawning ###
        if keys[pygame.K_b] and dt_mili - self.cooldowns["spawn"] > 0:
            self.cooldowns["spawn"] = 100
            self.tile_manager.add_entity(
                Enemy(
                    screen=self.screen,
                    control_type="enemy",
                    start_pos=inputs["mouse_pos"],
                )
            )
            self.logger.log(ManualSpawn("enemy", inputs["mouse_pos"]))
        ### manual pickup spawning ###
        if keys[pygame.K_n] and dt_mili - self.cooldowns["spawn"] > 0:
            self.cooldowns["spawn"] = 500
            r = random.randint(0, 3)
            self.tile_manager.add_entity(
                Pickup(
                    pickup_type=r,
                    start_pos=inputs["mouse_pos"],
                    screen=self.screen,
                )
            )
            self.logger.log(ManualSpawn(f"pickup({r})", inputs["mouse_pos"]))

    def handle_debug(self, dt_mili, keys) -> None:  # TODO Remove this
        if keys[pygame.K_f] and dt_mili - self.cooldowns["cam_switch"] >= 0:
            self.cooldowns["cam_switch"] = 10
            self.tile_manager.players.health -= 25

    def handle_entity_movement(self, dt, inputs):
        for en in self.tile_manager.enemies:
            if en.health <= 0:
                self.tile_manager.remove_entity(en)
                continue

            en.percept(self.tile_manager)
            en.get_move(
                inputs={"dt": dt},
                entities=self.tile_manager.get_adjacent_items(
                    tile_pos=en.current_tilemap_tile
                ),
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
        if type(self.camera_target) == Agent:
            self.draw_player = self.camera_target
        else:
            self.draw_player = self.tile_manager.players[0]

        self.screen.fill((255, 255, 255))  # white background

        # FPS
        cam = self.camera_controller.curr_cam
        cols = [(230, 230, 230), (200, 200, 200)]
        cols_searched = [(210, 250, 210), (180, 220, 180)]
        cols_visited = [(230, 210, 210), (200, 180, 180)]
        col_idx = 0

        for tile_row in self.tile_manager.tiles:
            for tile in tile_row:
                if tile in self.draw_player.searched_tiles:  # TODO Multiple agents
                    tile.draw(self.screen, cam, cols_searched[col_idx])
                elif tile in self.draw_player.visited_tiles:  # TODO Multiple agents
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

        for pu in self.tile_manager.pickups:
            pu.draw(cam=cam)

        for en in self.tile_manager.enemies:
            en.draw(cam=cam)

        for player in self.tile_manager.players:
            # print(player)
            player.draw(cam=cam)

        for wall in self.tile_manager.walls:
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
                    self.draw_player.stamina / self.draw_player.max_stamina * 250
                ),  # TODO Multiple agents
                15,
            )
            pygame.draw.rect(self.screen, Globals.COLOR_STAMINA, stamina_bar)

            food_bar2 = pygame.Rect(20, 630, 258, 23)
            pygame.draw.rect(self.screen, Globals.COLOR_BAR, food_bar2)
            food_bar = pygame.Rect(
                24,
                634,
                int(self.draw_player.food / self.draw_player.max_food * 250),
                15,  # TODO Multiple agents
            )
            pygame.draw.rect(self.screen, Globals.COLOR_FOOD, food_bar)

            health_bar2 = pygame.Rect(20, 660, 258, 23)
            pygame.draw.rect(self.screen, Globals.COLOR_BAR, health_bar2)
            health_bar = pygame.Rect(
                24,
                664,
                int(
                    self.draw_player.health / self.draw_player.max_health * 250
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
        # if Globals.DEBUG:
        #     for en in self.tile_manager.get_mortals():
        #         if self.cooldowns["target_self.cooldowns"] != 0:
        #             pygame.draw.line(
        #                 self.screen,
        #                 (100, 200, 200),
        #                 self.draw_player.pos * cam.zoom - cam.position,
        #                 en.pos * cam.zoom - cam.position,
        #             )

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
    main = Main(headless=False, self_restart=Globals.RESTART)
    main.start()
