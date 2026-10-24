from collections import deque
from grid import Grid

def reconstruct_path(
        came_from,
        start,
        goal
):

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


def bfs(grid):

    start = grid.start
    goal = grid.goal

    queue = deque([start])      # FIFO queue  front - [(0, 1)] - back
    came_from = {             
        start: None             # Next node: Previous node
    }
    visited_order = []          # cells removed from queue and processed 

    found = False               # Initialized whether goal been found

    while queue:                # Loop until empty

        current = queue.popleft()       # Remove next cell
        visited_order.append(current)   # record the processed cell 

        if current == goal:     # Check wether goal was found
            found = True 
            break

        for next_node in grid.neighbors(current):   # Get neighbor cells
            if next_node not in came_from:          # avoid visiting discovered cells
                came_from[next_node] = current      # record next_node as key & previous node as value
                queue.append(next_node)             # add neighbor node to queue

            
    if found:
        path = reconstruct_path(came_from, start, goal)
        return path, visited_order

    return [], visited_order

if __name__ == "__main__":
    # Test Run 

    grid = Grid(
        width = 6,
        height = 6,
        start = (0,0),
        goal = (5, 5),
        walls = {(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)} 
    )

    path, visited = bfs(grid)
    print(grid)
    print()
    print(f"Total cells explored: {len(visited)}")
    print("Path found:", path if path else "No Path found")
