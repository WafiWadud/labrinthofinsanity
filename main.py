import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 15
GRID_WIDTH = WIDTH // CELL_SIZE - 1
GRID_HEIGHT = HEIGHT // CELL_SIZE - 1
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


# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.color = BLUE
        self.move_cooldown = 0
        self.move_delay = 15

    def move(self, player_pos, maze):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance != 0:
            dx, dy = dx / distance, dy / distance

        new_x = int(self.pos[0] + dx)
        new_y = int(self.pos[1] + dy)

        if (
            0 <= new_x < GRID_WIDTH
            and 0 <= new_y < GRID_HEIGHT
            and maze[new_y][new_x] == 1
        ):
            self.pos = [new_x, new_y]
            self.move_cooldown = self.move_delay

    def knockback(self, player_pos, maze):
        dx = self.pos[0] - player_pos[0]
        dy = self.pos[1] - player_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance != 0:
            dx, dy = dx / distance, dy / distance

        for _ in range(2):  # Knock back by 2 squares
            new_x = int(self.pos[0] + dx)
            new_y = int(self.pos[1] + dy)
            if (
                0 <= new_x < GRID_WIDTH
                and 0 <= new_y < GRID_HEIGHT
                and maze[new_y][new_x] == 1
            ):
                self.pos = [new_x, new_y]
            else:
                break  # Stop if we hit a wall

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (self.pos[0] * CELL_SIZE, self.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )


# Generate the maze
maze, start, exit_pos = generate_maze(GRID_WIDTH, GRID_HEIGHT)

# Player
player_pos = list(start)
has_shotgun = True
shotgun_ammo = 5


# Enemy
enemy = Enemy(
    exit_pos[0] - random.randint(1, 5) + random.randint(1, GRID_WIDTH - 2),
    exit_pos[1] - random.randint(1, 5) + random.randint(1, GRID_HEIGHT - 2),
)

# Game loop
running = True
clock = pygame.time.Clock()
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            dx, dy = 0, 0
            if event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_SPACE:
                if has_shotgun and shotgun_ammo > 0:
                    shotgun_ammo -= 1
                    enemy.knockback(player_pos, maze)
                    print(f"Shotgun fired! Ammo left: {shotgun_ammo}")

            new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
            if maze[new_y][new_x] == 1:
                player_pos = [new_x, new_y]

    if not game_over:
        # Move enemy
        enemy.move(player_pos, maze)

        # Check if player has reached the exit with the key
        if tuple(player_pos) == exit_pos:
            print("Congratulations! You've escaped the maze!")
            running = False

        # Check if enemy has caught the player
        if player_pos == enemy.pos:
            print("Game Over! The enemy caught you.")
            game_over = True

        # Randomly spawn shotgun and ammo
        if not has_shotgun and random.random() < 0.001:  # Adjust probability as needed
            shotgun_pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if maze[shotgun_pos[1]][shotgun_pos[0]] == 1 and shotgun_pos != tuple(
                player_pos
            ):
                has_shotgun = True
                shotgun_ammo += 3
                print("You found a shotgun with 3 ammo!")

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

    # Draw the enemy if it's visible
    if (
        max(abs(enemy.pos[0] - player_pos[0]), abs(enemy.pos[1] - player_pos[1]))
        <= visibility_range
    ):
        enemy.draw(screen)

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
