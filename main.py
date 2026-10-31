from sys import exit
import pygame
from grid import Grid, Coordinate
from algorithms import bfs, dfs, astar
from maze_generators import generate_random_obstacles, generate_recursive_backtracker

# Dimensions 
cell_size = 40
hud_height = 85     # To make room for the metrics, hotkey and slider

# Color (Chromonyms.com)
grid_line_color = (200, 200, 200)   # Light Grey
bg_color = (255, 255, 255)          # White
start_color = (40, 167, 69)         # Green
goal_color = (255, 0, 0)            # Red
wall_color = (52, 58, 64)           # Onyx
visited_color = (173, 216, 230)     # Baby Blue
path_color = (255, 213, 79)         # Mustard

# Head Up Display (HUD) Styling
hud_bg_color = (33, 77, 41)         # Dark Charcoal Header
hud_text_color = (248, 249, 250)    # Ghost White
hud_accent_color = (255, 193, 7)    # Amber
status_searching = (100, 181, 246)  # Maya Blue
status_found = (129, 199, 132)      # Pistachio 
status_failed = (239, 83, 80)       # Sunset Orange

# Sliders Colors
slider_track_color = (73, 80, 87)   # Grey
slider_fill_color = (0, 123, 255)   # Blue
slider_knob_color = (248, 249, 250) # Ghost White

algorithms = {                                                   
    "1": ("Breadth-First Search (BFS)", bfs),
    "2": ("Depth First Search (DFS)", dfs),
    "3": ("A* Search (Manhattan)", astar)
}

class Slider:
    """A draggable UI Slider for controlling simulation speed"""
    def __init__(self, x: int, y: int, width: int,
                height: int, min_val: int = 1, max_val: int = 15, initial_val: int = 2):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.is_dragging = False
        self.knob_radius = height // 2 + 3

    def handle_event(self, event) -> bool:
        """Handles mouse down, drag and release. Returns True if value changed."""

        if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
            # Check click on track or slightly expanded knob hit-box 
            click_rect = self.rect.inflate(self.knob_radius * 2, self.knob_radius * 2)
            if click_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val(event.pos[0])
                return True

        elif (event.type == pygame.MOUSEBUTTONUP) and (event.button == 1):
            self.is_dragging = False

        elif (event.type == pygame.MOUSEMOTION) and self.is_dragging:
            self._update_val(event.pos[0])
            return True

        return False

    def _update_val(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / self.rect.width
        ratio = max(0.0, min(1.0, ratio))
        self.val = int(round(self.min_val + ratio * (self.max_val - self.min_val)))

    def draw(self, screen, font):
        # 1. Background track
        pygame.draw.rect(screen, slider_track_color, self.rect, border_radius = 4)

        # 2. Fill track portion
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.rect.width * ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, slider_fill_color, fill_rect, border_radius = 4)

        # 3. Knob thumb
        knob_x = self.rect.x + fill_width
        knob_y = self.rect.centery
        pygame.draw.circle(screen, slider_knob_color, (knob_x, knob_y), self.knob_radius)
        pygame.draw.circle(screen, (33, 37, 41), (knob_x, knob_y), self.knob_radius, 2)

        # 4. Label displaying current speed
        label_surf = font.render(f"Speed: {self.val}x", True, hud_text_color)
        screen.blit(label_surf, (self.rect.right + 12, self.rect.y -2))


def get_grid_pos(mouse_pos: Coordinate) -> Coordinate: 
    """Convert pixel coordinates to grid (x / row, y / col) coordinates."""
    pixel_x, pixel_y = mouse_pos

    if pixel_y < hud_height:
        return (-1, -1)

    grid_x = pixel_x // cell_size                       # Converting pixels at pos x into x-coordinate
    grid_y = (pixel_y - hud_height) // cell_size        # converting pixels at pos y into y-coordinate - subtract HUD height 

    return (grid_x, grid_y)


def draw_hud(
        screen: pygame.Surface, 
        font: pygame.font.Font,
        small_font: pygame.font.Font, 
        algo_name: str, 
        status: str, 
        visited_count: int, 
        path_len: int, 
        width: int,
        slider: Slider
    ):
    """Renders The Head Up Display Dashboard"""

    # HUD background banner 
    pygame.draw.rect(screen, hud_bg_color, pygame.Rect(0, 0, width, hud_height))
    pygame.draw.line(screen, (73, 80, 87), (0, hud_height - 1), (width, hud_height -1), 2)

    # Determine status color
    if status == "SEARCHING...":
        status_color = status_searching
    elif status == "PATH FOUND":
        status_color = status_found
    elif status == "NO PATH FOUND":
        status_color = status_failed
    else:
        status_color = hud_text_color

    # Shorten display name slightly so long names don't overflow
    if "(" in algo_name:
        display_name = algo_name.split(" (",)[0]
    else:
        display_name = algo_name
        
    # Row 1: Algo name (left) & Status (aligned right)
    algo_surf = font.render(f"Algo: {display_name}", True, hud_accent_color)
    status_surf = font.render(f"Status: {status}", True, status_color)

    # Blit: Algo on the left, status right after it with padding
    screen.blit(algo_surf, (16, 10))
    status_x = 16 + algo_surf.get_width() + 18
    screen.blit(status_surf, (status_x, 10))

    # Row 1 (Right): Visited & Path Length 
    stats_text = f"Visited: {visited_count}    Path: {path_len}"
    stats_surf = font.render(stats_text, True, hud_text_color)
    screen.blit(stats_surf, (width - stats_surf.get_width() - 16, 10))


    # Row 2: Controls hotkey helper
    helper_text = "[1/2/3] Switch Algo | [Space] Run | [C] Clear | [M] Maze | [R] Random | [S/G+Clicker] Endpoints"
    helper_surf = small_font.render(helper_text, True, (173, 181, 189))
    screen.blit(helper_surf, (16, 42))

    # Row 3: Draw Slider
    slider.draw(screen, small_font)


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
                coord[1] * cell_size + hud_height,
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
                coord[1] * cell_size + hud_height,
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
                y * cell_size + hud_height, 
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
            (x * cell_size, hud_height),                                # start position - Top
            (x * cell_size, hud_height + grid.height * cell_size)       # end position - bottom
        )


    for y in range(grid.height + 1):                    # Horizontal lines 
        pygame.draw.line(
            screen,
            grid_line_color,
            (0, hud_height + y * cell_size),                         # start position - left
            (grid.width * cell_size, hud_height + y * cell_size)     # end position - right
        )



def main():

    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont("Consolas", 15, bold = True)
    small_font = pygame.font.SysFont("Consolas", 12)


    pygame.display.set_caption('Algorithm Lab - Maze Editor')

    # initialize Grid Modal
    grid = Grid(
        width = 25,
        height = 12,
        start = (1, 1),
        goal = (14, 10),
    )

    screen_width = grid.width * cell_size                        # used to get screen width in pixels
    screen_height = grid.height * cell_size + hud_height         # used to get screen height in pixels

    pygame.display.set_caption('Algorithm Lab')

    screen = pygame.display.set_mode((screen_width, screen_height))  
    clock = pygame.time.Clock()

    # Initialize dynamic speed slider: (placed at x = 16, y = 58)
    speed_slider = Slider(
        x = 16,
        y = 66,
        width = 140,
        height = 10, 
        min_val = 1,
        max_val = 15,
        initial_val = 2
    )

    selected_key = "1"
    name, current_algo = algorithms[selected_key]
    status = "IDLE"
    

    # Visual state trackers
    visited_cells = set()                           # Stores cells processed during the animation
    displayed_path = []                             # Stores path cells that have been revealed so far
    full_path = []                                  # Stores the completed shortest path after the goal is found

    # Animation Control Variables
    search_generator = None
    is_searching = False
    is_drawing_path = False
    path_index = 0


    running = True
    while running:
        for event in pygame.event.get():
            # Quitting program
            if event.type == pygame.QUIT:
                running = False

            # Let the slider process clicks/drags regardless of simulation state
            speed_slider.handle_event(event)

            if event.type == pygame.KEYDOWN:
                # Press C to reset board 
                if event.key == pygame.K_c:
                    grid.walls.clear()
                    visited_cells.clear()
                    displayed_path.clear()
                    full_path.clear()
                    is_searching = False
                    is_drawing_path = False
                    search_generator = None
                    status = "IDLE"

                # When idle 
                elif not is_searching and not is_drawing_path:                  # prevents starting a new search while another search or path is operating 

                    # Random Obstacle scatter 
                    if event.key == pygame.K_r:
                        visited_cells.clear()
                        displayed_path.clear()
                        full_path.clear()
                        status = "IDLE"
                        grid.walls = generate_random_obstacles(grid, density = 0.28)

                    # Recursive Back-tracker Maze
                    elif event.key == pygame.K_m:
                        visited_cells.clear()
                        displayed_path.clear()
                        full_path.clear()
                        status = "IDLE"
                        grid.walls = generate_recursive_backtracker(grid)

                    # Selecting algorithms
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        selected_key = pygame.key.name(event.key)
                        name, current_algo = algorithms[selected_key]
                        visited_cells.clear()
                        displayed_path.clear()
                        full_path.clear()
                        status = "IDLE"

                    # Run selected algorithm using SPACE
                    elif event.key == pygame.K_SPACE:
                        visited_cells.clear()
                        displayed_path.clear()
                        full_path.clear()
                        search_generator = current_algo(grid)
                        is_searching = True
                        status = "SEARCHING..."

        # Mouse editing (only if idle and not dragging slider)
        if (not is_searching) and (not is_drawing_path) and (not speed_slider.is_dragging):            # Disables Maze editing during animations and slider movement
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
            speed = speed_slider.val
            for _ in range(speed):
                try:                                            # Works as generator eventually has no more value and raises error       
                    event_type, data = next(search_generator)
                    if event_type == "visiting":
                        visited_cells.add(data)
                    elif event_type == "path":
                        full_path = data
                        is_searching = False
                        is_drawing_path = True
                        path_index = 0
                        status = "PATH FOUND"
                        break
                    elif event_type == "not_found":
                        is_searching = False
                        status = "NO PATH FOUND"
                        break
                except StopIteration:
                    is_searching = False
                    if not full_path:
                        status = "NO PATH FOUND"
                    break

        # Shortest Path Animation (scales with slider rate as well)
        elif is_drawing_path:
            path_speed = max(1, speed_slider.val // 2)
            for _ in range(path_speed):
                if path_index < len(full_path):
                    displayed_path.append(full_path[path_index])
                    path_index += 1
                else:
                    is_drawing_path = False
                    break

        # Rendering
        draw_grid(screen, grid, visited_cells, displayed_path)
        draw_hud(
            screen = screen,
            font = font,
            small_font = small_font,
            algo_name = name,
            status = status,
            visited_count = len(visited_cells),
            path_len = len(full_path),
            width = screen_width,
            slider = speed_slider
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()