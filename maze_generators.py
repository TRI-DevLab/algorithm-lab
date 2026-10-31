import random
from typing import Set
from grid import Grid, Coordinate


def generate_random_obstacles(grid: Grid, density: float = 0.28) -> Set[Coordinate]:
    """ 
    Randomly scatters walls across the grid based on density percentage,
    guaranteeing start and goal remain unblocked.
    """

    walls = set()

    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)

            if coord != grid.start and coord != grid.goal:
                if random.random() < density:
                    walls.add(coord)

    return walls


def generate_recursive_backtracker(grid: Grid) -> Set[Coordinate]:
    """
    Generate a perfect maze using the randomized depth-first search 
    (Recursive Backtracking) algorithm
    """

    # 1. Fill the entire grid with walls 
    walls: Set[Coordinate] = set()

    for y in range(grid.height):
        for x in range(grid.width):
            coord = (x, y)

            walls.add(coord)


    # 2. Start craving from cell (1, 1) or grid.start

    if grid.width > 2 and grid.height > 2:
        start_cell = (1, 1)
    else:
        start_cell = grid.start

    walls.discard(start_cell)

    stack = [start_cell]
    visited = {start_cell}

    while stack:                            # While the stack still has items
        cx, cy = stack[-1]

        # Move 2 cells at a time in 4 different directions
        directions = [
            (0, -2),
            (0, 2),
            (-2, 0),
            (2, 0)
        ]

        random.shuffle(directions)

        carved = False
        for dx, dy in directions:
            nx = cx + dx
            ny = cy + dy

            # Stay strictly within boundaries (leaving a 1-cell outer border)
            if (0 < nx < grid.width - 1) and (0 < ny < grid.height - 1):
                if (nx, ny) not in visited:

                    # Carve wall between current cell and next cell
                    wall_between = (cx + dx // 2, cy + dy // 2)
                    walls.discard(wall_between)
                    walls.discard((nx, ny))

                    visited.add((nx, ny))
                    stack.append((nx, ny))
                    carved = True                               # Indicates that the algorithm successfully moved forward
                    break

        if not carved:
            stack.pop()

        # 3. Always ensure start and goal are open corridors 
        for endpoints in (grid.start, grid.goal):
            walls.discard(endpoints)

            # Open at least one neighbor so that the endpoints aren't isolated
            ex, ey = endpoints
            e_neighbors = [
                (ex + 1, ey),
                (ex - 1, ey),
                (ex, ey + 1),
                (ex, ey - 1)
            ]

            for (nx, ny) in e_neighbors:
                if (0 <= nx < grid.width) and (0 <= ny < grid.height) and ((nx, ny) not in walls):
                    break
            else:
                # if all neighbors are walls, puncture one
                if ex + 1 < grid.width:
                    walls.discard((ex + 1, ey))
                elif ey + 1 < grid.height:
                    walls.discard((ex, ey + 1))

    return walls