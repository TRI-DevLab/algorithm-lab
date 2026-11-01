from sys import exit
import pygame
from grid import Grid, Coordinate
from algorithms import bfs, dfs, astar, dijkstra
from maze_generators import generate_random_obstacles, generate_recursive_backtracker

# Grid Dimensions
grid_w = 17
grid_h = 13
hud_height = 85     # To make room for the metrics, hotkey and slider
divider_width = 12

# Color (Chromonyms.com)
grid_line_color = (200, 200, 200)   # Light Grey - walkable ground (cost 1)
bg_color = (255, 255, 255)          # White
start_color = (40, 167, 69)         # Green
goal_color = (255, 0, 0)            # Red
wall_color = (52, 58, 64)           # Onyx
path_color = (255, 213, 79)         # Mustard
mud_color = (181, 136, 99)          # Camel/ Light Brown - Mud/ swamp terrain (cost 5)

# Frontier Colors
visited_L_color = (144, 202, 249)   # Blue - (Single View & Left dual View)
visited_R_color = (206, 147, 216)   # Purple - (Right dual View)

# Head Up Display (HUD) Styling
hud_bg_color = (33, 37, 41)         # Dark Charcoal Header
hud_text_color = (248, 249, 250)    # Ghost White
hud_accent_color = (255, 193, 7)    # Amber

divider_color = (73, 80, 87)

status_searching = (100, 181, 246)  # Maya Blue
status_found = (129, 199, 132)      # Pistachio 
status_failed = (239, 83, 80)       # Sunset Orange

# Sliders Colors
slider_track_color = (73, 80, 87)   # Grey
slider_fill_color = (0, 123, 255)   # Blue
slider_knob_color = (248, 249, 250) # Ghost White

algorithms = {                                                   
    "1": ("BFS", bfs),
    "2": ("DFS", dfs),
    "3": ("A*", astar),
    "4": ("Dijkstra", dijkstra)
}

right_key_map = {
    pygame.K_7: "1",
    pygame.K_8: "2",
    pygame.K_9: "3",
    pygame.K_0: "4"
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
        screen.blit(label_surf, (self.rect.right + 10, self.rect.y - 2))


def get_grid_pos(mouse_pos, dual_view: bool, cell_size: int, grid_px_w: int, total_width: int) -> Coordinate: 
    """Convert pixel coordinates to grid (x, y) coordinates based on view mode."""
    pixel_x, pixel_y = mouse_pos

    if pixel_y < hud_height:
        return (-1, -1)

    grid_x = pixel_x // cell_size                       # Converting pixels at pos x into x-coordinate
    grid_y = (pixel_y - hud_height) // cell_size        # converting pixels at pos y into y-coordinate - subtract HUD height 

    # Depending on view mode the value of grid_x changes 
    if not dual_view:
        if 0 <= pixel_x < grid_px_w:
            return (grid_x, grid_y)
        return (-1, -1)
    else:
        if 0 <= pixel_x < grid_px_w:
            return (grid_x, grid_y)
        elif (grid_px_w + divider_width) <= pixel_x < total_width:
            grid_x = (pixel_x - grid_px_w - divider_width) // cell_size
            return (grid_x, grid_y)
        return (-1, -1)



def draw_hud(
        screen: pygame.Surface, 
        font: pygame.font.Font,
        small_font: pygame.font.Font, 
        dual_view: bool,
        total_width: int,
        grid_px_w: int,

        left_algo: str,
        left_stat: str,
        left_visited: int,
        left_path_len: int,
        left_cost: int,

        right_algo: str,
        right_stat: str,
        right_visited: int,
        right_path_len: int, 
        right_cost: int,

        slider: Slider
    ):
    """Renders The Head Up Display Dashboard"""

    # HUD background banner 
    pygame.draw.rect(screen, hud_bg_color, pygame.Rect(0, 0, total_width, hud_height))
    pygame.draw.line(screen, divider_color, (0, hud_height - 1), (total_width, hud_height -1), 2)

    # Determine status color
    def get_status_color(status):
        if status == "SEARCHING...":
            return status_searching
        if status == "PATH FOUND":
            return status_found
        if status == "NO PATH":
            return status_failed

        return hud_text_color

    
    if not dual_view:
        # Single-view HUD

        title = font.render(f"Algo: {left_algo}", True, hud_accent_color)
        stat = font.render(f"Status: {left_stat}", True, get_status_color(left_stat))
        visited = font.render(f"Visited: {left_visited}", True, hud_text_color)
        hops = font.render(f"Hops: {left_path_len}", True, hud_text_color)
        cost = font.render(f"Cost: {left_cost}", True, hud_accent_color if left_cost > 0 else hud_text_color)

        screen.blit(title, (16, 10))
        screen.blit(stat, (140, 10))
        screen.blit(visited, (310, 10))
        screen.blit(hops, (430, 10))
        screen.blit(cost, (520, 10))

        # Controls helper
        helper_text = "[V] Dual View | [1-4] Algo | [Space] Run | [M] Maze | [R] Random | [W+Click] Mud | [C] Clear"
        helper_surf = small_font.render(helper_text, True, (173, 181, 189))
        screen.blit(helper_surf, (16, 38))

    else:
        # Dual-view HUD

        # Left Side
        l_title = font.render(f"[L] {left_algo}", True, (144, 202, 249))
        l_stat = small_font.render(f"Status: {left_stat}", True, get_status_color(left_stat))
        l_metrics = small_font.render(f"Visited: {left_visited} | Hops: {left_path_len} | Cost: {left_cost}", True, hud_text_color)

        screen.blit(l_title, (16, 8))
        screen.blit(l_stat, (16, 28))
        screen.blit(l_metrics, (16, 44))


        # Right Side
        right_x = grid_px_w + divider_width + 16

        r_title = font.render(f"[R] {right_algo}", True, (206, 147, 216))
        r_stat = small_font.render(f"Status: {right_stat}", True, get_status_color(right_stat))
        r_metrics = small_font.render(f"Visited: {right_visited} | Hops: {right_path_len} | Cost: {right_cost}", True, hud_text_color)

        screen.blit(r_title, (right_x, 8))
        screen.blit(r_stat, (right_x, 28))
        screen.blit(r_metrics, (right_x, 44))

        # Control helper
        helper_text = "[V] Single View | [1-4] Left Algo | [7-0] Right Algo | [Space] Run | [M] Maze | [R] Random | [C] Clear"
        helper_surf = small_font.render(helper_text, True, (173, 181, 189))
        screen.blit(helper_surf, (16, 64))

    # Draw Slider
    slider.draw(screen, small_font)


def draw_grid(
        screen: pygame.surface, 
        grid: Grid,
        visited: set,
        path: list,
        offset_x: int,
        cell_size: int,
        visited_color: tuple
    ):           
    """Draw Grid lines, cells, start, goal, mud, and walls."""

    grid_px_w = grid.width * cell_size
    grid_px_h = grid.height * cell_size


    # Base Terrain (Mud and Empty)
    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)
            rect = pygame.Rect(
                x * cell_size + offset_x,
                y * cell_size + hud_height, 
                cell_size,
                cell_size
            )

            if coord in grid.weights:
                pygame.draw.rect(screen, mud_color, rect)

    # Visited Cells
    for coord in visited:
        # coord[0] = x and coord[1] = y
        if coord != grid.start and coord != grid.goal:
            rect = pygame.Rect(             # placing the position of path at pixel position
                coord[0] * cell_size + offset_x,
                coord[1] * cell_size + hud_height,
                cell_size,
                cell_size
            )

            # Tint mud cells slightly darker when visited
            if coord in grid.weights:
                cell_color = (110, 180, 220)
            else:
                cell_color = visited_color

            pygame.draw.rect(screen, cell_color, rect)

    # Shortest Path Cells 
    for coord in path:
        # coord[0] = x and coord[1] = y
        if coord != grid.start and coord != grid.goal:
            rect = pygame.Rect(             # placing the position of path at pixel position
                coord[0] * cell_size + offset_x,
                coord[1] * cell_size + hud_height,
                cell_size,
                cell_size
            )

            pygame.draw.rect(screen, path_color, rect)


    # Special Cells (Start, Goal and Walls)
    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)

            rect = pygame.Rect(         # placing the position of rectangle at pixel position
                x * cell_size + offset_x, 
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
            (x * cell_size + offset_x, hud_height),                                 # start position - Top
            (x * cell_size + offset_x, hud_height + grid_px_h)        # end position - bottom
        )


    for y in range(grid.height + 1):                    # Horizontal lines 
        pygame.draw.line(
            screen,
            grid_line_color,
            (offset_x, hud_height + y * cell_size),                         # start position - left
            (offset_x + grid_px_w, hud_height + y * cell_size)              # end position - right
        )



def main():

    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont("Consolas", 15, bold = True)
    small_font = pygame.font.SysFont("Consolas", 12)


    # initialize Grid Modal
    grid = Grid(
        width = grid_w,
        height = grid_h,
        start = (1, 1),
        goal = (grid_w - 2, grid_h - 2),
    ) 

    # View Mode State 
    dual_view = False               # Start in Single view

    # Used to determine the size of the screen depending on the View Mode
    def calc_window_geometry(is_dual):
        if is_dual:
            cell_size = 30                  # For Dual View
        else:
            cell_size = 40                  # Single View

        pixel_width = grid_w * cell_size        # Screen width in pixels
        pixel_height = grid_h * cell_size       # screen height in pixels 

        if is_dual:
            total_width = (pixel_width * 2 + divider_width)     # total width in dual view mode
        else:
            total_width = pixel_width                           # total width stays the same in single view mode

        total_height = pixel_height + hud_height                # total height 

        return cell_size, pixel_width, total_width, total_height        # Returns multiple items that will be later used for processing


    # Unpack Values for use in programs 
    cell_size, grid_px_w, total_width, total_height = calc_window_geometry(dual_view)  

    # The main screen
    screen = pygame.display.set_mode((total_width, total_height)) 

    # Captions 
    pygame.display.set_caption('Algorithm Lab')

    # For Frame Speed  
    clock = pygame.time.Clock()

    # Initialize dynamic speed slider: (placed at x = 16, y = 58)
    speed_slider = Slider(
        x = total_width - 190,
        y = 60 if dual_view else 58,
        width = 110,
        height = 10, 
        min_val = 1,
        max_val = 15,
        initial_val = 1
    )


    # Left / Primary Algorithm (Default: BFS)
    left_key = "1"
    left_name, left_algo = algorithms[left_key]
    left_status = "IDLE"

    #---- Visual State trackers
    left_visited = set()                                    # Cells processed during animation (visited cells)
    left_displayed_path = []                                # The path cells that have been revealed so far
    left_full_path = []                                     # The complete path from start to goal
    left_cost = 0                                           # The Path cost (for A* and Dijkstra Algorithms)

    #---- Animation Control Variables                       
    left_generator = None                                   # Search generator 
    left_is_searching = False                               # Control for when an algorithm runs
    left_is_drawing = False                                 # Control for when anything is drawn on the grid
    left_path_index = 0
    
    
    # Right Algorithm (Default: A*)
    right_key = "3"
    right_name, right_algo = algorithms[right_key]
    right_status = "IDLE"

    #---- Visual State trackers 
    right_visited = set()
    right_displayed_path = []
    right_full_path = []
    right_cost = 0

    #---- Animation Control Variables
    right_generator = None
    right_is_searching = False
    right_is_drawing = False
    right_path_index = 0


    running = True
    while running:
        for event in pygame.event.get():
            # Quitting program
            if event.type == pygame.QUIT:
                running = False

            # Let the slider process clicks/drags regardless of simulation state
            speed_slider.handle_event(event)

            if event.type == pygame.KEYDOWN:
                is_animating = (left_is_searching or left_is_drawing or right_is_searching or right_is_drawing)

                # Toggle View Mode with [V]
                if (event.key == pygame.K_v) and (not is_animating):
                    dual_view = not dual_view
                    cell_size, grid_px_w, total_width, total_height = calc_window_geometry(dual_view)
                    screen = pygame.display.set_mode((total_width, total_height))
                    speed_slider.rect.x = total_width - 190
                    speed_slider.rect.y = 60 if dual_view else 58


                # C - Clear/ Reset 
                if event.key == pygame.K_c:
                    grid.walls.clear()
                    grid.weights.clear()

                    left_visited.clear()
                    left_displayed_path.clear()
                    left_full_path.clear()
                    left_cost = 0
                    left_is_searching = False
                    left_is_drawing = False
                    left_generator = None
                    left_status = "IDLE"

                    right_visited.clear()
                    right_displayed_path.clear()
                    right_full_path.clear()
                    right_cost = 0
                    right_is_searching = False
                    right_is_drawing = False
                    right_generator = None
                    right_status = "IDLE"

                # Maze Generation and Algorithm selection (only when idle)
                elif not is_animating:         

                    # Random Obstacle scatter 
                    if event.key == pygame.K_r:
                        grid.weights.clear()
                        grid.walls = generate_random_obstacles(grid, density = 0.28)

                    # Recursive Back-tracker Maze
                    elif event.key == pygame.K_m:
                        grid.weights.clear()
                        grid.walls = generate_recursive_backtracker(grid)

                    # Left / Single View Algorithm Selection: Key 1, 2, 3, 4
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        left_key = pygame.key.name(event.key)
                        left_name, left_algo = algorithms[left_key]
                        left_visited.clear()
                        left_displayed_path.clear()
                        left_full_path.clear()
                        left_cost = 0
                        left_status = "IDLE"

                    # Right Algorithm Selection: Key 7, 8, 9, 0 (Dual View)
                    elif dual_view and (event.key in right_key_map):
                        right_key = right_key_map[event.key]
                        right_name, right_algo = algorithms[right_key]
                        right_visited.clear()
                        right_displayed_path.clear()
                        right_full_path.clear()
                        right_cost = 0
                        right_status = "IDLE"

                    # Start Algorithm Run/ Race: Space-bar
                    elif event.key == pygame.K_SPACE:
                        left_visited.clear()
                        left_displayed_path.clear()
                        left_full_path.clear()
                        left_cost = 0
                        left_generator = left_algo(grid)
                        left_is_searching = True
                        left_status = "SEARCHING..."

                        if dual_view:
                            right_visited.clear()
                            right_displayed_path.clear()
                            right_full_path.clear()
                            right_cost = 0
                            right_generator = right_algo(grid)
                            right_is_searching = True
                            right_status = "SEARCHING..."

        # Mouse editing (only if idle and not dragging slider)
        is_animating = (left_is_searching or left_is_drawing or right_is_searching or right_is_drawing)

        if (not is_animating) and (not speed_slider.is_dragging):            # Disables Maze editing during animations and slider movement
            # Mouse Interaction
            mouse_pressed = pygame.mouse.get_pressed()              # Mouse Buttons (left, middle, right)
            keys_pressed = pygame.key.get_pressed()                 # Keyboard keys
            grid_pos = get_grid_pos(pygame.mouse.get_pos(), dual_view, cell_size, grid_px_w, total_width)         # Grid coordinate position conversion from mouse pixel position

            if grid.in_bounds(grid_pos):                    # First we confirm that the mouse is in the grid
                
                # Left mouse button
                if mouse_pressed[0]:

                    if keys_pressed[pygame.K_s]:        # s - key
                        # Move start node (coordinate)
                        if grid_pos != grid.goal:               # start node cannot override goal node 
                            grid.walls.discard(grid_pos)        # remove any walls already there
                            grid.weights.pop(grid_pos, None)    # remove any mud placed there
                            grid.start = grid_pos               # assign or update the start node (coordinate)
                    elif keys_pressed[pygame.K_g]:      # g - key
                        # Move goal node (coordinate)
                        if grid_pos != grid.start:              # goal node cannot override start node
                            grid.walls.discard(grid_pos)        # remove any walls already there
                            grid.weights.pop(grid_pos, None)    # remove any mud placed there
                            grid.goal = grid_pos                # assign or update the goal node (coordinate)
                    elif keys_pressed[pygame.K_w]:
                        # paint weighted mud cell (cost = 5)
                        if grid_pos != grid.start and grid_pos != grid.goal:
                            grid.walls.discard(grid_pos)
                            grid.weights[grid_pos] = 5
                    else:
                        # Place a wall
                        if (grid_pos != grid.start) and (grid_pos != grid.goal): # Cannot override start or goal node
                            grid.weights.pop(grid_pos, None)        # Discard mud when wall placed on top of it 
                            grid.walls.add(grid_pos)        # place wall node in set of walls

                # Right mouse button - Erase walls and Mud
                elif mouse_pressed[2]:
                    grid.walls.discard(grid_pos)
                    grid.weights.pop(grid_pos, None)


        # Search exploration animation
        # 1. Step left Search
        if left_is_searching and left_generator:
            speed = speed_slider.val
            for _ in range(speed):
                try:                                                    # Works as generator eventually has no more value and raises error       
                    event_type, data, cost = next(left_generator)
                    if event_type == "visiting":
                        left_visited.add(data)
                    elif event_type == "path":
                        left_full_path = data
                        left_cost = cost
                        left_is_searching = False
                        left_is_drawing = True
                        left_path_index = 0
                        left_status = "PATH FOUND"
                        break
                    elif event_type == "not_found":
                        left_is_searching = False
                        left_status = "NO PATH FOUND"
                        break
                except StopIteration:
                    left_is_searching = False
                    if not left_full_path:
                        left_status = "NO PATH FOUND"
                    break

        # Path Animation (scales with slider rate as well)
        elif left_is_drawing:
            path_speed = max(1, speed_slider.val // 2)
            for _ in range(path_speed):
                if left_path_index < len(left_full_path):
                    left_displayed_path.append(left_full_path[left_path_index])
                    left_path_index += 1
                else:
                    left_is_drawing = False
                    break


        # 2. Step Right Search (only if dual view active)
        if dual_view:
            if right_is_searching and right_generator:
                speed = speed_slider.val
                for _ in range(speed):
                    try:                                                    # Works as generator eventually has no more value and raises error       
                        event_type, data, cost = next(right_generator)
                        if event_type == "visiting":
                            right_visited.add(data)
                        elif event_type == "path":
                            right_full_path = data
                            right_cost = cost
                            right_is_searching = False
                            right_is_drawing = True
                            right_path_index = 0
                            right_status = "PATH FOUND"
                            break
                        elif event_type == "not_found":
                            right_is_searching = False
                            right_status = "NO PATH FOUND"
                            break
                    except StopIteration:
                        right_is_searching = False
                        if not right_full_path:
                            right_status = "NO PATH FOUND"
                        break

            # Path Animation (scales with slider rate as well)
            elif right_is_drawing:
                path_speed = max(1, speed_slider.val // 2)
                for _ in range(path_speed):
                    if right_path_index < len(right_full_path):
                        right_displayed_path.append(right_full_path[right_path_index])
                        right_path_index += 1
                    else:
                        right_is_drawing = False
                        break



        # Render Loop
        screen.fill(bg_color)

        if not dual_view:
            # Single View Grid
            draw_grid(
                screen, 
                grid, 
                left_visited, 
                left_displayed_path,
                offset_x = 0,
                cell_size = cell_size,
                visited_color = visited_L_color
            )
        else:
            # Dual View Grids & Dividers
            draw_grid(
                screen,
                grid,
                left_visited,
                left_displayed_path,
                offset_x = 0,
                cell_size = cell_size,
                visited_color = visited_L_color
            )

            pygame.draw.rect(
                screen, 
                divider_color, 
                pygame.Rect(grid_px_w, hud_height, divider_width, grid_h * cell_size)
            )

            right_offset = grid_px_w + divider_width

            draw_grid(
                screen,
                grid,
                right_visited,
                right_displayed_path,
                offset_x = right_offset,
                cell_size = cell_size,
                visited_color = visited_R_color
            )


        # Draw Dynamic HUD
        draw_hud(
            screen = screen,
            font = font,
            small_font = small_font,
            dual_view = dual_view,
            total_width = total_width,
            grid_px_w = grid_px_w,
            left_algo = left_name,
            left_stat = left_status,
            left_visited = len(left_visited),
            left_path_len = len(left_full_path),
            left_cost = left_cost,
            right_algo = right_name,
            right_stat = right_status,
            right_visited = len(right_visited),
            right_path_len = len(right_full_path),
            right_cost = right_cost,
            slider = speed_slider
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()