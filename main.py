class BoardException(Exception):
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы попали за границы игрового поля!"
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"
class BoardShipException(BoardException):
    def __str__(self):
        return "Недопустимое место для корабля"

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
class Ship:
    def __init__(self, start, length, orient):
        self.start = start
        self.length = length
        self.orient = orient
        self.lives = length

    def coord(self):
        ship_coord = []
        for i in range(self.length):
            coord_x = self.start.x
            coord_y = self.start.y

            if self.orient == 'v':
                coord_x += i

            elif self.orient == 'h':
                coord_y += i

            ship_coord.append(Dot(coord_x, coord_y))

        return ship_coord

class Board:
    def __init__(self, size):
        self.size = size
        self.field = [["o"] * self.size for i in range(0, self.size)]
        self.busy = []
        self.ships = []
        self.count = 0

    def __str__(self):
        game_field = "  |"
        for i in range(self.size):
            game_field += f" {i} |"
        for i, value in enumerate(self.field):
            game_field += f"\n{i} | " + " | ".join(value) + " |"
        return game_field

    def add_ship(self, ship):
        for i in ship.coord():
            if self.out_board(i):
                raise BoardOutException()
            elif i in self.busy:
                raise BoardShipException
            self.field[i.x][i.y] = "■"
            self.busy.append(i)

        self.contour(ship, False)
        self.ships.append(ship)

    def out_board(self, i):
        return not ((0 <= i.x < self.size) and (0 <= i.y < self.size))

    def contour(self, ship, show):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for i in ship.coord():
            for ix, iy in near:
                cur = Dot(i.x + ix, i.y + iy)
                if not (self.out_board(cur)) and cur not in self.busy:
                    if show:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    def board_clear(self):
        self.busy = []
    def shot(self, sht_coord):
        if self.out_board(sht_coord):
            raise BoardOutException()

        if sht_coord in self.busy:
            raise BoardUsedException()

        self.busy.append(sht_coord)
        for ship in self.ships:
            if sht_coord in ship.coord():

                ship.lives -= 1

                self.field[sht_coord.x][sht_coord.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, True)
                    print("Корабль убит!")
                    return False
                else:
                    print("Корабль ранен!")
                    print("Осталось попаданий:", ship.lives)
                    return True

        self.field[sht_coord.x][sht_coord.y] = "."
        print("Мимо!")
        return False

class Player:
    def __init__(self, board):
        self.board = board



b = Board(8)
ship = Ship(Dot(2,3), 4, 'v')


b.add_ship(ship)
print(b)
b.board_clear()
b.shot(Dot(2,2))
print(b)
b.shot(Dot(2,3))
print(b)
b.shot(Dot(3,3))
print(b)
b.shot(Dot(4,3))
print(b)
b.shot(Dot(5,3))
print(b)
