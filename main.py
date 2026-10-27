from sys import exit
import pygame
from grid import Grid, Coordinate
from algorithms import bfs, dfs, astar

# Visual Constants 
cell_size = 40
grid_line_color = (200, 200, 200)   # Light Grey
bg_color = (255, 255, 255)          # White
start_color = (0, 255, 0)           # Green
goal_color = (255, 0, 0)            # Red
wall_color = (50, 50, 50)           # Dark Grey
visited_color = (173, 216, 230)     # Light Blue
path_color = (255, 213, 79)         # Gold 

algorithms = {
    "1": ("Breadth-First Search (BFS)", bfs),
    "2": ("Depth First Search (DFS)", dfs),
    "3": ("A* Search (Manhattan)", astar)
}


def get_grid_pos(mouse_pos: Coordinate) -> Coordinate: 
    """Convert pixel coordinates to grid (x / row, y / col) coordinates."""
    pixel_x, pixel_y = mouse_pos

    grid_x = pixel_x // cell_size       # Converting pixels at pos x into x-coordinate
    grid_y = pixel_y // cell_size       # converting pixels at pos y into y-coordinate

    return (grid_x, grid_y)

def draw_grid(
        screen: pygame.surface, 
        grid: Grid,
        visited: list,
        path: list
    ):           
    """Draw Grid lines, cells, start, goal, and walls."""

    screen.fill(bg_color)

    # Visited Cells
    for coord in visited:
        # coord[0] = x and coord[1] = y
        if coord != grid.start and coord != grid.goal:
            rect = pygame.Rect(             # placing the position of path at pixel position
                coord[0] * cell_size,
                coord[1] * cell_size,
                cell_size,
                cell_size
            )

            pygame.draw.rect(screen, visited_color, rect)

    # Shortest Path Cells 
    for coord in path:
        # coord[0] = x and coord[1] = y
        if coord != grid.start and coord != grid.goal:
            rect = pygame.Rect(             # placing the position of path at pixel position
                coord[0] * cell_size,
                coord[1] * cell_size,
                cell_size,
                cell_size
            )

            pygame.draw.rect(screen, path_color, rect)


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
        height = 16,
        start = (1, 1),
        goal = (14, 10),
    )


    screen_width = grid.width * cell_size           # used to get screen width in pixels
    screen_height = grid.height * cell_size         # used to get screen height in pixels

    screen = pygame.display.set_mode((screen_width, screen_height))  
    clock = pygame.time.Clock()

    selected_key = "1"
    name, current_algo = algorithms[selected_key]
    pygame.display.set_caption(f"Algorithm Lab - [{name}] | [1] BFS  [2] DFS  [3] A*")
    

    # Visual state trackers
    visited_cells = set()                           # Stores cells processed during the animation
    displayed_path = []                             # Stores path cells that have been revealed so far
    full_path = []                                  # Stores the completed shortest path after the goal is found

    # Animation Control Variables
    search_generator = None
    is_searching = False
    is_drawing_path = False
    path_index = 0

    # Number of nodes processed per frame
    steps_per_frame = 1

    running = True
    while running:
        for event in pygame.event.get():
            # Quitting program
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Press C to reset board 
                if event.key == pygame.K_c:
                    grid.walls.clear()
                    visited_cells.clear()
                    displayed_path.clear()
                    is_searching = False
                    is_drawing_path = False
                    search_generator = None

                # Selecting algorithm when idle 
                elif not is_searching and not is_drawing_path:                  # prevents starting a new search while another search or path is operating 
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        selected_key = pygame.key.name(event.key)
                        name, current_algo = algorithms[selected_key]
                        pygame.display.set_caption(f"Algorithm Lab - [{name}] | [1] BFS  [2] DFS  [3] A*")

                    # Run selected algorithm using SPACE
                    elif event.key == pygame.K_SPACE:
                        visited_cells.clear()
                        displayed_path.clear()
                        full_path.clear()
                        search_generator = current_algo(grid)
                        is_searching = True

        
        if (not is_searching) and (not is_drawing_path):            # Disables Maze editing during animations
            # Mouse Interaction
            mouse_pressed = pygame.mouse.get_pressed()              # Mouse Buttons (left, middle, right)
            keys_pressed = pygame.key.get_pressed()                 # Keyboard keys
            grid_pos = get_grid_pos(pygame.mouse.get_pos())         # Grid coordinate position conversion from mouse pixel position

            if grid.in_bounds(grid_pos):                    # First we confirm that the mouse is in the grid
                
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

        # Search exploration animation
        if is_searching and search_generator:
            for _ in range(steps_per_frame):
                try:                                            # Works as generator eventually has no more value and raises error       
                    event_type, data = next(search_generator)
                    if event_type == "visiting":
                        visited_cells.add(data)
                    elif event_type == "path":
                        full_path = data
                        is_searching = False
                        is_drawing_path = True
                        path_index = 0
                        break
                    elif event_type == "not_found":
                        is_searching = False
                        break
                except StopIteration:
                    is_searching = False
                    break

        # Shortest Path Animation
        elif is_drawing_path:
            if path_index < len(full_path):
                displayed_path.append(full_path[path_index])
                path_index += 1
            else:
                is_drawing_path = False

        draw_grid(screen, grid, visited_cells, displayed_path)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()