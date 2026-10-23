from sys import exit
import pygame
from grid import Grid, Coordinate

# Visual Constants 
cell_size = 40
grid_line_color = (200, 200, 200)   # Light Grey
bg_color = (255, 255, 255)          # White
start_color = (0, 255, 0)           # Green
goal_color = (255, 0, 0)            # Red
wall_color = (50, 50, 50)           # Dark Grey


def get_grid_pos(mouse_pos: Coordinate) -> Coordinate: 
    """Convert pixel coordinates to grid (x / row, y / col) coordinates."""
    pixel_x, pixel_y = mouse_pos

    grid_x = pixel_x // cell_size       # Converting pixels at pos x into x-coordinate
    grid_y = pixel_y // cell_size       # converting pixels at pos y into y-coordinate

    return (grid_x, grid_y)

def draw_grid(screen: pygame.surface, grid: Grid):           
    """Draw Grid lines, cells, start, goal, and walls."""
    screen.fill(bg_color)

    # Special Cells
    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)

            rect = pygame.Rect(         # placing the position of rectangle at pixel position
                x * cell_size, 
                y * cell_size, 
                cell_size, 
                cell_size
            )

            # used to draw rectangles depending on the special cell value from grid class
            if coord == grid.start:
                pygame.draw.rect(screen, start_color, rect)
            elif coord == grid.goal:
                pygame.draw.rect(screen, goal_color, rect)
            elif coord in grid.walls:
                pygame.draw.rect(screen, wall_color, rect)


    # Draw Grid lines
    for x in range(grid.width + 1):                     # Vertical lines 
        pygame.draw.line(
            screen,
            grid_line_color,
            (x * cell_size, 0),                         # start position - Top
            (x * cell_size, grid.height * cell_size)    # end position - bottom
        )


    for y in range(grid.height + 1):                    # Horizontal lines 
        pygame.draw.line(
            screen,
            grid_line_color,
            (0, y * cell_size),                         # start position - left
            (grid.width * cell_size, y * cell_size)     # end position - right
        )



def main():

    pygame.init()
    pygame.display.set_caption('Algorithm Lab - Maze Editor')

    # initialize Grid Modal
    grid = Grid(
        width = 16,
        height = 12,
        start = (1, 1),
        goal = (14, 10),
    )


    screen_width = grid.width * cell_size           # used to get screen width in pixels
    screen_height = grid.height * cell_size         # used to get screen height in pixels

    screen = pygame.display.set_mode((screen_width, screen_height))  
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            # Quitting program
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Press C to clear all walls
                if event.key == pygame.K_c:
                    grid.walls.clear()

        # Mouse Interaction
        mouse_pressed = pygame.mouse.get_pressed()              # Mouse Buttons (left, middle, right)
        keys_pressed = pygame.key.get_pressed()                 # Keyboard keys
        grid_pos = get_grid_pos(pygame.mouse.get_pos())         # Grid coordinate position conversion from mouse pixel position

        if grid.in_bounds(grid_pos):        # First we confirm that the mouse is in the grid
            
            # Left mouse button
            if mouse_pressed[0]:

                if keys_pressed[pygame.K_s]:        # s - key
                    # Move start node (coordinate)
                    if grid_pos != grid.goal:           # start node cannot override goal node 
                        grid.walls.discard(grid_pos)    # remove any walls already there
                        grid.start = grid_pos           # assign or update the start node (coordinate)
                elif keys_pressed[pygame.K_g]:      # g - key
                    # Move goal node (coordinate)
                    if grid_pos != grid.start:          # goal node cannot override start node
                        grid.walls.discard(grid_pos)    # remove any walls already there
                        grid.goal = grid_pos            # assign or update the goal node (coordinate)
                else:
                    # Place a wall
                    if (grid_pos != grid.start) and (grid_pos != grid.goal): # Cannot override start or goal node
                        grid.walls.add(grid_pos)        # place wall node in set of walls

            # Right mouse button - Erase walls
            elif mouse_pressed[2]:
                grid.walls.discard(grid_pos)

        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()