# Grid 

class Grid:
    def __init__(self, 
        width = 10, 
        height = 10, 
        start = (0, 0), 
        goal = None, 
        walls = None
    ):
        self.width = width      # width of the grid (x)
        self.height = height    # height of the grid (y)
        self.start = start      # start coordinate (x, y)
        if goal is not None:    # test if they imputed a goal coordinate (x, y)
            self.goal = goal
        else:
            self.goal = (width - 1, height - 1)     # if not imputed assign a predetermined coordinate

        if walls is not None:      # test if they imputed a wall coordinates
            self.walls = walls
        else:
            self.walls = set()      # if no imputed wall coordinate assign empty set
        

           

    def __str__(self):

        grid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                if (j, i) == self.start:
                    row.append('S')
                elif (j, i) == self.goal:
                    row.append('E')
                elif (j, i) in self.walls:
                    row.append('#')
                else:
                    row.append('.')
            grid.append(''.join(row))
        return '\n'.join(grid)

if __name__ == "__main__":

    grid_1 = Grid(10, 10, (0,0), (9,9), {(3,2), (3,3), (3,4), (3,5), (4,5)})

    grid_2 = Grid(15, 8, (0,2), (7,7), {(3,5), (4,5), (4,6), (4,7), (3,7)})

    print(grid_1)
    print()
    print(grid_2)