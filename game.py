import pygame
import math
import random

TANK_RADIUS = 25

GUN_LENGTH = 70
GUN_WIDTH = 20

SHOT_RADIUS = 10
SHOT_SPEED = 2

HAZARD_CHANCE = 1
HAZARD_SPEED = 1

WIN_LENGTH = 800
WIN_WIDTH = 800

CENTER = (WIN_LENGTH / 2, WIN_WIDTH / 2)

WIN = pygame.display.set_mode((WIN_LENGTH, WIN_WIDTH))


FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def rotate_point(p, around_p, angle):
    s = math.sin(math.radians(angle))
    c = math.cos(math.radians(angle))

    p = list(p)
    p[0] -= around_p[0]
    p[1] -= around_p[1]

    x = p[0] * c - p[1] * s
    y = p[0] * s + p[1] * c
    new = [around_p[0] + x, around_p[1] + y]
    return new


def handle_movement(to_move, speed):
    to_remove = []
    for object in to_move:
        object['location'][0] += object['direction'][0] * speed
        object['location'][1] += object['direction'][1] * speed
        if not 0 <= object['location'][0] <= WIN_LENGTH or not 0 <= object['location'][1] <= WIN_WIDTH:
            to_remove.append(object)
    for object in to_remove:
        to_move.remove(object)


def handle_hazard_collision(tank, hazards):
    for hazard in hazards:
        pass
        

def draw(tank, shots, hazards):
    WIN.fill(BLACK)
    pygame.draw.circle(WIN, WHITE, tank['location'], TANK_RADIUS)
    gun_to_draw = pygame.transform.rotate(tank['gun'], -tank['angle'])
    rect = gun_to_draw.get_rect()
    rect.center = rotate_point((tank['location'][0] + GUN_LENGTH / 2, tank['location'][1]), tank['location'], tank['angle'])
    WIN.blit(gun_to_draw, rect)
    for shot in shots:
        pygame.draw.circle(WIN, WHITE, shot['location'], SHOT_RADIUS)

    for hazard in hazards:
        pygame.draw.circle(WIN, RED, hazard['location'], SHOT_RADIUS)

    pygame.display.update()

def angle_to_direction(angle):
    return [math.cos(math.radians(angle)), math.sin(math.radians(angle))]

def main():
    clock = pygame.time.Clock()
    
    shots = []
    hazards = []


    gun = pygame.Surface((GUN_LENGTH, GUN_WIDTH))
    gun.set_colorkey(BLACK)
    gun.fill(WHITE)

    tank = {'location': list(CENTER), 'angle': 0, 'gun': gun} 
    

    run = True
    while run:
        if random.random() <= HAZARD_CHANCE:
            side = random.randint(1, 4)
            match side:
                case 1:
                    x = 0
                    y = random.uniform(0, WIN_WIDTH)
                case 2:
                    x = random.uniform(0, WIN_LENGTH)
                    y = WIN_WIDTH
                case 3:
                    x = WIN_LENGTH
                    y = random.uniform(0, WIN_WIDTH)
                case 4:
                    x = random.uniform(0, WIN_LENGTH)
                    y = 0

            direction = [(tank['location'][0] - x) / WIN_LENGTH, (tank['location'][1] - y) / WIN_WIDTH]
            
            hazards.append({'location': [x, y], 'direction': direction})

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x, y = angle_to_direction(tank['angle'])
                    shots.append({'location': [tank['location'][0] + x * GUN_LENGTH, tank['location'][1] + y * GUN_LENGTH], 'direction': [x, y]})

        handle_movement(shots, SHOT_SPEED)
        handle_movement(hazards, HAZARD_SPEED)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            tank['angle'] = (tank['angle'] - 1) % 360
        if keys[pygame.K_RIGHT]:
            tank['angle'] = (tank['angle'] + 1) % 360
        if keys[pygame.K_UP]:
            x, y = angle_to_direction(tank['angle'])
            tank['location'][0] += x
            tank['location'][1] += y
        if keys[pygame.K_DOWN]:
            x, y = angle_to_direction(tank['angle'])
            tank['location'][0] -= x
            tank['location'][1] -= y
        
        draw(tank, shots, hazards)        
    
    pygame.quit()

if __name__ == '__main__':
    main()