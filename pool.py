import pygame
from pygame.math import Vector2
import sys
import math

# Table dimensions
WINDOWS_WIDTH, WINDOWS_HEIGHT = 500, 900
BORDER_WIDTH = 50
TABLE_WIDTH, TABLE_HEIGHT = WINDOWS_WIDTH - 2 * BORDER_WIDTH, WINDOWS_HEIGHT - 2 * BORDER_WIDTH

# Define ball properties
BALL_SIZE = 10
BALL_MASS = 1
FRICTION = 0.02
EDGE_FRICTION = 1
STANDARD_SPEED = 10
MAX_SPEED = 20

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
BROWN = (110, 40, 20)

# Define balls colors
NUM_BALLS = 15
POOL_BALL_COLORS = [
    YELLOW, BLUE, RED, PURPLE, ORANGE, GREEN, RED, BLACK,
    YELLOW, BLUE, RED, PURPLE, ORANGE, GREEN, RED
]

# Define hole 
HOLE_SIZE = 4 * BALL_SIZE
HOLE_COLOR = BLACK

hole_positions = [
    (BORDER_WIDTH, BORDER_WIDTH),
    (BORDER_WIDTH + TABLE_WIDTH, BORDER_WIDTH),
    (BORDER_WIDTH, BORDER_WIDTH + TABLE_HEIGHT),
    (BORDER_WIDTH + TABLE_WIDTH, BORDER_WIDTH + TABLE_HEIGHT),
    (BORDER_WIDTH, TABLE_HEIGHT // 2),
    (BORDER_WIDTH + TABLE_WIDTH, TABLE_HEIGHT // 2)
]
# Define cue 
cue_angle = 90
cue_length = 150
current_speed = STANDARD_SPEED

# Define Score
score = 0
TEXT_COLOR = WHITE

# Setup Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
pygame.display.set_caption('Pool')

# Initialize font
font = pygame.font.SysFont(None, 36)


# Function to calculate positions of balls in a triangular formation
def initial_ball_positions():
    positions = []
    rows = 5
    for row in range(rows):
        y = BORDER_WIDTH + 100 + (rows - row - 1) * BALL_SIZE * 2.5
        for col in range(row + 1):
            x = (2 * BORDER_WIDTH + TABLE_WIDTH) // 2 - (row / 2 - col) * BALL_SIZE * 2.5
            positions.append((x, y))
    return positions


# Function to handle ball collisions with walls 
def handle_wall_collisions(item):
    if item['position'].x <= BORDER_WIDTH + item['size']:
        item['direction'].x *= -1
        item['position'].x = BORDER_WIDTH + item['size']
        item['speed'] = max(0, item['speed'] - EDGE_FRICTION)

    elif item['position'].x >= BORDER_WIDTH + TABLE_WIDTH - item['size']:
        item['direction'].x *= -1
        item['position'].x = BORDER_WIDTH + TABLE_WIDTH - item['size']
        item['speed'] = max(0, item['speed'] - EDGE_FRICTION)

    if item['position'].y <= BORDER_WIDTH + item['size']:
        item['direction'].y *= -1
        item['position'].y = BORDER_WIDTH + item['size']
        item['speed'] = max(0, item['speed'] - EDGE_FRICTION)

    elif item['position'].y >= BORDER_WIDTH + TABLE_HEIGHT - item['size']:
        item['direction'].y *= -1
        item['position'].y = BORDER_WIDTH + TABLE_HEIGHT - item['size']
        item['speed'] = max(0, item['speed'] - EDGE_FRICTION)


# Function to handle collisions between balls
def handle_ball_collisions():
    for i, item1 in ball.items():
        if item1['potted']:
            continue  # Skip potted balls
        for j, item2 in ball.items():
            if i < j and not item2['potted']:
                pos_diff = item1['position'] - item2['position']
                distance = pos_diff.length()
                if distance < item1['size'] + item2['size']:  # Collision detected
                    normal = pos_diff.normalize()
                    v_rel = item1['direction'] * item1['speed'] - item2['direction'] * item2['speed']
                    v_rel_normal = v_rel.dot(normal)

                    if v_rel_normal <= 0:
                        impulse = (2 * v_rel_normal) / (item1['mass'] + item2['mass'])
                        item1['direction'] -= impulse * item2['mass'] * normal
                        item2['direction'] += impulse * item1['mass'] * normal

                        item1['speed'] = max(0, item1['direction'].length() - 2 * FRICTION)
                        item2['speed'] = max(0, item2['direction'].length() - 2 * FRICTION)
                        item1['direction'].normalize_ip()
                        item2['direction'].normalize_ip()


# Function to update the ball positions
def update_positions():
    global running, score

    for item in ball.values():
        if not item['potted']:
            item['position'] += item['direction'] * item['speed']  # Move ball
            item['speed'] = max(0, item['speed'] - FRICTION)  # Slow down ball for friction

            handle_wall_collisions(item)
            check_ball_in_hole(item)


# Function to check for balls in hole
def check_ball_in_hole(item):
    global running, score
    for hole_pos in hole_positions:
        if (item['position'] - Vector2(hole_pos)).length() <= HOLE_SIZE / 2:
            item['potted'] = True
            item['speed'] = 0
            score += 1

            # If the white ball is potted, quit the game
            if item['color'] == WHITE:
                running = False
            break


# Function to calculate the angle of the cue based on the mouse position
def calculate_cue_angle(mouse_pos):
    white_ball_pos = ball[NUM_BALLS - 1]['position']
    delta_x = mouse_pos[0] - white_ball_pos.x
    delta_y = mouse_pos[1] - white_ball_pos.y
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return angle


# Function to draw holes on the table
def draw_holes():
    for pos in hole_positions:
        pygame.draw.circle(screen, HOLE_COLOR, pos, HOLE_SIZE // 2)


# Draw the game table
def draw_game_table():
    # Draw the table
    screen.fill(BROWN)
    pygame.draw.rect(screen, DARK_GREEN, (BORDER_WIDTH, BORDER_WIDTH, TABLE_WIDTH, TABLE_HEIGHT))
    draw_holes()

    # Draw the score
    score_text = font.render(f"{score}", True, TEXT_COLOR)
    screen.blit(score_text, ((TABLE_WIDTH + 2 * BORDER_WIDTH) // 2, 10))  # Draw score in the top left corner

    # Draw all balls
    for item in ball.values():
        if not item['potted']:
            pygame.draw.circle(screen, item['color'], (int(item['position'].x), int(item['position'].y)), item['size'])

    # Draw the cue force besides the white ball if it's not moving
    white_ball = ball[NUM_BALLS - 1]
    if white_ball['speed'] == 0:
        speed_text = font.render(f"{int(current_speed)}", True, TEXT_COLOR)
        text_rect = speed_text.get_rect(center=(white_ball['position'].x + 30, white_ball['position'].y))
        screen.blit(speed_text, text_rect)


# Draw the pool cue
def draw_cue():
    white_ball = ball[NUM_BALLS - 1]
    cue_start = white_ball['position']
    cue_end = cue_start + Vector2(cue_length * math.cos(math.radians(cue_angle)),
                                  cue_length * math.sin(math.radians(cue_angle)))
    pygame.draw.line(screen, WHITE, (cue_start.x, cue_start.y), (cue_end.x, cue_end.y), 3)


# Initialize the game

# Generate initial positions for balls
initial_positions = initial_ball_positions()[:NUM_BALLS]

# Initialize the game balls
ball = {
    i: {
        'mass': BALL_MASS,
        'size': BALL_SIZE,
        'speed': 0,
        'position': Vector2(initial_positions[i]),
        'direction': Vector2(0, 0),
        'color': POOL_BALL_COLORS[i % len(POOL_BALL_COLORS)],
        'potted': False
    } for i in range(NUM_BALLS)
}

# Initialize the white ball
white_ball_pos = Vector2((2 * BORDER_WIDTH + TABLE_WIDTH) // 2, BORDER_WIDTH + TABLE_HEIGHT - 100)
ball[NUM_BALLS] = {
    'mass': BALL_MASS,
    'size': BALL_SIZE,
    'speed': 0,
    'position': white_ball_pos,
    'direction': Vector2(0, 0),
    'color': WHITE,
    'potted': False
}
NUM_BALLS += 1  # Include the white ball in the count


# Main game loop
def main():
    global cue_angle, current_speed, running
    clock = pygame.time.Clock()
    running = True
    ball_moving = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # On mouse button move white ball based on cue angle
                    if ball[NUM_BALLS - 1]['speed'] == 0:
                        ball[NUM_BALLS - 1]['speed'] = current_speed
                        ball[NUM_BALLS - 1]['direction'] = -Vector2(math.cos(math.radians(cue_angle)),
                                                                    math.sin(math.radians(cue_angle)))
                        ball_moving = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC key to quit
                    running = False

        # Update cue angle and strike power, based on mouse position
        mouse_pos = pygame.mouse.get_pos()
        white_ball_pos = ball[NUM_BALLS - 1]['position']
        distance_to_mouse = (mouse_pos[0] - white_ball_pos.x, mouse_pos[1] - white_ball_pos.y)
        distance = Vector2(distance_to_mouse).length()

        # Adjust speed based on distance
        current_speed = max(1, min(MAX_SPEED, int(distance / 10)))

        cue_angle = calculate_cue_angle(mouse_pos)

        if ball_moving:
            # Update balls position
            update_positions()
            handle_ball_collisions()
            ball_moving = any(item['speed'] > 0 for item in ball.values() if not item['potted'])

        draw_game_table()
        if ball[NUM_BALLS - 1]['speed'] == 0:
            # Draw cue only if white bass is not moving
            draw_cue()

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()
    sys.exit()


# Run the game
if __name__ == "__main__":
    main()
