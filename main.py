from sys import exit
import pygame
from grid import Grid

# Visual Constants 
cell_size = 40
grid_line_color = (200, 200, 200)   # Light Grey
bg_color = (255, 255, 255)          # White
start_color = (0, 255, 0)           # Green
goal_color = (255, 0, 0)            # Red
wall_color = (50, 50, 50)           # Dark Grey

def draw_grid(screen, grid):           
    """Draw Grid lines, cells, start, goal, and walls"""
    screen.fill(bg_color)

    # Special Cells
    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)

            rect = pygame.Rect(
                x * cell_size, 
                y * cell_size, 
                cell_size, 
                cell_size
            )

            if coord == grid.start:
                pygame.draw.rect(screen, start_color, rect)
            elif coord == grid.goal:
                pygame.draw.rect(screen, goal_color, rect)
            elif coord in grid.walls:
                pygame.draw.rect(screen, wall_color, rect)


    # Draw Grid lines

    for x in range(grid.width + 1):
        pygame.draw.line(
            screen,
            grid_line_color,
            (x * cell_size, 0),
            (x * cell_size, grid.height * cell_size)
        )


    for y in range(grid.height + 1):
        pygame.draw.line(
            screen,
            grid_line_color,
            (0, y * cell_size),
            (grid.width * cell_size, y * cell_size)
        )



def main():

    pygame.init()
    pygame.display.set_caption('Algorithm Lab - Maze Editor')

    # initialize Grid Modal
    grid = Grid(
        width = 15,
        height = 15,
        start = (1, 1),
        goal = (14, 14),
        walls = {(5, 2), (5, 3), (5,4), (5, 5), (6, 5), (7, 5), (7, 6), (8, 6)}
    )


    screen_width = grid.width * cell_size
    screen_height = grid.width * cell_size

    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()