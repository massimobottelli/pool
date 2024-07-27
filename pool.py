import pygame
from pygame.math import Vector2
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
WINDOWS_WIDTH, WINDOWS_HEIGHT = 500, 900
BORDER_WIDTH = 50
TABLE_WIDTH, TABLE_HEIGHT = WINDOWS_WIDTH - 2 * BORDER_WIDTH, WINDOWS_HEIGHT - 2 * BORDER_WIDTH
screen = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
pygame.display.set_caption('Pool')

# Score
score = 0

# Define colors
GREEN = (0, 128, 0)
BROWN = (110, 40, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 255, 0)  # Yellow for speed text

# Define ball properties
BALL_SIZE = 10
BALL_MASS = 1
FRICTION = 0.02
EDGE_FRICTION = 1
MAX_SPEED = 20
STANDARD_SPEED = 10

# Define hole properties
HOLE_SIZE = 4 * BALL_SIZE
HOLE_COLOR = BLACK

# Define number of balls and colors
NUM_BALLS = 15
POOL_BALL_COLORS = [
    (255, 255, 0),  # Yellow
    (0, 0, 255),  # Blue
    (255, 0, 0),  # Red
    (128, 0, 128),  # Dark purple
    (255, 165, 0),  # Orange
    (0, 255, 0),  # Green
    (255, 0, 0),  # Red
    (0, 0, 0),  # Black
    (255, 255, 0),  # Yellow
    (0, 0, 255),  # Blue
    (255, 0, 0),  # Red
    (128, 0, 128),  # Dark purple
    (255, 165, 0),  # Orange
    (0, 255, 0),  # Green
    (255, 0, 0)  # Red
]

# Initialize font
font = pygame.font.SysFont(None, 36)

# Function to calculate positions of balls in a triangular formation
def calculate_positions():
    positions = []
    rows = 5
    for row in range(rows):
        y = BORDER_WIDTH + 100 + (rows - row - 1) * BALL_SIZE * 2.5
        for col in range(row + 1):
            x = (2 * BORDER_WIDTH + TABLE_WIDTH) // 2 - (row / 2 - col) * BALL_SIZE * 2.5
            positions.append((x, y))
    return positions

# Generate initial positions for balls
initial_positions = calculate_positions()[:NUM_BALLS]

# Initialize ball objects (including the white ball)
objects = {
    i: {
        'mass': BALL_MASS,
        'size': BALL_SIZE,
        'speed': 0,
        'position': Vector2(initial_positions[i]),
        'direction': Vector2(0, 0),
        'color': POOL_BALL_COLORS[i % len(POOL_BALL_COLORS)],
        'potted': False  # Add a 'potted' flag
    } for i in range(NUM_BALLS)
}

# Add the white ball
white_ball_pos = Vector2((2 * BORDER_WIDTH + TABLE_WIDTH) // 2, BORDER_WIDTH + TABLE_HEIGHT - 100)
objects[NUM_BALLS] = {
    'mass': BALL_MASS,
    'size': BALL_SIZE,
    'speed': 0,
    'position': white_ball_pos,
    'direction': Vector2(0, -1.1),
    'color': WHITE,
    'potted': False  # Add a 'potted' flag
}
NUM_BALLS += 1  # Include the white ball in the count

# Initialize cue settings
cue_angle = 90
cue_length = 150
current_speed = STANDARD_SPEED

# Update ball positions and handle wall collisions
def update_positions():
    global running, score  # Add global running to quit the game

    for obj in objects.values():
        if obj['potted']:
            continue  # Skip potted balls

        obj['position'] += obj['direction'] * obj['speed']
        obj['speed'] = max(0, obj['speed'] - FRICTION)

        # Handle wall collisions and apply edge friction
        if obj['position'].x <= BORDER_WIDTH + obj['size']:
            obj['direction'].x *= -1
            obj['position'].x = BORDER_WIDTH + obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        elif obj['position'].x >= BORDER_WIDTH + TABLE_WIDTH - obj['size']:
            obj['direction'].x *= -1
            obj['position'].x = BORDER_WIDTH + TABLE_WIDTH - obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        if obj['position'].y <= BORDER_WIDTH + obj['size']:
            obj['direction'].y *= -1
            obj['position'].y = BORDER_WIDTH + obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        elif obj['position'].y >= BORDER_WIDTH + TABLE_HEIGHT - obj['size']:
            obj['direction'].y *= -1
            obj['position'].y = BORDER_WIDTH + TABLE_HEIGHT - obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        # Check for collision with holes
        for hole_pos in hole_positions:
            if (obj['position'] - Vector2(hole_pos)).length() <= HOLE_SIZE / 2:
                obj['potted'] = True
                obj['speed'] = 0
                score += 1

                # If the white ball is potted, quit the game
                if obj['color'] == WHITE:
                    global running  # Declare running as global to modify its value
                    running = False  # Set the running flag to False to quit the game
                break

# Handle collisions between balls
def handle_collisions():
    for i, obj1 in objects.items():
        if obj1['potted']:
            continue  # Skip potted balls
        for j, obj2 in objects.items():
            if i < j and not obj2['potted']:
                pos_diff = obj1['position'] - obj2['position']
                distance = pos_diff.length()
                if distance < obj1['size'] + obj2['size']:  # Collision detected
                    normal = pos_diff.normalize()
                    v_rel = obj1['direction'] * obj1['speed'] - obj2['direction'] * obj2['speed']
                    v_rel_normal = v_rel.dot(normal)

                    if v_rel_normal <= 0:
                        impulse = (2 * v_rel_normal) / (obj1['mass'] + obj2['mass'])
                        obj1['direction'] -= impulse * obj2['mass'] * normal
                        obj2['direction'] += impulse * obj1['mass'] * normal

                        obj1['speed'] = max(0, obj1['direction'].length() - 2 * FRICTION)
                        obj2['speed'] = max(0, obj2['direction'].length() - 2 * FRICTION)
                        obj1['direction'].normalize_ip()
                        obj2['direction'].normalize_ip()

# Draw holes on the table
hole_positions = [
    (BORDER_WIDTH, BORDER_WIDTH),
    (BORDER_WIDTH + TABLE_WIDTH, BORDER_WIDTH),
    (BORDER_WIDTH, BORDER_WIDTH + TABLE_HEIGHT),
    (BORDER_WIDTH + TABLE_WIDTH, BORDER_WIDTH + TABLE_HEIGHT),
    (BORDER_WIDTH, TABLE_HEIGHT // 2),
    (BORDER_WIDTH + TABLE_WIDTH, TABLE_HEIGHT // 2)
]

def draw_holes():
    for pos in hole_positions:
        pygame.draw.circle(screen, HOLE_COLOR, pos, HOLE_SIZE // 2)

# Draw all balls, score, and speed text
def draw_balls():
    screen.fill(BROWN)
    pygame.draw.rect(screen, GREEN, (BORDER_WIDTH, BORDER_WIDTH, TABLE_WIDTH, TABLE_HEIGHT))
    draw_holes()

    # Draw the score
    score_text = font.render(f"{score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))  # Draw score in the top left corner

    for obj in objects.values():
        if not obj['potted']:
            pygame.draw.circle(screen, obj['color'], (int(obj['position'].x), int(obj['position'].y)), obj['size'])

    # Draw the initial speed of the white ball if it's not moving
    white_ball = objects[NUM_BALLS - 1]
    if white_ball['speed'] == 0:
        speed_text = font.render(f"{int(current_speed)}", True, TEXT_COLOR)
        text_rect = speed_text.get_rect(center=(white_ball['position'].x + 30, white_ball['position'].y))
        screen.blit(speed_text, text_rect)

# Draw the pool cue
def draw_cue():
    white_ball = objects[NUM_BALLS - 1]
    cue_start = white_ball['position']
    cue_end = cue_start + Vector2(cue_length * math.cos(math.radians(cue_angle)),
                                  cue_length * math.sin(math.radians(cue_angle)))
    pygame.draw.line(screen, WHITE, (cue_start.x, cue_start.y), (cue_end.x, cue_end.y), 3)

# Main game loop
def main():
    global cue_angle, current_speed, running
    running = True
    clock = pygame.time.Clock()
    ball_moving = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if objects[NUM_BALLS - 1]['speed'] == 0:
                        objects[NUM_BALLS - 1]['speed'] = current_speed
                        objects[NUM_BALLS - 1]['direction'] = -Vector2(math.cos(math.radians(cue_angle)),
                                                                       math.sin(math.radians(cue_angle)))
                        ball_moving = True
                elif event.key == pygame.K_LEFT:
                    cue_angle = (cue_angle - 5) % 360
                elif event.key == pygame.K_RIGHT:
                    cue_angle = (cue_angle + 5) % 360
                elif event.key == pygame.K_UP:
                    current_speed = min(MAX_SPEED, current_speed + 1)
                elif event.key == pygame.K_DOWN:
                    current_speed = max(1, current_speed - 1)

        if ball_moving:
            update_positions()
            handle_collisions()
            ball_moving = any(obj['speed'] > 0 for obj in objects.values() if not obj['potted'])

        draw_balls()
        if objects[NUM_BALLS - 1]['speed'] == 0:
            draw_cue()

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()
