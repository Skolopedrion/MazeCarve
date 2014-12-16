import random

N, S, E, W = 0b0001, 0b0010, 0b0100, 0b1000

OPPOSITE = {
    N: S,
    S: N,
    E: W,
    W: E
}

intersection = {
    N | S | E | W: chr(9532),
    N | S | E: chr(9500),
    N | S | W: chr(9508),
    S | E | W: chr(9516),
    N | E | W: chr(9524),
    N | S: chr(9474),
    E | W: chr(9472),
    S | E: chr(9484),
    N | E: chr(9492),
    S | W: chr(9488),
    N | W: chr(9496),
    N: chr(9474),
    S: chr(9474),
    E: chr(9472),
    W: chr(9472),
    0: chr(32)
}

class MazeCell:
    def __init__(self, fill, x, y):
        self.fill = fill
        self.x, self.y = x, y
        self.is_intact = True
        self.connection = {direction: True for direction in (N, S, E, W)}
        
    def between(self, other):
        if other.y < self.y:
            return N
        elif other.y > self.y:
            return S
        elif other.x > self.x:
            return E
        elif other.x < self.x:
            return W
        else:
            raise ValueError("'other' is not next to the cell.")

    def connect(self, other):
        self.is_intact, other.is_intact = False, False

        self.connection[self.between(other)] = False
        other.connection[OPPOSITE[self.between(other)]] = False

    def coordinates(self):
        return self.x, self.y

    def __repr__(self):
        return "<MazeCell on ({x}, {y})>".format(
            x=self.x, y=self.y
        )

    def __bool__(self):
        return self.fill


class Maze(list):
    def __init__(self, width, height, rooms=0):
        self.width, self.height = width//2, height//2
        self.rooms = []
        maze = [[MazeCell(True, ix, iy) for ix in range(self.width)]
                                        for iy in range(self.height)]
        super().__init__(maze)

        cells = []
        current = self.random_cell()
        visited = 1

        while visited < (self.height * self.width):
            intact = [c for c in self.neighbors(current) if c.is_intact]
            if intact:
                cell = random.choice(intact)
                current.connect(cell)
                cells.append(current)
                current = cell
                visited += 1

            else:
                current = cells.pop()

        cell_matrix = [[MazeCell(True, x, y) for x in range(self.width * 2 + 1)] for y in range(self.height * 2 + 1)]
        cell_stack = [self[x, y] for y in range(self.height) for x in range(self.width)]
        for cell in cell_stack:
            x = cell.x * 2 + 1
            y = cell.y * 2 + 1
            cell_matrix[y][x] = MazeCell(False, x, y)

            if not cell.connection[N] and y > 0:
                cell_matrix[y - 1][x] = MazeCell(False, x, y-1)
            if not cell.connection[S] and y + 1 < self.height:
                cell_matrix[y + 1][x] = MazeCell(False, x, y+1)
            if not cell.connection[E] and x + 1 < self.width:
                cell_matrix[y][x + 1] = MazeCell(False, x+1, y)
            if not cell.connection[W] and x > 0:
                cell_matrix[y][x - 1] = MazeCell(False, x-1, y)

        super().__init__(cell_matrix)
        self.create_random_rooms(rooms)

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            x, y = index
            self[y][x] = value
        else:
            return super().__setitem__(index, value)

    def __getitem__(self, index):
        if isinstance(index, tuple):
            x, y = index
            return self[y][x]
        else:
            return super().__getitem__(index)

    def __repr__(self):
        def str_cell(c):
            conns = 0b0000
            for i, neighbor in enumerate(self.neighbors(c, keep_position=True)):
                conns |= bool(neighbor) and bool(c) * (N, S, E, W)[i]
            return intersection[conns]

        display = ''
        for line in self:
            for cell in line:
                display += str_cell(cell)
            display += '\n'
        return display

    def neighbors(self, cell, keep_position=False):
        x, y = cell.x, cell.y
        n = []
        for new_x, new_y in [(x, y - 1), (x, y + 1), (x + 1, y), (x - 1, y)]:
            try:
                if (new_x < 0) or (new_y < 0):
                    raise IndexError
                n.append(self[new_x, new_y])
            except IndexError:
                if keep_position:
                    n.append(None)
        return n

    def random_cell(self, exclude_borders=False):
        x = random.randrange(self.width)
        y = random.randrange(self.height)
        while len(self.neighbors(self[x, y])) < 4 and exclude_borders:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
        return self[x, y]

    def create_random_rooms(self, rooms):
        spacing = 2

        room_coords = lambda rx, ry: (
            (
                rx * ((self.width - (spacing * (self.width // 4 + 1))) // 4) + spacing,
                ry * ((self.height - (spacing * (self.height // 4 + 1))) // 4) + spacing
            ),
            (
                (rx + 1) * ((self.width - (spacing * (self.width // 4 + 1))) // 4) + spacing,
                (ry + 1) * ((self.height - (spacing * (self.height // 4 + 1))) // 4) + spacing
            )
        )

        """eventual_rooms = [
            (Room(*room_coords(x, y)), print(room_coords(x, y)))
            for y in range(4)
            for x in range(4)
        ]

        for room in random.sample([r[0] for r in eventual_rooms], rooms):
            for x, y in room:
                self[x, y] = MazeCell(False, x, y)
            self.rooms.append(room)"""


class Room(list):
    def __init__(self, pos1, pos2):
        x1, y1, x2, y2 = pos1 + pos2
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        self.pos1, self.pos2 = (x1, y1), (x2, y2)
        self.width, self.height = abs(x1-x2), abs(y1-y2)
        coordinates = []

        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                coordinates.append((x, y))
        super().__init__(coordinates)

    def around(self, degree):
        pos1 = (self.pos1[0] - degree,
                self.pos1[1] - degree)
        pos2 = (self.pos2[0] + degree,
                self.pos2[1] + degree)
        return set(Room(pos1, pos2))

if __name__ == '__main__':
    import sys
    width, height = map(int, sys.argv[1:])
    print(Maze(width, height))