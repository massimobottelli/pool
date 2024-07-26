import pygame
from pygame.math import Vector2
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pool')

# Define colors
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)

# Define ball properties
BALL_SIZE = 10
BALL_MASS = 1
FRICTION = 0.02
EDGE_FRICTION = 1

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


# Function to calculate positions of balls in a triangular formation
def calculate_positions():
    positions = []
    rows = 5  # Number of rows in the formation
    for row in range(rows):
        y = 100 + (rows - row - 1) * BALL_SIZE * 2.5
        for col in range(row + 1):
            x = WIDTH // 2 - (row / 2 - col) * BALL_SIZE * 2.5
            positions.append((x, y))
    return positions


# Generate initial positions for balls
initial_positions = calculate_positions()[:NUM_BALLS]


# Generate a random direction vector
def random_direction():
    angle = random.uniform(0, 2 * math.pi)
    return Vector2(math.cos(angle), math.sin(angle))


# Initialize ball objects (including the white ball)
objects = {
    i: {
        'mass': BALL_MASS,
        'size': BALL_SIZE,
        'speed': 0,
        'position': Vector2(initial_positions[i]),
        'direction': random_direction(),
        'color': POOL_BALL_COLORS[i % len(POOL_BALL_COLORS)]
    } for i in range(NUM_BALLS)
}

# Add the white ball
white_ball_pos = Vector2(WIDTH // 2, HEIGHT - 100)
objects[NUM_BALLS] = {
    'mass': BALL_MASS,
    'size': BALL_SIZE,
    'speed': 10,
    'position': white_ball_pos,
    'direction': Vector2(0, -1.2),   # set the initial direction oh White ball
    'color': WHITE
}
NUM_BALLS += 1  # Include the white ball in the count


# Update ball positions and handle wall collisions
def update_positions():
    for obj in objects.values():
        # Update position based on direction and speed
        obj['position'] += obj['direction'] * obj['speed']

        # Apply friction to decrease speed over time
        obj['speed'] = max(0, obj['speed'] - FRICTION)

        # Handle wall collisions and apply edge friction
        if obj['position'].x <= obj['size']:
            obj['direction'].x *= -1
            obj['position'].x = obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        elif obj['position'].x >= WIDTH - obj['size']:
            obj['direction'].x *= -1
            obj['position'].x = WIDTH - obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        if obj['position'].y <= obj['size']:
            obj['direction'].y *= -1
            obj['position'].y = obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)

        elif obj['position'].y >= HEIGHT - obj['size']:
            obj['direction'].y *= -1
            obj['position'].y = HEIGHT - obj['size']
            obj['speed'] = max(0, obj['speed'] - EDGE_FRICTION)


# Handle collisions between balls
def handle_collisions():
    for i, obj1 in objects.items():
        for j, obj2 in objects.items():
            if i < j:
                pos_diff = obj1['position'] - obj2['position']
                distance = pos_diff.length()
                if distance < obj1['size'] + obj2['size']:  # Collision detected
                    # Calculate normal vector
                    normal = pos_diff.normalize()

                    # Relative velocity
                    v_rel = obj1['direction'] * obj1['speed'] - obj2['direction'] * obj2['speed']
                    v_rel_normal = v_rel.dot(normal)

                    if v_rel_normal <= 0:
                        # Calculate impulse and update velocities
                        impulse = (2 * v_rel_normal) / (obj1['mass'] + obj2['mass'])
                        obj1['direction'] -= impulse * obj2['mass'] * normal
                        obj2['direction'] += impulse * obj1['mass'] * normal

                        # Update speeds and normalize directions
                        obj1['speed'] = obj1['direction'].length()
                        obj2['speed'] = obj2['direction'].length()
                        obj1['direction'].normalize_ip()
                        obj2['direction'].normalize_ip()

                        # Apply collision friction
                        obj1['speed'] = max(0, obj1['speed'] - 0.25 * EDGE_FRICTION)
                        obj2['speed'] = max(0, obj2['speed'] - 0.25 * EDGE_FRICTION)


# Draw all balls on the screen
def draw_balls():
    screen.fill(GREEN)  # Clear the screen with background color
    for obj in objects.values():
        pygame.draw.circle(screen, obj['color'], (int(obj['position'].x), int(obj['position'].y)), obj['size'])
    pygame.display.flip()


# Main game loop
def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        update_positions()
        handle_collisions()
        draw_balls()

        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()
    sys.exit()


# Run the game
if __name__ == "__main__":
    main()
