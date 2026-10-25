from collections import deque
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


def bfs(grid: Grid) -> Generator[Tuple[str, Any], None, None]:
    """ 
    Executes the Breadth-First Search Algorithm on a given Grid.

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

        for next_node in grid.neighbors(current):   # Get neighbor cells
            if next_node not in came_from:          # avoid visiting discovered cells
                came_from[next_node] = current      # record next_node as key & previous node as value
                queue.append(next_node)             # add neighbor node to queue


    yield ("not_found", None)           # When no path/route found

if __name__ == "__main__":
    # Test Run 

    grid = Grid(
        width = 6,
        height = 6,
        start = (0,0),
        goal = (5, 5),
        walls = {(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)} 
    )

    
