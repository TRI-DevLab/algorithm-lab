from collections import deque
import heapq
from grid import Grid, Coordinate
from typing import Dict, List, Optional, Tuple, Any, Generator

def reconstruct_path(
        came_from: Dict[Coordinate, Optional[Coordinate]],
        start: Coordinate,
        goal: Coordinate
) -> List[Coordinate]:
    """Reconstructs the shortest path from start to goal - by tracing came_from backwards."""
    current = goal          # working backwards so its starts from end
    path = []

    while current is not None:              # While the variable current is not empty = start 
        path.append(current)                # add to path from the goal to the start
        current = came_from.get(current)    # collect the previous node (value) from current node (key)

    path.reverse() # reverse so the start is first and goal is last

    if path and path[0] == start:           # check if empty or if start is the first index
        return path
    else:
        return []

def manhattan_distance(a: Coordinate, b: Coordinate) -> int:
    """Heuristic function h(n) for grid path-finding."""

    x_distance = abs(a[0] - b[0])       # horizontal distance
    y_distance = abs(a[1] - b[1])       # vertical distance

    return x_distance + y_distance      # estimated distance 

def bfs(grid: Grid) -> Generator[Tuple[str, Any], None, None]:
    """ 
    Executes the Breadth-First Search Algorithm (FIFO Queue) on a given Grid.

    Yields: 
    - ("visiting", Coordinate): The node (cell / coordinates) currently being processed
    - ("path", List[Coordinate]): The reconstructed shortest path from start to goal
    - ("not_found", None): Indicates to path exits (goal unreachable)
    """
    start = grid.start
    goal = grid.goal

    queue = deque([start])      # FIFO queue  front - [(0, 1)] - back

    came_from: Dict[Coordinate, Optional[Coordinate]] = {             
        start: None             # Next node: Previous node
    }

    while queue:                # Loop until empty

        current = queue.popleft()       # Remove next cell
        yield ("visiting", current)     # Cell currently being the processed

        if current == goal:     # Check wether goal was found
            path = reconstruct_path(came_from, start, goal)     # reconstructs path from start - goal when goal found
            yield ("path", path)        # return shortest route
            return                      # used to exit generator

        for neighbor in grid.neighbors(current):   # Get neighbor cells
            if neighbor not in came_from:          # avoid visiting discovered cells
                came_from[neighbor] = current      # record next_node as key & previous node as value
                queue.append(neighbor)             # add neighbor node to queue


    yield ("not_found", None)           # When no path/route found

def dfs(grid: Grid) -> Generator[Tuple[str, Any], None, None]:
    """ Executes the Depth First Search Algorithm (LIFO stack) for a given Grid
    """
    start = grid.start
    goal = grid.goal

    stack = [start]         # Stack (FILO) the cell placed on top is the first removed

    came_from: Dict[Coordinate, Optional[Coordinate]] = {
        start: None
    }

    visited = set()                 # tracks processed cells 

    while stack:                    # Loop until empty 
        current = stack.pop()       # Removes the most recently added cell

        if current in visited:      # if cell being processed already been processed (skips next steps)
            continue

        visited.add(current)
        yield ("visiting", current)

        if current == goal:         # Once goal found path is reconstructed and generated (May not be shortest path)
            path = reconstruct_path(came_from, start, goal)
            yield ("path", path)
            return 

        for neighbor in grid.neighbors(current):        # used to find neighbors and add to stack for processing 
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    yield ("not_found", None)       # when no route found

def astar(grid: Grid) -> Generator[Tuple[str, Any], None, None]:

    start = grid.start
    goal = grid.goal

    # Priority Queue stores: (f_score, tie_breaker_counter, node)
    counter = 0
    open_heap = []          # Stores cells waiting to be explored ordered by priority 
    # inserts entry into a min_heap so that entry with smallest priority is popped first
    heapq.heappush(open_heap, (manhattan_distance(start, goal), counter, start))      

    came_from: Dict[Coordinate, Optional[Coordinate]] = {           # for route reconstruction 
        start: None
    }

    g_score: Dict[Coordinate, int] = {                              # stores the best known actual cost
        start: 0
    }

    closed_set = set()      # Records cells already being processed by A*

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current in closed_set:           # Skips entries for cells already processed
            continue
        closed_set.add(current)
        yield ("visiting", current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ("path", path)
            return

        tentative_g = g_score[current] + 1      # the cost of reaching a neighbor

        for neighbor in grid.neighbors(current):
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbor, goal)
                counter += 1
                heapq.heappush(open_heap, (f_score, counter, neighbor))

    yield ("not_found", None)

if __name__ == "__main__":
    # Test Run 

    grid = Grid(
        width = 6,
        height = 6,
        start = (0,0),
        goal = (5, 5),
        walls = {(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)} 
    )
    
    print("======= Test Gid =======\n")

    print(grid)
