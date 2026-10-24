from typing import Set, Tuple, List

Coordinate = Tuple[int, int] # Custom datatype for coordinates 

class Grid:
    def __init__(self, 
        width: int = 10, 
        height: int = 10, 
        start: Coordinate = (0, 0), 
        goal: Coordinate = None, 
        walls: Set[Coordinate] = None
    ):
        self.width = width      # width of the grid (x)
        self.height = height    # height of the grid (y)
        self.start = start      # start coordinate (x, y)

        if goal is not None:    # test if they imputed a goal coordinate (x, y)
            self.goal = goal
        else:
            self.goal = (width - 1, height - 1)     # if not imputed assign a predetermined coordinate

        if walls is not None:       # test if they imputed a wall coordinates
            self.walls = walls
        else:
            self.walls = set()      # if no imputed wall coordinate assign empty set
        
    def in_bounds(self, node: Coordinate) -> bool:
        """Check if the coordinates lie within the grid limits."""
        x, y = node
        if (x >= 0 and x < self.width) and (y >= 0 and y < self.height):
            return True

        return False

    def is_passable(self, node: Coordinate) -> bool:
        """Check if the coordinate is not a wall."""
        if node not in self.walls:
            return True

        return False

    def neighbors(self, node: Coordinate) -> List[Coordinate]: 
        """Returns connected open coordinates"""
        x, y = node

        candidates = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        valid_neighbors = []

        for next_node in candidates:
            if self.in_bounds(next_node) and self.is_passable(next_node):
                valid_neighbors.append(next_node)

        return valid_neighbors
           

    def __str__(self):
        """The Representation of The Grid."""
        col = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                coord = (x, y)
                
                if coord == self.start:
                    row.append('S')
                elif coord == self.goal:
                    row.append('E')
                elif coord in self.walls:
                    row.append('#')
                else:
                    row.append('.')

            col.append(' '.join(row))

        return '\n'.join(col)


if __name__ == "__main__":
    # Quick Test in Terminal:


    coordinate_1 = (9, 3)

    coordinate_2 = (5, 6)

    coordinate_3 = (19, 2)

    grid_1 = Grid(
        15, 
        8, 
        (2, 4), 
        (9, 6), 
        {(5, 5), (5, 6), (5, 7), (6, 7), (6, 8)})

    print("Terminal preview of the grid:")
    print(grid_1)

    print()

    print(f"Is {coordinate_1} in Grid_1: {grid_1.in_bounds(coordinate_1)}")
    print(f"Is {coordinate_1} passable in Grid_1: {grid_1.is_passable(coordinate_1)}")
    print(f"Next pathways of coordinate: {coordinate_1} are {grid_1.neighbor(coordinate_1)}")

    print()

    print(f"Is {coordinate_2} in Grid_1: {grid_1.in_bounds(coordinate_2)}")
    print(f"Is {coordinate_2} passable in Grid_1: {grid_1.is_passable(coordinate_2)}")
    print(f"Next pathways of coordinate: {coordinate_2} are {grid_1.neighbor(coordinate_2)}")

    print()

    print(f"Is {coordinate_3} in Grid_1: {grid_1.in_bounds(coordinate_3)}")
    print(f"Is {coordinate_3} passable in Grid_1: {grid_1.is_passable(coordinate_3)}")
    print(f"Next pathways of coordinate: {coordinate_3} are {grid_1.neighbor(coordinate_3)}")