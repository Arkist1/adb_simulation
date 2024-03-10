from camera import Camera, Camera_controller

from entities import Bullet, Agent, Wall, Pickup, Enemy
from utils import Object, Hitbox, Globals

import random
import pygame

from pygame._sdl2.video import Window


class EntityHolder:
    def __init__(self) -> None:
        self.players: list[Agent] = []
        self.boxes: list[Hitbox] = []
        self.bullets: list[Bullet] = []
        self.pickups: list[Pickup] = []
        self.enemies: list[Enemy] = []
        self.walls: list[Wall] = []
        
    def get_objects(self) -> list[Object]:
        return self.players + self.enemies + self.walls
    
    def get_items(self) -> list[Hitbox]:
        return self.players + self.boxes + self.bullets + self.pickups + self.enemies + self.walls

def main():

    pygame.init()

    screen = pygame.display.set_mode([Globals.SCREEN_WIDTH, Globals.SCREEN_HEIGHT])
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial" , 18 , bold = True)

    running = True
    entities = EntityHolder()
    entities.players.append(Agent(screen=screen))

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

    playercam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)
    followcam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)
    mapcam = Camera(pygame.Vector2([0, 0]), Globals.MAP_SIZE)
    freecam = Camera(pygame.Vector2([0, 0]), Globals.SCREEN_SIZE)

    cams = {
        "playercam": playercam,
        "mapcam": mapcam,
        "followcam": followcam,
        "freecam": freecam,
    }
    cameracontroller = Camera_controller(
        cams=cams, window=Window.from_display_module()
    )

    camera_target = entities.players[0]
    vectors = []

    while running:
        dt = clock.tick(Globals.FPS) / 1000
        dt_mili = clock.get_time()
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", True, (0, 0, 0))
        fps_position = (0, 0)

        # check for closing pygame._sdl2.video.Window
        for event in pygame.event.get():  # event loop
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_keys = pygame.mouse.get_pressed()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        current_player = entities.players[0]

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
        for pl in entities.players:
            if pl.health <= 0:
                entities.players.remove(pl)
                entities.players.append(Agent(screen=screen))

        ### pickup collision detection ###
        for pu in entities.pickups:
            if current_player.is_colliding(pu):
                entities.pickups.remove(pu)
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
            current_player.is_running = True
        elif inputs["crouch"] and current_player.stamina > 0:
            current_player.stamina -= 0.5
            current_player.speed = 150
            current_player.is_crouching = True
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
            for item in entities.get_items():
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
            entities.enemies.append(
                Enemy(screen=screen, type="enemy", start_pos=inputs["mouse_pos"])
            )

        ### manual pickup spawning ###
        if keys[pygame.K_n] and dt_mili - cd["spawn"] > 0:
            cd["spawn"] = 500
            entities.pickups.append(
                Pickup(
                    pickup_type=random.randint(0, 3),
                    start_pos=[random.randint(200, 600), random.randint(200, 600)],
                    screen=screen,
                )
            )
             
        entities.walls.append(Wall(screen, pygame.Vector2(200, 200)))

        if keys[pygame.K_f] and dt_mili - cd["cam_switch"] >= 0:
            cd["cam_switch"] = 10
            current_player.health -= 25

        ###### Perceptions #####
        for en in entities.enemies:
            en.percept()

        ###### Movement #####
        for en in entities.enemies:
            en.get_move(inputs={"nearest_player": current_player, "dt": dt}, entities=entities.get_objects())

        for player in entities.players:
            player.get_move(inputs, entities.get_objects())

            playercam.position = player.pos - playercam.size / 2
            # cam2.position = player.pos - cam2.size / 2

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
                freecam.apply_zoom(0.80)
            if keys[pygame.K_p]:
                freecam.apply_zoom(1.25)

        for bl in entities.bullets:
            bl.move(inputs)

        ### bullet fire ###
        if mouse_keys[0] and dt_mili - cd["bullet"] > 0:
            # current_player.food += 1
            cd["bullet"] = 75

            entities.bullets.append(current_player.shoot(inputs["mouse_pos"]))

        ################ Drawing cycle ################
            
        screen.fill((255, 255, 255))  # white background
        
        cam = cameracontroller.curr_cam
        screen.blit(fps_text, fps_position)

        for bl in entities.bullets:
            if bl.pos[0] >= Globals.MAP_WIDTH:
                entities.bullets.remove(bl)
            elif bl.pos[0] < 0:
                entities.bullets.remove(bl)
            elif bl.pos[1] >= Globals.MAP_HEIGHT:
                entities.bullets.remove(bl)
            elif bl.pos[1] < 0:
                entities.bullets.remove(bl)

            bl.draw(cam=cam)

        for pu in entities.pickups:
            pu.draw(cam=cam)

        for en in entities.enemies:
            en.draw(cam=cam)

        for player in entities.players:
            player.draw(cam=cam)
            
        for wall in entities.walls:
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
