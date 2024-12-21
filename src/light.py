import pygame
import random
import math
from gridElements import Block

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 500
BLOCKS = 25
BLOCK_SIZE = WIDTH // BLOCKS
LIGHT_RADIUS = BLOCKS // 3
WALL_BLOCKS = BLOCKS * 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (200, 200, 200)
FLOOR_COLOR = (50, 50, 50)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Light Simulation")

# Create grid of blocks
grid = [[Block(x, y) for x in range(BLOCKS)] for y in range(BLOCKS)]

for _ in range(WALL_BLOCKS):
    grid[random.randint(0, len(grid)-1)][random.randint(0, len(grid)-1)].walls = {
            "right": random.choice([True, True, False]),
            "left": random.choice([True, True, False]),
            "top": random.choice([True, True, False]),
            "down": random.choice([True, True, False]),
        }
def cast_light(start_x, start_y):
    """Calculate the visible area from the light source, considering starting block's walls."""
    visible = set()

    # Get the starting block
    start_block = grid[start_y][start_x]

    # Define direction constraints based on the starting block's walls
    direction_constraints = {
        "top": not start_block.walls["top"],
        "right": not start_block.walls["right"],
        "down": not start_block.walls["down"],
        "left": not start_block.walls["left"],
    }

    for angle in range(0, 360):  # Cast light in all directions
        radian = math.radians(angle)
        dx = math.cos(radian)
        dy = math.sin(radian)

        # Skip angles where the light is blocked by the starting block's walls
        if (dy < 0 and not direction_constraints["top"]) or \
           (dx > 0 and not direction_constraints["right"]) or \
           (dy > 0 and not direction_constraints["down"]) or \
           (dx < 0 and not direction_constraints["left"]):
            continue

        for radius in range(1, LIGHT_RADIUS + 1):
            x = start_x + round(dx * radius)
            y = start_y + round(dy * radius)
            if 0 <= x < BLOCKS and 0 <= y < BLOCKS:  # Check grid bounds
                visible.add((x, y))
                block = grid[y][x]

                # Stop if a wall is hit in the current direction
                if radius > 1:
                    px = start_x + round(dx * (radius - 1))
                    py = start_y + round(dy * (radius - 1))
                    prev_block = grid[py][px]
                    if (
                        (px < x and prev_block.walls["right"]) or
                        (px > x and prev_block.walls["left"]) or
                        (py < y and prev_block.walls["down"]) or
                        (py > y and prev_block.walls["top"])
                    ):
                        break

                if block.walls["top"] or block.walls["right"] or block.walls["down"] or block.walls["left"]:
                    break
            else:
                break

    return visible



def draw_grid(visible_blocks, light_source):
    """Draw the grid with walls, lighting effects, and visible floors."""
    # Draw floors for visible blocks
    for y in range(BLOCKS):
        for x in range(BLOCKS):
            block = grid[y][x]
            rect = pygame.Rect(x * BLOCK_SIZE + 2, y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4)

            if (x, y) in visible_blocks:
                # Fill visible block with floor color
                pygame.draw.rect(screen, FLOOR_COLOR, rect)

                # Draw walls
                if block.walls["top"]:
                    pygame.draw.line(screen, WALL_COLOR, rect.topleft, rect.topright, 2)
                if block.walls["right"]:
                    pygame.draw.line(screen, WALL_COLOR, rect.topright, rect.bottomright, 2)
                if block.walls["down"]:
                    pygame.draw.line(screen, WALL_COLOR, rect.bottomright, rect.bottomleft, 2)
                if block.walls["left"]:
                    pygame.draw.line(screen, WALL_COLOR, rect.bottomleft, rect.topleft, 2)

    # Highlight the light source
    pygame.draw.circle(
        screen,
        (255, 255, 0),
        (light_source[0] * BLOCK_SIZE + BLOCK_SIZE // 2, light_source[1] * BLOCK_SIZE + BLOCK_SIZE // 2),
        BLOCK_SIZE // 2,
    )


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get mouse position in block coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    light_x, light_y = mouse_x // BLOCK_SIZE, mouse_y // BLOCK_SIZE

    # Calculate visible blocks
    visible_blocks = cast_light(light_x, light_y)

    # Draw everything
    screen.fill(BLACK)
    draw_grid(visible_blocks, (light_x, light_y))
    pygame.display.flip()

# Quit Pygame
pygame.quit()
