# Pool Game

A simple pool game implemented in Python using Pygame. The game features a set of colored pool balls and a white cue ball, with basic physics for ball movement and collision handling.

## Features

- **Basic Pool Physics**: Balls move and collide with each other and the walls of the screen.
- **Ball Colors**: A variety of colors for different balls.
- **Friction**: Friction is applied to simulate ball slowing over time.
- **Collisions**: Basic collision detection and response between balls.


## Code Overview

- **Imports**: The script uses `pygame` for game rendering and input handling, `Vector2` from `pygame.math` for vector operations, and `random` and `math` for game physics and ball movement.

- **Initialization**:
    - The game window is set up with dimensions 400x800 pixels.
    - Colors and ball properties are defined.

- **Ball Setup**:
    - Balls are arranged in a triangular formation.
    - Each ball has properties such as mass, size, speed, and direction.
    - The white cue ball is initialized separately.

- **Physics**:
    - Ball positions are updated based on their speed and direction.
    - Ball collisions with walls and each other are handled with basic physics principles.

- **Rendering**:
    - Balls are drawn on the screen with their respective colors.

- **Main Game Loop**:
    - Handles user input, updates ball positions, processes collisions, and draws the game state on the screen.

## Controls

- **Quit Game**: Press `Q` to quit the game.

