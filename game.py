import pygame
import math
import random
import os
pygame.init()

INFO = pygame.display.Info()
WIN_WIDTH = INFO.current_w
WIN_HEIGHT = INFO.current_h

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
CENTER = (WIN_WIDTH / 2, WIN_HEIGHT / 2)
DEFAULT_FPS = 60

EDGES = (-1, 1, 2, -2)
LEFT, RIGHT, TOP, BOTTOM = EDGES

SPACESHIP_TYPE = 0
SPACESHIP_HEIGHT = WIN_HEIGHT * (17/135)
SPACESHIP_IMAGE_PATH = 'assets\\spaceship.png'
SPACESHIP_MAX_SPEED = WIN_HEIGHT / 200
SPACESHIP_SPEED_INCREMENTS = SPACESHIP_MAX_SPEED / 50
SPACESHIP_MAX_ROTATE_SPEED = WIN_HEIGHT / 350
SPACESHIP_ROTATE_SPEED_INCREMENTS = SPACESHIP_MAX_ROTATE_SPEED / 50

SHOT_TYPE = 1
SHOT_RADIUS = WIN_HEIGHT / 108
SHOT_SPEED = SPACESHIP_MAX_SPEED * 1.25
SHOT_COLOR = (255, 255, 255)

STARTING_LIFE = 5
STARTING_AMMO = 10

POWERUP_TYPE = 2
POWERUP_SPEED = SPACESHIP_MAX_SPEED * 0.9

AMMO_POWERUP_POWER = 0
AMMO_POWERUP_CHANCE = 0.003
AMMO_POWERUP_TO_ADD = 10
AMMO_POWERUP_RADIUS = SHOT_RADIUS * 1.5
AMMO_POWERUP_COLOR = (30, 50, 255)

HEAL_POWERUP_POWER = 1
HEAL_POWERUP_CHANCE = 0.001
HEAL_POWERUP_TO_ADD = 1
HEAL_POWERUP_RADIUS = SHOT_RADIUS
HEAL_POWERUP_COLOR = (0, 255, 0)

SHOOT_POWERUP_POWER = 2
SHOOT_POWERUP_CHANCE = 0.0005
SHOOT_POWERUP_NUM_OF_SHOTS = 16
SHOOT_POWERUP_RADIUS = SHOT_RADIUS * 0.7
SHOOT_POWERUP_COLOR = (255,223,0)

HAZARD_TYPE = 3
BASE_HAZARD_CHANCE = 0.05
HAZARD_SPEED = SPACESHIP_MAX_SPEED * 0.75

MIN_HAZARD_WIDTH = WIN_HEIGHT / 10
MAX_HAZARD_WIDTH = WIN_HEIGHT / 3
MIN_HAZARD_HEIGHT = WIN_HEIGHT / 10
MAX_HAZARD_HEIGHT = WIN_HEIGHT / 3
MAX_HAZARD_POINTS = 9
HAZARD_BORDER = 2
MAX_ROTATE_SPEED = 1
HAZARD_FILL_COLOR = (150, 0, 0)
HAZARD_BORDER_COLOR = (205, 127, 50)

SPACESHIP_HIT_EVENT = pygame.USEREVENT + 0
HAZARD_SHOT_EVENT = pygame.USEREVENT + 1
POWERUP_COLLECTED_EVENT = pygame.USEREVENT + 2
OBJECT_OUT_OF_SCREEN_EVENT = pygame.USEREVENT + 3
BACKGROUND_COLOR = (20, 20, 20)

GAME_OVER_TEXT_COLOR = (235, 163, 70)
FONT = 'Times New Roman'
SCORE_TEXT_COLOR = (144, 213, 255)
AMMO_TEXT_COLOR = (200,200,200)
GAME_FONT_SIZE = int(WIN_HEIGHT / 15)
GAME_OVER_FONT_SIZE = int(WIN_HEIGHT / 8)

HEART_RADIUS = WIN_HEIGHT / 108
HEART_COLOR = (255, 0, 0)
HEART = pygame.surface.Surface((HEART_RADIUS * 2, HEART_RADIUS * 2))
HEART.fill(BACKGROUND_COLOR)
HEART.set_colorkey(BACKGROUND_COLOR)
pygame.draw.circle(HEART, HEART_COLOR, (HEART_RADIUS / 2, HEART_RADIUS / 2), HEART_RADIUS / 2, draw_top_left=True, draw_top_right=True)
pygame.draw.circle(HEART, HEART_COLOR, (HEART_RADIUS * 1.5, HEART_RADIUS / 2), HEART_RADIUS / 2, draw_top_left=True, draw_top_right=True)
pygame.draw.polygon(HEART, HEART_COLOR, ((0, HEART_RADIUS / 2), (HEART_RADIUS, HEART_RADIUS * 2), (HEART_RADIUS * 2, HEART_RADIUS / 2)))

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

def mult_direction(direction, mult):
    """
        Multiplies direction vector by a multiplier, such that the distance is the original distance times the multiplier
    """
    return [c * math.sqrt(abs(mult)) * (1 if mult >= 0 else -1) for c in direction]

def handle_movement(objects_lists):
    """
        Handles movement of multiple object. 
        Raises event for objects that go out of the screen.
    """
    for to_move in objects_lists:
        for obj in to_move:
            dir = obj['direction']
            obj['location'][0] += dir[0]
            obj['location'][1] += dir[1]

            if 'rotate' in obj and obj['rotate'] != 0:
                obj['angle'] = (obj['angle'] + obj['rotate']) % 360
                obj['surface'] = pygame.transform.rotate(obj['orig_surface'], obj['angle'])

            if is_object_out_of_screen(obj, 1):
                pygame.event.post(pygame.event.Event(OBJECT_OUT_OF_SCREEN_EVENT, object=obj))

def handle_keyboard_input_movement_normal(spaceship, keys):
    """
        Handles keyboard movement input:
        Up: move ship forwards
        Down: move ship backwards
        Right: rotate ship clockwise
        Left: rotate ship counter clockwise
        If up and down aren't pressed, ship stops.
        If right and left aren't pressed, ship doesn't rotate.
    """
    if bool(keys[pygame.K_LEFT]) != bool(keys[pygame.K_RIGHT]):
        spaceship['rotate'] = (1 if keys[pygame.K_LEFT] else -1) * SPACESHIP_MAX_ROTATE_SPEED
    else:
        spaceship['rotate'] = 0

    if bool(keys[pygame.K_UP]) != bool(keys[pygame.K_DOWN]):
        spaceship['direction'] = mult_direction(angle_to_direction(-spaceship['angle']), SPACESHIP_MAX_SPEED * (1 if keys[pygame.K_UP] else -1))
    else:
        spaceship['direction'] = [0, 0]
    speed = math.sqrt(sum([c ** 2 for c in spaceship['direction']]))

    if(speed > SPACESHIP_MAX_SPEED):
        spaceship['direction'][0] *= SPACESHIP_MAX_SPEED / speed
        spaceship['direction'][1] *= SPACESHIP_MAX_SPEED / speed

def handle_keyboard_input_movement_physics(spaceship, keys):
    """
        Handles keyboard movement input:
        Up: accelerates forwards
        Down: accelerates backwards
        Right: accelerates rotation clockwise
        Left: accelerates rotation counter clockwise
    """                
    if bool(keys[pygame.K_LEFT]) != bool(keys[pygame.K_RIGHT]):
        if keys[pygame.K_LEFT]:
            spaceship['rotate'] = min(spaceship['rotate'] + SPACESHIP_SPEED_INCREMENTS, SPACESHIP_MAX_ROTATE_SPEED)
        else:
            spaceship['rotate'] = max(spaceship['rotate'] - SPACESHIP_SPEED_INCREMENTS, -SPACESHIP_MAX_ROTATE_SPEED)

    if bool(keys[pygame.K_UP]) != bool(keys[pygame.K_DOWN]):
        direction = angle_to_direction(-spaceship['angle'])
        to_add = mult_direction(direction, SPACESHIP_SPEED_INCREMENTS * (1 if keys[pygame.K_UP] else -1))
        spaceship['direction'][0] += to_add[0]
        spaceship['direction'][1] += to_add[1]

        speed = sum([c ** 2 for c in spaceship['direction']])

        if(speed > SPACESHIP_MAX_SPEED):
           spaceship['direction'][0] *= SPACESHIP_MAX_SPEED / speed
           spaceship['direction'][1] *= SPACESHIP_MAX_SPEED / speed

def is_object_out_of_screen(obj, percentage):
    """
        Returns whether an object is out of the screen by percentage 
        percentage=1 means the object need to be fully out of screen, 
        percentage=0 means that the object need to be just touching out of screen
    """
    size = obj['surface'].get_size()
    size_coefficient = 0.5 - percentage
    return not size_coefficient * size[0] <= obj['location'][0] <= WIN_WIDTH - size_coefficient * size[0] or \
            not size_coefficient * size[1] <= obj['location'][1] <= WIN_HEIGHT - size_coefficient * size[1]

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
    for obj in objects:
        WIN.blit(obj['surface'], get_top_left(obj['surface'], obj['location']))
    
    for i in range(life):
        WIN.blit(HEART, (WIN_WIDTH - HEART_RADIUS * 3 * (i+1), HEART_RADIUS * 1.5))

    score_text = font.render("Score: " + str(score) + " "*(3-len(str(score))), 1, SCORE_TEXT_COLOR)
    ammo_text = font.render("Ammo: " + str(ammo) + " "*(len(str(STARTING_AMMO))-len(str(ammo))), 1, AMMO_TEXT_COLOR)
    
    WIN.blit(score_text, (0,0))
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
        edge = random.choice(EDGES)

    if edge == LEFT:
        x = -size[0] / 2
        y = random.uniform(0, WIN_HEIGHT)
    elif edge == TOP:
        x = random.uniform(0, WIN_WIDTH)
        y = WIN_HEIGHT + size[1] / 2
    elif edge == RIGHT:
        x = WIN_WIDTH + size[0] / 2
        y = random.uniform(0, WIN_HEIGHT)
    elif edge == BOTTOM:
        x = random.uniform(0, WIN_WIDTH)
        y = -size[1] / 2

    return [x,y], edge

def new_hazard(spaceship_location):
    """
        Creates a new hazard in a random edge location
    """
    hazard = create_polygon(MAX_HAZARD_POINTS, MIN_HAZARD_WIDTH, MAX_HAZARD_WIDTH, MIN_HAZARD_HEIGHT, MAX_HAZARD_HEIGHT, HAZARD_FILL_COLOR, HAZARD_BORDER, HAZARD_BORDER_COLOR)

    loc = random_edge_point(hazard.get_size())[0]

    direction = direction_between_points(loc, spaceship_location)
    return {'type': HAZARD_TYPE, 'surface': hazard.copy(), 'orig_surface': hazard, 'location': loc, 'direction': mult_direction(direction, HAZARD_SPEED), 
            'angle': 0, 'rotate': random.randint(1, MAX_ROTATE_SPEED) * random.choice([-1, 1])}

def new_shot(spaceship, added_angle = 0):
    """
        Creates a shot that comes out of the spaceship
    """
    shot = pygame.Surface((SHOT_RADIUS*2, SHOT_RADIUS*2))
    shot.fill(BACKGROUND_COLOR)
    shot.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(shot, SHOT_COLOR, (SHOT_RADIUS, SHOT_RADIUS), SHOT_RADIUS)

    direction = angle_to_direction(-spaceship['angle'] + added_angle)
    mult = spaceship['orig_surface'].get_width() / 2 - SHOT_RADIUS
    loc = [spaceship['location'][i] + direction[i] * mult for i in range(2)]
    return {'type': SHOT_TYPE, 'surface': shot, 'location': loc, 'direction': mult_direction(direction, SHOT_SPEED)}

def new_powerup(power, radius, color):
    """
        Creates a new powerup that starts from one of the edges
    """
    powerup = pygame.Surface((radius*2, radius*2))
    powerup.fill(BACKGROUND_COLOR)
    powerup.set_colorkey(BACKGROUND_COLOR)
    pygame.draw.circle(powerup, color, (radius, radius), radius)

    loc, edge = random_edge_point(powerup.get_size())
    direction = direction_between_points(loc, random_edge_point(edge=-edge)[0])
    return {'type': POWERUP_TYPE, 'surface': powerup, 'location': loc, 'direction': mult_direction(direction, POWERUP_SPEED), 'power': power}

def game(physics_enabled=False):
    """
        Runs the game, returns whether the game ended with a quit command
    """
    font = pygame.font.SysFont(FONT, 50)
    clock = pygame.time.Clock()
    fps = DEFAULT_FPS
    shots = []
    hazards = []
    powerups = []
    life = STARTING_LIFE
    ammo = STARTING_AMMO
    score = 0
    angle = random.randint(0,360)
    spaceship_image = pygame.image.load(SPACESHIP_IMAGE_PATH)
    spaceship_image = pygame.transform.scale(spaceship_image, 
                                             ((spaceship_image.get_width() / spaceship_image.get_height()) * SPACESHIP_HEIGHT, SPACESHIP_HEIGHT))
    spaceship = {'type': SPACESHIP_TYPE, 'orig_surface': spaceship_image, 'surface': pygame.transform.rotate(spaceship_image, angle), 
                 'location': list(CENTER), 'direction': [0,0], 'angle': angle, 'rotate': 0}
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
                    if ammo > 0 or invincible:
                        shots.append(new_shot(spaceship))
                        if not invincible:
                            ammo -= 1
                if event.key == pygame.K_RETURN:
                    pause = not pause
                if event.key == pygame.K_p:
                    physics_enabled = not physics_enabled
                if event.key == pygame.K_i:
                    invincible = not invincible
                if event.key == pygame.K_ESCAPE:
                    to_quit = True
                if event.key == pygame.K_BACKSLASH:
                    fps = DEFAULT_FPS

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

                if event.powerup['power'] == AMMO_POWERUP_POWER:
                    ammo += AMMO_POWERUP_TO_ADD

                elif event.powerup['power'] == HEAL_POWERUP_POWER:
                    life += HEAL_POWERUP_TO_ADD
                    
                elif event.powerup['power'] == SHOOT_POWERUP_POWER:
                    for i in range(SHOOT_POWERUP_NUM_OF_SHOTS):
                        shots.append(new_shot(spaceship, i * 360 / SHOOT_POWERUP_NUM_OF_SHOTS))

                powerups.remove(event.powerup)

            elif event.type == OBJECT_OUT_OF_SCREEN_EVENT:
                obj = event.object
                if obj['type'] == SHOT_TYPE:
                    shots.remove(obj)
                elif obj['type'] == HAZARD_TYPE:
                    hazards.remove(obj)
                elif obj['type'] == POWERUP_TYPE:
                    powerups.remove(obj)

        if pause:
            continue

        keys = pygame.key.get_pressed()
        if not physics_enabled:
            handle_keyboard_input_movement_normal(spaceship, keys)
        else:
            handle_keyboard_input_movement_physics(spaceship, keys)

        if keys[pygame.K_RIGHTBRACKET]:
            fps += 1
        if keys[pygame.K_LEFTBRACKET] and fps > 0:
            fps -= 1

        if random.random() <= BASE_HAZARD_CHANCE / (len(hazards)/4+1):
            hazards.append(new_hazard(spaceship['location']))

        if random.random() <= AMMO_POWERUP_CHANCE:
            powerups.append(new_powerup(AMMO_POWERUP_POWER, AMMO_POWERUP_RADIUS, AMMO_POWERUP_COLOR))

        if life < STARTING_LIFE and random.random() <= HEAL_POWERUP_CHANCE:
            powerups.append(new_powerup(HEAL_POWERUP_POWER, HEAL_POWERUP_RADIUS, HEAL_POWERUP_COLOR))
            
        if random.random() <= SHOOT_POWERUP_CHANCE:
            powerups.append(new_powerup(SHOOT_POWERUP_POWER, SHOOT_POWERUP_RADIUS, SHOOT_POWERUP_COLOR))

        orig_spaceship_loc = spaceship['location'][:]
        handle_movement([[spaceship], shots, hazards, powerups])
        if is_object_out_of_screen(spaceship, 0.5):
            spaceship['location'] = orig_spaceship_loc
            spaceship['direction'] = mult_direction(spaceship['direction'], -1)
            spaceship['rotate'] *= -1

        handle_collisions(spaceship, shots, hazards, powerups)
        draw([*shots, spaceship, *hazards, *powerups], score, life, ammo, font)
    return to_quit

def main():
    """
        Main function, calls the game and allows restarting
    """
    pygame.init()
    start = True
    to_quit = False
    physics_enabled = False
    while not to_quit:
        if start:
            to_quit = game(physics_enabled)
            start = False
            if not to_quit:
                font = pygame.font.SysFont(FONT, GAME_OVER_FONT_SIZE, bold=True)
                lost_text = font.render('GAME OVER!', 1, GAME_OVER_TEXT_COLOR)
                font = pygame.font.SysFont(FONT, GAME_OVER_FONT_SIZE//2, bold=True)
                instructions = font.render('Press Enter to restart, Escape to quit', 1, GAME_OVER_TEXT_COLOR)
                physics_description = font.render('Press p to toggle physics mode', 1, GAME_OVER_TEXT_COLOR)
                WIN.blit(lost_text, get_top_left(lost_text, CENTER))
                WIN.blit(instructions, get_top_left(instructions, (CENTER[0] - instructions.get_size()[1] / 2, CENTER[1] + GAME_OVER_FONT_SIZE)))
                WIN.blit(physics_description, get_top_left(physics_description, (CENTER[0] - physics_description.get_size()[1] / 2, CENTER[1] + GAME_OVER_FONT_SIZE * 1.5)))
                pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                to_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start = True
                if event.key == pygame.K_ESCAPE:
                    to_quit = True
                if event.key == pygame.K_p:
                    physics_enabled = not physics_enabled

    pygame.quit()

if __name__ == '__main__':
    main()