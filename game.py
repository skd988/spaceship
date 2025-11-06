import pygame
import math
import random
import os

SPACESHIP_SIZE = (136, 160)

SHOT_RADIUS = 10
SHOT_SPEED = 5

SPACESHIP_SPEED = 4

HAZARD_RADIUS = 15
HAZARD_CHANCE = 0.03
HAZARD_SPEED = 3

WIN_LENGTH = 1600
WIN_HEIGHT = 1600

CENTER = (WIN_LENGTH / 2, WIN_HEIGHT / 2)

WIN = pygame.display.set_mode((WIN_LENGTH, WIN_HEIGHT))
SPACESHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'spaceship.png')), SPACESHIP_SIZE)

FPS = 60

BACKGROUND_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


"""
Rotate a point around another by angle
"""
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


"""
handles movement of multiple objects, removes objects that go out of the screen
"""
def handle_movement(to_move, speed, remove=True, rotate=False):
    to_remove = []
    for object in to_move:
        dir = object['direction'] if 'direction' in object else angle_to_direction(object['angle'])
        mult = speed / math.sqrt(dir[0]**2 + dir[1]**2)
        object['location'][0] += dir[0] * mult
        object['location'][1] += dir[1] * mult

        size = object['surface'].get_size()
        if remove and not -size[0] / 2 <= object['location'][0] <= WIN_LENGTH + size[0] / 2 or not -size[1] / 2 <= object['location'][1] <= WIN_HEIGHT + size[1] / 2:
            to_remove.append(object)
        if rotate:
            object['angle'] = (object['angle'] + 1) % 360
            object['surface'] = pygame.transform.rotate(object['orig_surface'], object['angle'])

    if remove:
        for object in to_remove:
            to_move.remove(object)


def get_top_left(surface, center):
    return list(surface.get_rect(center = center).topleft)


def handle_collisions(spaceship, shots, hazards):
    spaceship_mask = pygame.mask.from_surface(spaceship['surface'])
    spaceship_top_left = get_top_left(spaceship['surface'], spaceship['location'])
    hit = False
    hazards_to_remove = []
    shots_to_remove = []
    for hazard in hazards:
        hazard_mask = pygame.mask.from_surface(hazard['surface'])
        hazard_top_left = get_top_left(hazard['surface'], hazard['location'])
        if spaceship_mask.overlap(hazard_mask, (hazard_top_left[0] - spaceship_top_left[0], hazard_top_left[1] - spaceship_top_left[1])):
            hit = True
            hazards_to_remove.append(hazard)
            continue
        for shot in shots:
            shot_mask = pygame.mask.from_surface(shot['surface'])
            shot_top_left = get_top_left(shot['surface'], shot['location'])
            if shot_mask.overlap(hazard_mask, (hazard_top_left[0] - shot_top_left[0], hazard_top_left[1] - shot_top_left[1])):
                hazards_to_remove.append(hazard)
                shots_to_remove.append(shot)
                break
        for shot in shots_to_remove:
            shots.remove(shot)
        shots_to_remove = []

    for hazard in hazards_to_remove:
        hazards.remove(hazard)

    return hit


def draw(spaceship, shots, hazards):
    WIN.fill(BACKGROUND_COLOR)
    for shot in shots:
        WIN.blit(shot['surface'], get_top_left(shot['surface'], shot['location']))
    spaceship_mask = pygame.mask.from_surface(spaceship['surface'])
    
    WIN.blit(spaceship['surface'], get_top_left(spaceship['surface'], spaceship['location']))

    for hazard in hazards:
        WIN.blit(hazard['surface'], get_top_left(hazard['surface'], hazard['location']))

    pygame.display.update()


def angle_to_direction(angle):
    return [math.cos(math.radians(angle)), math.sin(math.radians(angle))]

def point_in_line(start_p, end_p, x):
    return ((end_p[1] - start_p[1]) / (end_p[0] - start_p[0])) * (x - start_p[0]) + start_p[1]

def create_polygon(max_points, min_width, max_width, min_height, max_height, color):
    num_points = random.randint(3, max_points)
    height = random.uniform(min_height, max_height)
    width = random.uniform(min_width, max_width)
    num_up_points = random.randint(0, num_points - 2)
    num_down_points = num_points - num_up_points - 2
    highest = random.randint(0, num_up_points + 1)
    lowest = random.randint(1 if highest == 0 else 0, num_down_points + (0 if highest == num_up_points + 1 else 1))

    distance = min(height, width) / num_points 
    if highest == 0:
        left_p_y = 0
    elif lowest == 0:
        left_p_y = height
    else:
        left_p_y = random.uniform(0, height)
    left_p = (0, left_p_y)
    if highest == num_up_points + 1:
        right_p_y = 0
    elif lowest == num_down_points + 1:
        right_p_y = height
    else:
        right_p_y = random.uniform(0, height)
    right_p = (width, right_p_y)

    up_points = [left_p]
    for i in range(num_up_points):
        point_x = random.uniform(up_points[-1][0] + distance, right_p[0] - distance * (num_up_points - i + 1))
        if i + 1 == highest:
            point_y = 0
        else:
            point_y = random.uniform(0, point_in_line(left_p, right_p, point_x) - distance)
        up_points += [(point_x, point_y)]
    up_points += [right_p]
    down_points = [left_p]

    for i in range(num_down_points):
        point_x = random.uniform(down_points[-1][0] + distance, right_p[0] - distance * (num_down_points - i + 1))
        if i + 1 == lowest:
            point_y = height
        else:   
            point_y = random.uniform(point_in_line(left_p, right_p, point_x) + distance, max_height)
        down_points += [(point_x, point_y)]
    
    down_points = down_points[1:]
    points = up_points + down_points[::-1]
    polygon = pygame.Surface((width, height))
    polygon.fill(BACKGROUND_COLOR)
    polygon.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.polygon(polygon, color, points)
    return polygon

def new_hazard(spaceship_location):
    side = random.randint(1, 4)
    match side:
        case 1:
            x = -HAZARD_RADIUS / 2
            y = random.uniform(0, WIN_HEIGHT)
        case 2:
            x = random.uniform(0, WIN_LENGTH)
            y = WIN_HEIGHT + HAZARD_RADIUS / 2
        case 3:
            x = WIN_LENGTH + HAZARD_RADIUS / 2
            y = random.uniform(0, WIN_HEIGHT)
        case 4:
            x = random.uniform(0, WIN_LENGTH)
            y = -HAZARD_RADIUS / 2

    direction = [(spaceship_location[0] - x) / WIN_LENGTH, (spaceship_location[1] - y) / WIN_HEIGHT]
    hazard = create_polygon(10, 100, 200, 100, 200, RED)
    return {'location': [x,y], 'surface': hazard.copy(), 'orig_surface': hazard, 'angle': 0, 'direction': direction}

def new_shot(spaceship):
    direction = angle_to_direction(spaceship['angle'])
    shot = pygame.Surface((SHOT_RADIUS*2, SHOT_RADIUS*2))
    shot.fill(BACKGROUND_COLOR)
    shot.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(shot, WHITE, (SHOT_RADIUS, SHOT_RADIUS), SHOT_RADIUS)

    mult = (SPACESHIP_SIZE[1] / 2 - SHOT_RADIUS) / math.sqrt(direction[0]**2 + direction[1]**2)
    return {'location': [spaceship['location'][i] + direction[i] * mult for i in range(2)], 'surface': shot, 'direction': direction}


def main():
    clock = pygame.time.Clock()
    
    shots = []
    hazards = []
    life = 10
    score = 0
    spaceship = {'surface': SPACESHIP_IMAGE.copy(), 'location': list(CENTER), 'angle': 0} 
    run = True
    last_f = clock.get_time()
    while life:
        if random.random() <= HAZARD_CHANCE:
            hazards.append(new_hazard(spaceship['location']))
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x, y = angle_to_direction(spaceship['angle'])
                    shots.append(new_shot(spaceship))

        handle_movement(shots, SHOT_SPEED)
        handle_movement(hazards, HAZARD_SPEED, rotate=True)
        shots_before = len(shots)
        if handle_collisions(spaceship, shots, hazards):
            life -= 1
        score += shots_before - len(shots)
        keys = pygame.key.get_pressed()
        if bool(keys[pygame.K_LEFT]) != bool(keys[pygame.K_RIGHT]):
                spaceship['angle'] = (spaceship['angle'] + (-1 if keys[pygame.K_LEFT] else 1) * SPACESHIP_SPEED) % 360  
                spaceship['surface'] = pygame.transform.rotate(SPACESHIP_IMAGE, -spaceship['angle'])
        if keys[pygame.K_UP]:
            handle_movement([spaceship], SPACESHIP_SPEED)
        if keys[pygame.K_DOWN]:
            handle_movement([spaceship], -SPACESHIP_SPEED)
        #if keys[pygame.K_SPACE]:
            #shots.append(new_shot(spaceship))


        draw(spaceship, shots, hazards)        
    print("score is", score)
    pygame.quit()

if __name__ == '__main__':
    main()