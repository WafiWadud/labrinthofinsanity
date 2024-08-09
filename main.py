import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = (WIDTH // CELL_SIZE) - 1
GRID_HEIGHT = (HEIGHT // CELL_SIZE) - 1
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")


# Wilson's algorithm
def generate_maze(width, height):
    # Initialize the maze with all walls
    maze = [[0 for _ in range(width)] for _ in range(height)]

    def get_neighbors(x, y):
        neighbors = []
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append((nx, ny))
        return neighbors

    # Choose a random starting cell (must be odd coordinates)
    start = (random.randrange(1, width, 2), random.randrange(1, height, 2))
    maze[start[1]][start[0]] = 1  # Mark as passage

    # List of unvisited cells (only odd coordinates)
    unvisited = [
        (x, y)
        for y in range(1, height, 2)
        for x in range(1, width, 2)
        if (x, y) != start
    ]

    while unvisited:
        current = random.choice(unvisited)
        path = [current]

        while current not in [
            (x, y) for y in range(height) for x in range(width) if maze[y][x] == 1
        ]:
            next_cell = random.choice(get_neighbors(*current))
            if next_cell in path:
                path = path[: path.index(next_cell) + 1]
            else:
                path.append(next_cell)
            current = next_cell

        for i in range(len(path) - 1):
            current = path[i]
            next_cell = path[i + 1]
            maze[current[1]][current[0]] = 1  # Mark as passage
            # Create passage between cells
            wall_x = current[0] + (next_cell[0] - current[0]) // 2
            wall_y = current[1] + (next_cell[1] - current[1]) // 2
            maze[wall_y][wall_x] = 1
            if current in unvisited:
                unvisited.remove(current)

        maze[path[-1][1]][path[-1][0]] = 1
        if path[-1] in unvisited:
            unvisited.remove(path[-1])

    # Ensure the start position is accessible
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = start[0] + dx, start[1] + dy
        if 0 <= nx < width and 0 <= ny < height:
            maze[ny][nx] = 1

    # Choose a random exit position on the edge of the maze
    edge_passages = []
    for x in range(width):
        if maze[1][x] == 1:
            edge_passages.append((x, 0))
        if maze[height - 2][x] == 1:
            edge_passages.append((x, height - 1))
    for y in range(height):
        if maze[y][1] == 1:
            edge_passages.append((0, y))
        if maze[y][width - 2] == 1:
            edge_passages.append((width - 1, y))

    exit_pos = random.choice(edge_passages)
    maze[exit_pos[1]][exit_pos[0]] = 1  # Ensure the exit is a passage

    return maze, start, exit_pos


# Generate the maze
maze, start, exit_pos = generate_maze(GRID_WIDTH, GRID_HEIGHT)

# Player
player_pos = list(start)
has_key = False

# Key and exit positions
key_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
while key_pos == tuple(player_pos):
    key_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1

            new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
            if (
                0 <= new_x < GRID_WIDTH
                and 0 <= new_y < GRID_HEIGHT
                and maze[new_y][new_x] == 1
            ):
                player_pos = [new_x, new_y]

    # Check if player has collected the key
    if tuple(player_pos) == key_pos:
        has_key = True
        key_pos = (-1, -1)  # Remove the key from the maze

    # Check if player has reached the exit with the key
    if has_key and tuple(player_pos) == exit_pos:
        print("Congratulations! You've escaped the maze!")
        running = False

    # Clear the screen
    screen.fill(BLACK)

    # Draw the visible part of the maze
    visibility_range = 1000
    for y in range(
        max(0, player_pos[1] - visibility_range),
        min(GRID_HEIGHT, player_pos[1] + visibility_range + 1),
    ):
        for x in range(
            max(0, player_pos[0] - visibility_range),
            min(GRID_WIDTH, player_pos[0] + visibility_range + 1),
        ):
            if maze[y][x] == 0:
                pygame.draw.rect(
                    screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
            else:
                pygame.draw.rect(
                    screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

    # Draw the player
    pygame.draw.rect(
        screen,
        RED,
        (player_pos[0] * CELL_SIZE, player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    )

    # Draw the key if it's visible and not collected
    if (
        not has_key
        and max(abs(key_pos[0] - player_pos[0]), abs(key_pos[1] - player_pos[1]))
        <= visibility_range
    ):
        pygame.draw.rect(
            screen,
            YELLOW,
            (key_pos[0] * CELL_SIZE, key_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

    # Draw the exit if it's visible
    if (
        max(abs(exit_pos[0] - player_pos[0]), abs(exit_pos[1] - player_pos[1]))
        <= visibility_range
    ):
        pygame.draw.rect(
            screen,
            GREEN,
            (exit_pos[0] * CELL_SIZE, exit_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(30)

# Quit Pygame
pygame.quit()
