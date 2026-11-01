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


def calculate_path_cost(grid, path):
    """Calculates the total weighted movement cost of a path (excluding the start cell)."""

    if not path or len(path) <= 1:
        return 0

    return sum(grid.cost(node) for node in path[1:])


def bfs(grid: Grid) -> Generator[Tuple[str, Any, Optional[int]], None, None]:
    """ 
    Executes the Breadth-First Search Algorithm (FIFO Queue) on a given Grid.

    Yields: 
    - ("visiting", Coordinate): The node (cell / coordinates) currently being processed
    - ("path", List[Coordinate]): The reconstructed shortest path from start to goal
    - ("not_found", None): Indicates no path exits (goal unreachable)

    Treats all passable cells with uniform cost of 1
    """
    start = grid.start
    goal = grid.goal

    queue = deque([start])      # FIFO queue  front - [(0, 1)] - back

    came_from: Dict[Coordinate, Optional[Coordinate]] = {             
        start: None             # Next node: Previous node
    }

    while queue:                # Loop until empty

        current = queue.popleft()               # Remove next cell
        yield ("visiting", current, None)       # Cell currently being the processed

        if current == goal:     # Check wether goal was found
            path = reconstruct_path(came_from, start, goal)     # reconstructs path from start - goal when goal found
            total_cost = calculate_path_cost(grid, path)        # total cost of path
            yield ("path", path, total_cost)                    # return shortest route
            return                      # used to exit generator

        for neighbor in grid.neighbors(current):   # Get neighbor cells
            if neighbor not in came_from:          # avoid visiting discovered cells
                came_from[neighbor] = current      # record next_node as key & previous node as value
                queue.append(neighbor)             # add neighbor node to queue


    yield ("not_found", None, 0)           # When no path/route found


def dfs(grid: Grid) -> Generator[Tuple[str, Any, Optional[int]], None, None]:
    """ 
    Executes the Depth First Search Algorithm (LIFO stack) for a given Grid.

    Yields:
    - ("visiting", Coordinate): The node (cell / coordinate) currently being processed.
    - ("path", List[Coordinate]): The reconstructed shortest path from start to goal.
    - ("not_found", None): Indicates no path exists (goal unreachable)

    Explores as deep as possible along a branch.
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
        yield ("visiting", current, None)

        if current == goal:         # Once goal found path is reconstructed and generated (May not be shortest path)
            path = reconstruct_path(came_from, start, goal)
            total_cost = calculate_path_cost(grid, path)
            yield ("path", path, total_cost)
            return 

        for neighbor in grid.neighbors(current):        # used to find neighbors and add to stack for processing 
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    yield ("not_found", None, 0)       # when no route found


def astar(grid: Grid) -> Generator[Tuple[str, Any, Optional[int]], None, None]:
    """
    Executes the A* Search Algorithm (Priority Queue + Manhattan Heuristic) for a given grid.
    It combines cumulative cost with g(n) with Manhattan heuristics h(n).
    Takes Weighted Terrain into account while directing exploration towards the goal.
    """
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
        yield ("visiting", current, None)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ("path", path, g_score[goal])
            return

        tentative_g = g_score[current] + 1      # the cost of reaching a neighbor

        for neighbor in grid.neighbors(current):
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbor, goal)
                counter += 1
                heapq.heappush(open_heap, (f_score, counter, neighbor))

    yield ("not_found", None, 0)


def dijkstra(grid: Grid) -> Generator[Tuple[str, Any, Optional[int]], None, None]:
    """
    Executes Dijkstra's Algorithm which expands the lowest-cost nodes first using cumulative cost g(n).
    It guarantees the lowest total weight route on a non-negative weighted graph.
    """
    start = grid.start
    goal = grid.goal
    counter = 0
    open_heap = []
    heapq.heappush(open_heap, (0, counter, start))

    came_from: Dict[Coordinate, Optional[Coordinate]] = {
        start: None
    }

    cost_so_far: Dict[Coordinate, int] = {
        start: 0
    }

    closed_set = set()

    while open_heap:                # while the heap is not empty
        current_cost, _, current = heapq.heappop(open_heap)

        if current in closed_set:
            continue
        closed_set.add(current)
        yield ("visiting", current, None)

        if current == grid.goal:
            path = reconstruct_path(came_from, start, goal)
            yield ("path", path, cost_so_far[goal])
            return

        for neighbor in grid.neighbors(current):
            new_cost = cost_so_far[current] + grid.cost(neighbor)
            if (neighbor not in cost_so_far) or (new_cost < cost_so_far[neighbor]):
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                counter += 1
                heapq.heappush(open_heap, (new_cost, counter, neighbor))

    yield("not_found", None, 0)
    

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
