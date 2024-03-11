from entities import Wall
from .entityholder import EntityHolder

import random
import pygame

def generate_y_wall(screen: pygame.Surface, entities: EntityHolder, loc: pygame.Vector2, door: bool):
    if not door:
        entities.walls.append(Wall(screen, loc, 330, 30))
    else:
        entities.walls.append(Wall(screen, loc + pygame.Vector2(-115, 0), 100, 30))
        entities.walls.append(Wall(screen, loc + pygame.Vector2(115, 0), 100, 30))
        
def generate_x_wall(screen: pygame.Surface, entities: EntityHolder, loc: pygame.Vector2, door: bool):
    if not door:
        entities.walls.append(Wall(screen, loc, 30, 300))
    else:
        entities.walls.append(Wall(screen, loc + pygame.Vector2(0, -115), 30, 100))
        entities.walls.append(Wall(screen, loc + pygame.Vector2(0, 115), 30, 100))

def generate_house(screen: pygame.Surface, entities: EntityHolder, loc: pygame.Vector2, door: int = 0):
    top = loc + pygame.Vector2(0, -150)
    bottom = loc + pygame.Vector2(0, 150)
    left = loc + pygame.Vector2(-150, 0)
    right = loc + pygame.Vector2(150, 0)
    
    generate_y_wall(screen, entities, top, door==0)
    generate_x_wall(screen, entities, right, door==1)
    generate_y_wall(screen, entities, bottom, door==2)
    generate_x_wall(screen, entities, left, door==3)

def generate_houses(screen: pygame.Surface, entities: EntityHolder):
    loc = pygame.Vector2(500, 500)
    generate_house(screen, entities, loc, door=random.randint(0, 3))
    