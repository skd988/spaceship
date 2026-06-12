import pygame
import math
import random
import os

SPACESHIP_SIZE = (136, 160)

SHOT_RADIUS = 10
SHOT_SPEED = 5

SPACESHIP_SPEED = 4
STARTING_LIFE = 3

HAZARD_CHANCE = 0.03
HAZARD_SPEED = 3

MIN_HAZARD_WIDTH = 100
MAX_HAZARD_WIDTH = 300
MIN_HAZARD_HEIGHT = 100
MAX_HAZARD_HEIGHT = 300
MAX_HAZARD_POINTS = 7

WIN_LENGTH = 1600
WIN_HEIGHT = 800

CENTER = (WIN_LENGTH / 2, WIN_HEIGHT / 2)

WIN = pygame.display.set_mode((WIN_LENGTH, WIN_HEIGHT))
SPACESHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'spaceship.png')), SPACESHIP_SIZE)

DEFAULT_FPS = 60

BACKGROUND_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (144, 213, 255)

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
    Handles movement of multiple object. 
    If remove is true, removes objects that go out of the screen.
"""
def handle_movement(to_move, speed, rotate=False):
    to_remove = []
    for object in to_move:
        dir = object['direction'] if 'direction' in object else angle_to_direction(object['angle'])
        mult = speed / math.sqrt(dir[0]**2 + dir[1]**2)
        object['location'][0] += dir[0] * mult
        object['location'][1] += dir[1] * mult

        if rotate:
            object['angle'] = (object['angle'] + 1) % 360
            object['surface'] = pygame.transform.rotate(object['orig_surface'], object['angle'])

        if is_object_out_of_screen(object, 1):
            to_remove.append(object)

    for object in to_remove:
        to_move.remove(object)


"""
    Returns whether an object is out of the screen by percentage 
    percentage=1 means the object need to be fully out of screen, 
    percentage=0 means that the object need to be just touching out of screen
"""
def is_object_out_of_screen(object, percentage):
    size = object['surface'].get_size()
    size_coefficient = 0.5 - percentage
    return not size_coefficient * size[0] <= object['location'][0] <= WIN_LENGTH - size_coefficient * size[0] or \
            not size_coefficient * size[1] <= object['location'][1] <= WIN_HEIGHT - size_coefficient * size[1]

"""
    Returns the top left point (as a list) of a surface according to a center point
"""
def get_top_left(surface, center):
    return list(surface.get_rect(center = center).topleft)


"""
    Handles the collisions of the spaceship, shots and hazards. 
    If a hazard hits the spaceship, it gets removed and the player is hit (handled in the main loop)
    If a shot hits an hazard, both get removed
"""
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

"""
    Draws the objects of the game on screen
"""
def draw(objects, score, life, font):
    WIN.fill(BACKGROUND_COLOR)
    for object in objects:
        WIN.blit(object['surface'], get_top_left(object['surface'], object['location']))
        
    score_text = font.render("Score: " + str(score) + " "*(3-len(str(score))), 1, LIGHT_BLUE)
    life_text = font.render("Life: " + str(life) + " "*(len(str(STARTING_LIFE))-len(str(life))), 1, GREEN)

    WIN.blit(score_text, (0,0))
    WIN.blit(life_text, (WIN_LENGTH - life_text.get_size()[0], 0))
    pygame.display.update()

"""
    Converts angle to direction
"""
def angle_to_direction(angle):
    return [math.cos(math.radians(angle)), math.sin(math.radians(angle))]

"""
    Returns the y value for an x on a line defined by two points
"""
def point_in_line(start_p, end_p, x):
    return ((end_p[1] - start_p[1]) / (end_p[0] - start_p[0])) * (x - start_p[0]) + start_p[1]

"""
    Creates a random polygon
"""
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

"""
    Creates a new hazard in a random edge location
"""
def new_hazard(spaceship_location):
    side = random.randint(1, 4)
    hazard = create_polygon(MAX_HAZARD_POINTS, MIN_HAZARD_WIDTH, MAX_HAZARD_WIDTH, MIN_HAZARD_HEIGHT, MAX_HAZARD_HEIGHT, RED)
    size = hazard.get_size()
    match side:
        case 1:
            x = -size[0] / 2
            y = random.uniform(0, WIN_HEIGHT)
        case 2:
            x = random.uniform(0, WIN_LENGTH)
            y = WIN_HEIGHT + size[1] / 2
        case 3:
            x = WIN_LENGTH + size[0] / 2
            y = random.uniform(0, WIN_HEIGHT)
        case 4:
            x = random.uniform(0, WIN_LENGTH)
            y = -size[1] / 2

    direction = [(spaceship_location[0] - x) / WIN_LENGTH, (spaceship_location[1] - y) / WIN_HEIGHT]
    return {'location': [x,y], 'surface': hazard.copy(), 'orig_surface': hazard, 'angle': 0, 'direction': direction}

"""
    Creates a shot that comes out of the spaceship
"""
def new_shot(spaceship):
    direction = angle_to_direction(spaceship['angle'])
    shot = pygame.Surface((SHOT_RADIUS*2, SHOT_RADIUS*2))
    shot.fill(BACKGROUND_COLOR)
    shot.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(shot, WHITE, (SHOT_RADIUS, SHOT_RADIUS), SHOT_RADIUS)

    mult = (SPACESHIP_SIZE[1] / 2 - SHOT_RADIUS) / math.sqrt(direction[0]**2 + direction[1]**2)
    return {'location': [spaceship['location'][i] + direction[i] * mult for i in range(2)], 'surface': shot, 'direction': direction}

"""
    Runs the game, returns whether the game ended with a quit command
"""
def game():
    font = pygame.font.SysFont("monospace", 50)
    clock = pygame.time.Clock()
    fps = DEFAULT_FPS
    shots = []
    hazards = []
    life = STARTING_LIFE
    score = 0
    spaceship = {'surface': SPACESHIP_IMAGE.copy(), 'location': list(CENTER), 'angle': 0}
    
    to_quit = False
    while life and not to_quit:
        if random.random() <= HAZARD_CHANCE:
            hazards.append(new_hazard(spaceship['location']))
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                to_quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shots.append(new_shot(spaceship))

        handle_movement(shots, SHOT_SPEED)
        handle_movement(hazards, HAZARD_SPEED, rotate=True)
        shots_before = len(shots)
        if handle_collisions(spaceship, shots, hazards):
            life -= 1
        score += shots_before - len(shots)
        keys = pygame.key.get_pressed()
        if bool(keys[pygame.K_LEFT]) != bool(keys[pygame.K_RIGHT]):
                orig_angle = spaceship['angle']
                spaceship['angle'] = (spaceship['angle'] + (-1 if keys[pygame.K_LEFT] else 1) * SPACESHIP_SPEED) % 360
                spaceship['surface'] = pygame.transform.rotate(SPACESHIP_IMAGE, -spaceship['angle'])
                if is_object_out_of_screen(spaceship, 0.5):
                    spaceship['angle'] = orig_angle
                spaceship['surface'] = pygame.transform.rotate(SPACESHIP_IMAGE, -spaceship['angle'])
        
        orig_loc = spaceship['location'][:]
        if keys[pygame.K_UP]:
            handle_movement([spaceship], SPACESHIP_SPEED)
            if is_object_out_of_screen(spaceship, 0.5):
                spaceship['location'] = orig_loc
        if keys[pygame.K_DOWN]:
            handle_movement([spaceship], -SPACESHIP_SPEED)
            if is_object_out_of_screen(spaceship, 0.5):
                spaceship['location'] = orig_loc

        if keys[pygame.K_LEFTBRACKET]:
            fps -= 1
        if keys[pygame.K_RIGHTBRACKET]:
            fps += 1

        draw([spaceship, *shots, *hazards], score, life, font)
    
    return to_quit

"""
    Main function, calls the game and allows restarting
"""
def main():
    pygame.init()
    start = True
    to_quit = False
    while not to_quit:
        if start:
            to_quit = game()
            start = False
            if not to_quit:
                font = pygame.font.SysFont('monospace', 50, bold=True)
                lost_text = font.render('GAME OVER!', 1, YELLOW)
                font = pygame.font.SysFont('monospace', 30, bold=True)
                instructions = font.render('Press Space to restart, q to quit', 1, YELLOW)

                WIN.blit(lost_text, get_top_left(lost_text, CENTER))
                WIN.blit(instructions, get_top_left(instructions, (CENTER[0] - instructions.get_size()[1] / 2, CENTER[1] + 50)))
                pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                to_quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True
                if event.key == pygame.K_q:
                    to_quit = True

    pygame.quit()

if __name__ == '__main__':
    main()