import pygame
import math
import random
import os

LEFT, TOP, RIGHT, BOTTOM = tuple(range(4))

SPACESHIP_SIZE = (136, 160)

SHOT_RADIUS = 10
SHOT_SPEED = 5

SPACESHIP_SPEED = 4
STARTING_LIFE = 3
STARTING_AMMO = 10

POWERUP_SPEED = 5

AMMO_POWERUP_CHANCE = 0.005
AMMO_POWERUP_RADIUS = 15

HAZARD_CHANCE = 0.03
HAZARD_SPEED = 3

MIN_HAZARD_WIDTH = 100
MAX_HAZARD_WIDTH = 300
MIN_HAZARD_HEIGHT = 100
MAX_HAZARD_HEIGHT = 300
MAX_HAZARD_POINTS = 9
HAZARD_BORDER = 2

WIN_LENGTH = 1600
WIN_HEIGHT = 800

CENTER = (WIN_LENGTH / 2, WIN_HEIGHT / 2)

SPACESHIP_HIT_EVENT = pygame.USEREVENT + 0
HAZARD_SHOT_EVENT = pygame.USEREVENT + 1
POWERUP_COLLECTED_EVENT = pygame.USEREVENT + 2

WIN = pygame.display.set_mode((WIN_LENGTH, WIN_HEIGHT))
SPACESHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'spaceship.png')), SPACESHIP_SIZE)

DEFAULT_FPS = 60

BACKGROUND_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (205, 127, 50)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (144, 213, 255)
BLUE = (30, 50, 255)

def direction_between_points(src, dest):
    """
        Returns the direction from src to dest, normalized
    """
    direction = [dest[0]-src[0], dest[1]-src[1]]
    distance = math.sqrt(direction[0]**2 + direction[1]**2)
    return [direction[0]/distance, direction[1]/distance]

def rotate_point(p, around_p, angle):
    """
        Rotate a point around another by angle
    """
    s = math.sin(math.radians(angle))
    c = math.cos(math.radians(angle))

    p = list(p)
    p[0] -= around_p[0]
    p[1] -= around_p[1]

    x = p[0] * c - p[1] * s
    y = p[0] * s + p[1] * c
    new = [around_p[0] + x, around_p[1] + y]
    return new

def handle_movement(to_move, speed, rotate=False):
    """
        Handles movement of multiple object. 
        If remove is true, removes objects that go out of the screen.
    """
    to_remove = []
    for object in to_move:
        dir = object['direction'] if 'direction' in object else angle_to_direction(object['angle'])
        object['location'][0] += dir[0] * speed
        object['location'][1] += dir[1] * speed

        if rotate:
            object['angle'] = (object['angle'] + 1) % 360
            object['surface'] = pygame.transform.rotate(object['orig_surface'], object['angle'])

        if is_object_out_of_screen(object, 1):
            to_remove.append(object)

    for object in to_remove:
        to_move.remove(object)

def is_object_out_of_screen(object, percentage):
    """
        Returns whether an object is out of the screen by percentage 
        percentage=1 means the object need to be fully out of screen, 
        percentage=0 means that the object need to be just touching out of screen
    """
    size = object['surface'].get_size()
    size_coefficient = 0.5 - percentage
    return not size_coefficient * size[0] <= object['location'][0] <= WIN_LENGTH - size_coefficient * size[0] or \
            not size_coefficient * size[1] <= object['location'][1] <= WIN_HEIGHT - size_coefficient * size[1]

def get_top_left(surface, center):
    """
        Returns the top left point (as a list) of a surface according to a center point
    """
    return list(surface.get_rect(center = center).topleft)

def handle_collisions(spaceship, shots, hazards, powerups):
    """
        Handles the collisions of the spaceship, shots, hazards and powerups. 
        Raises events for collisions between spaceship and hazards, shots and hazards, and spaceship and powerups
    """
    spaceship_mask = pygame.mask.from_surface(spaceship['surface'])
    spaceship_top_left = get_top_left(spaceship['surface'], spaceship['location'])
    for hazard in hazards:
        hazard_mask = pygame.mask.from_surface(hazard['surface'])
        hazard_top_left = get_top_left(hazard['surface'], hazard['location'])
        if spaceship_mask.overlap(hazard_mask, (hazard_top_left[0] - spaceship_top_left[0], hazard_top_left[1] - spaceship_top_left[1])):
            pygame.event.post(pygame.event.Event(SPACESHIP_HIT_EVENT, hazard=hazard))
            continue

        for shot in shots:
            shot_mask = pygame.mask.from_surface(shot['surface'])
            shot_top_left = get_top_left(shot['surface'], shot['location'])
            if shot_mask.overlap(hazard_mask, (hazard_top_left[0] - shot_top_left[0], hazard_top_left[1] - shot_top_left[1])):
                pygame.event.post(pygame.event.Event(HAZARD_SHOT_EVENT, hazard=hazard, shot=shot))
                break
    
    for powerup in powerups:
        powerup_mask = pygame.mask.from_surface(powerup['surface'])
        powerup_top_left = get_top_left(powerup['surface'], powerup['location'])
        if powerup_mask.overlap(spaceship_mask, (spaceship_top_left[0] - powerup_top_left[0], spaceship_top_left[1] - powerup_top_left[1])):
            pygame.event.post(pygame.event.Event(POWERUP_COLLECTED_EVENT, powerup=powerup))

def draw(objects, score, life, ammo, font):
    """
        Draws the objects of the game on screen
    """
    WIN.fill(BACKGROUND_COLOR)
    for object in objects:
        WIN.blit(object['surface'], get_top_left(object['surface'], object['location']))
    
    score_text = font.render("Score: " + str(score) + " "*(3-len(str(score))), 1, LIGHT_BLUE)
    life_text = font.render("Life: " + str(life) + " "*(len(str(STARTING_LIFE))-len(str(life))), 1, GREEN)
    ammo_text = font.render("Ammo: " + str(ammo) + " "*(len(str(STARTING_AMMO))-len(str(ammo))), 1, WHITE)
    
    WIN.blit(score_text, (0,0))
    WIN.blit(life_text, (WIN_LENGTH - life_text.get_size()[0], 0))
    WIN.blit(ammo_text, (0,WIN_HEIGHT - ammo_text.get_size()[1]))
    pygame.display.update()

def angle_to_direction(angle):
    """
        Converts angle to direction
    """
    return [math.cos(math.radians(angle)), math.sin(math.radians(angle))]

def point_in_line(start_p, end_p, x):
    """
        Returns the y value for an x on a line defined by two points
    """
    return ((end_p[1] - start_p[1]) / (end_p[0] - start_p[0])) * (x - start_p[0]) + start_p[1]

def create_polygon(max_points, min_width, max_width, min_height, max_height, color, border_width=0, border_color=(0,0,0)):
    """
        Creates a random polygon
    """
    #chooses number of points for the polygon - from 3 (triangle) to max points)
    num_points = random.randint(3, max_points)
    
    #chooses height and width of the surrounding the polygon surrounding rectangle
    height = random.uniform(min_height, max_height)
    width = random.uniform(min_width, max_width)

    #chooses how many top points and bottom points there will be (in addition to the left most and right most points, which don't count)
    num_top_points = random.randint(0, num_points - 2)
    num_bottom_points = num_points - num_top_points - 2

    #chooses the highest and lowest points
    highest = random.randint(0, num_top_points + 1)
    lowest = random.randint(1 if highest == 0 else 0, num_bottom_points + (0 if highest == num_top_points + 1 else 1))

    #choose the left most point
    if highest == 0:
        left_p_y = 0
    elif lowest == 0:
        left_p_y = height
    else:
        left_p_y = random.uniform(0, height)
    left_p = (0, left_p_y)

    #choose the right most point
    if highest == num_top_points + 1:
        right_p_y = 0
    elif lowest == num_bottom_points + 1:
        right_p_y = height
    else:
        right_p_y = random.uniform(0, height)
    right_p = (width, right_p_y)

    distance = min(height, width) / num_points

    #chooses top points: makes sure that no point passes the line between the left most and right most points
    top_points = [left_p]
    for i in range(num_top_points):
        point_x = random.uniform(top_points[-1][0] + distance, right_p[0] - distance * (num_top_points - i + 1))
        if i + 1 == highest:
            point_y = 0
        else:
            max_y = point_in_line(left_p, right_p, point_x)
            max_y = max(0, max_y - distance)
            point_y = random.uniform(0, max_y)
        top_points += [(point_x, point_y)]
    top_points += [right_p]

    #chooses bottom points: makes sure that no point passes the line between the left most and right most points
    bottom_points = [left_p]
    for i in range(num_bottom_points):
        point_x = random.uniform(bottom_points[-1][0] + distance, right_p[0] - distance * (num_bottom_points - i + 1))
        if i + 1 == lowest:
            point_y = height
        else:
            min_y = point_in_line(left_p, right_p, point_x)
            min_y = min(min_y + distance, height)
            point_y = random.uniform(min_y, height)
        bottom_points += [(point_x, point_y)]
    
    #points are all the top followed by the bottoms (bottoms are reversed so they will be sorted right to left)
    points = top_points + bottom_points[::-1]
    polygon = pygame.Surface((width + border_width * 2, height + border_width * 2))
    polygon.fill(BACKGROUND_COLOR)
    polygon.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.polygon(polygon, color, points)
    if border_width > 0:
        pygame.draw.polygon(polygon, border_color, points, border_width)
    return polygon

def random_edge_point(size=(0,0), edge=None):
    """
        Randomizes an edge point
    """
    if not edge:
        edge = random.randint(0, 3)

    if edge == LEFT:
        x = -size[0] / 2
        y = random.uniform(0, WIN_HEIGHT)
    elif edge == TOP:
        x = random.uniform(0, WIN_LENGTH)
        y = WIN_HEIGHT + size[1] / 2
    elif edge == RIGHT:
        x = WIN_LENGTH + size[0] / 2
        y = random.uniform(0, WIN_HEIGHT)
    elif edge == BOTTOM:
        x = random.uniform(0, WIN_LENGTH)
        y = -size[1] / 2

    return [x,y], edge

def new_hazard(spaceship_location):
    """
        Creates a new hazard in a random edge location
    """
    hazard = create_polygon(MAX_HAZARD_POINTS, MIN_HAZARD_WIDTH, MAX_HAZARD_WIDTH, MIN_HAZARD_HEIGHT, MAX_HAZARD_HEIGHT, RED, HAZARD_BORDER, ORANGE)
    angle = random.randint(0, 360)
    hazard = pygame.transform.rotate(hazard, angle)

    loc = random_edge_point(hazard.get_size())[0]

    direction = direction_between_points(loc, spaceship_location)
    return {'location': loc, 'surface': hazard.copy(), 'orig_surface': hazard, 'angle': angle, 'direction': direction}

def new_shot(spaceship):
    """
        Creates a shot that comes out of the spaceship
    """
    shot = pygame.Surface((SHOT_RADIUS*2, SHOT_RADIUS*2))
    shot.fill(BACKGROUND_COLOR)
    shot.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(shot, WHITE, (SHOT_RADIUS, SHOT_RADIUS), SHOT_RADIUS)

    direction = angle_to_direction(spaceship['angle'])
    mult = SPACESHIP_SIZE[1] / 2 - SHOT_RADIUS
    loc = [spaceship['location'][i] + direction[i] * mult for i in range(2)]
    return {'location': loc, 'surface': shot, 'direction': direction}

def new_powerup(type, radius):
    """
        Creates a new powerup that starts from one of the edges
    """
    powerup = pygame.Surface((radius*2, radius*2))
    powerup.fill(BACKGROUND_COLOR)
    powerup.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(powerup, BLUE, (radius, radius), radius)

    loc, edge = random_edge_point(powerup.get_size())
    direction = direction_between_points(loc, random_edge_point(edge=(edge+2)%4)[0])
    return {'location': loc, 'surface': powerup, 'direction': direction, 'type': type}

def game():
    """
        Runs the game, returns whether the game ended with a quit command
    """
    font = pygame.font.SysFont("monospace", 50)
    clock = pygame.time.Clock()
    fps = DEFAULT_FPS
    shots = []
    hazards = []
    powerups = []
    life = STARTING_LIFE
    ammo = STARTING_AMMO
    score = 0
    spaceship = {'surface': SPACESHIP_IMAGE.copy(), 'location': list(CENTER), 'angle': 0}
    pause = False
    invincible = False
    to_quit = False
    draw([spaceship, *shots, *hazards], score, life, ammo, font)

    while life and not to_quit:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                to_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not pause:
                    if ammo > 0:
                        shots.append(new_shot(spaceship))
                        ammo -= 1
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_i:
                    invincible = not invincible
            elif event.type == SPACESHIP_HIT_EVENT:
                if not invincible:
                    life -= 1
                if life:
                    hazards.remove(event.hazard)
            elif event.type == HAZARD_SHOT_EVENT:
                if event.hazard not in hazards or event.shot not in shots:
                    continue

                hazards.remove(event.hazard)
                shots.remove(event.shot)
                score += 1
            elif event.type == POWERUP_COLLECTED_EVENT:
                if event.powerup not in powerups:
                    continue

                if event.powerup['type'] == 'ammo':
                    ammo += 10
                powerups.remove(event.powerup)

        if pause:
            continue

        keys = pygame.key.get_pressed()
        if bool(keys[pygame.K_LEFT]) != bool(keys[pygame.K_RIGHT]):
            orig_angle = spaceship['angle']
            spaceship['angle'] = (spaceship['angle'] + (1 if keys[pygame.K_RIGHT] else -1) * SPACESHIP_SPEED) % 360
            spaceship['surface'] = pygame.transform.rotate(SPACESHIP_IMAGE, -spaceship['angle'])
            if is_object_out_of_screen(spaceship, 0.5):
                spaceship['angle'] = orig_angle

        if bool(keys[pygame.K_UP]) != bool(keys[pygame.K_DOWN]):
            orig_loc = spaceship['location'][:]
            handle_movement([spaceship], SPACESHIP_SPEED * (1 if keys[pygame.K_UP] else -1))
            if is_object_out_of_screen(spaceship, 0.5):
                spaceship['location'] = orig_loc

        if keys[pygame.K_LEFTBRACKET]:
            fps -= 1
        if keys[pygame.K_RIGHTBRACKET]:
            fps += 1

        if random.random() <= HAZARD_CHANCE:
            hazards.append(new_hazard(spaceship['location']))

        if random.random() <= AMMO_POWERUP_CHANCE:
            powerups.append(new_powerup('ammo', AMMO_POWERUP_RADIUS))

        handle_movement(shots, SHOT_SPEED)
        handle_movement(hazards, HAZARD_SPEED, rotate=True)
        handle_movement(powerups, POWERUP_SPEED)
        handle_collisions(spaceship, shots, hazards, powerups)
        draw([spaceship, *shots, *hazards, *powerups], score, life, ammo, font)

    return to_quit

def main():
    """
        Main function, calls the game and allows restarting
    """
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True
                if event.key == pygame.K_q:
                    to_quit = True

    pygame.quit()

if __name__ == '__main__':
    main()