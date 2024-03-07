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

    # Colors
    stamina_yellow = (255, 255, 10)
    food_green = (90, 255, 140)
    health_red = (255, 30, 70)
    bar_grey = (75, 75, 75)

    hunger_rate = 2500
    stamina_cooldown = 1000

    cd = {"spawn": 0, "bullet": 0, "food": 0, "stamina_regen": 0}

    while running:
        dt = clock.tick(globals.FPS) / 1000
        print(dt)
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
            "mouse_pos": mouse_pos,
            "dt": dt,
        }

        if cd["bullet"] >= 0:
            cd["bullet"] -= clock.get_time()
        if cd["spawn"] >= 0:
            cd["spawn"] -= clock.get_time()
        if cd["food"] <= hunger_rate:
            cd["food"] += clock.get_time()
        if cd["stamina_regen"] >= 0:
            cd["stamina_regen"] -= clock.get_time()

        if mouse_keys[0] and clock.get_time() - cd["bullet"] > 0:
            # players[0].food += 1
            cd["bullet"] = 75
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

        stamina_bar2 = pygame.Rect(20, 600, 258, 23)
        pygame.draw.rect(screen, bar_grey, stamina_bar2)
        stamina_bar = pygame.Rect(24, 604, int(players[0].stamina/players[0].max_stamina*250), 15)
        pygame.draw.rect(screen, stamina_yellow, stamina_bar)

        food_bar2 = pygame.Rect(20, 630, 258, 23)
        pygame.draw.rect(screen, bar_grey, food_bar2)
        food_bar = pygame.Rect(24, 634, int(players[0].food/players[0].max_food*250), 15)
        pygame.draw.rect(screen, food_green, food_bar)
        
        health_bar2 = pygame.Rect(20, 660, 258, 23)
        pygame.draw.rect(screen, bar_grey, health_bar2)
        health_bar = pygame.Rect(24, 664, int(players[0].health/players[0].max_health*250), 15)
        pygame.draw.rect(screen, health_red, health_bar)
        
            
        # Flip (draw) the display
        pygame.display.flip()
    #
    # End of running loop
    #=======================================

    pygame.quit()


if __name__ == "__main__":
    main()
