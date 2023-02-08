from random import randint


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

    def __repr__(self):
        return f"({self.x}, {self.y})"


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

            if self.orient == 0:
                coord_x += i

            elif self.orient == 1:
                coord_y += i

            ship_coord.append(Dot(coord_x, coord_y))

        return ship_coord


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.field = [["o"] * self.size for i in range(0, self.size)]
        self.busy = []
        self.ships = []
        self.count = 0
        self.hid = hid

    def __str__(self):
        game_field = "  |"
        for i in range(self.size):
            game_field += f" {i} |"
        for i, value in enumerate(self.field):
            game_field += f"\n{i} | " + " | ".join(value) + " |"
        if self.hid:
            game_field = game_field.replace("■", "o")
        return game_field

    def add_ship(self, ship):
        for i in ship.coord():
            if self.out_board(i) or i in self.busy:
                raise BoardShipException
        for i in ship.coord():
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
    def __init__(self, board, enemy, size):
        self.size = size
        self.board = board
        self.enemy = enemy

    def ask(self, ask_type=None, leght=None):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self, ask_type=None, lenght=None):
        d = Dot(randint(0, self.size), randint(0, self.size))
        print(f"Ход компьютера: {d.x} {d.y}")
        return d


class User(Player):
    def ask(self, ask_type=None, lenght=None):
        while True:
            if ask_type == None:
                cords = input("Ваш ход: ").split()
            else:
                cords = input(f"Укажите начальную точку размещения корабля(размер - {lenght}): ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x, y)


class Game:
    def __init__(self, size, gen_type):
        self.size = size
        self.gen_type = gen_type
        pl = self.random_board(self.gen_type)
        co = self.random_board(1)
        co.hid = True

        self.ai = AI(co, pl, size - 1)
        self.us = User(pl, co, size - 1)

    def random_board(self, type):
        board = None
        while board is None:
            board = self.place(type)
        return board

    def place(self, gen_type):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                if gen_type == 1:
                    ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                else:
                    st_coord = User.ask(self, 1, l)
                    ship = Ship(st_coord, l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    if gen_type != 1:
                        print(board)
                    break
                except BoardException as e:
                    print(e)

        board.board_clear()
        return board

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.loop()


size = input('Введите размер игрового поля (5-9): ')
if size.isdigit() and 5 <= int(size) <= 9:
    auto = int(input('Хотите расставить корабли автоматически? 1 - ДА, 0 - НЕТ: '))
    g = Game(int(size), auto)
    g.start()
else:
    print(" Необходимо ввести число от 5 до 9! ")

# b.add_ship(ship)
# print(b)
# b.board_clear()
# b.shot(Dot(2, 2))
# print(b)
# b.shot(Dot(2, 3))
# print(b)
# b.shot(Dot(3, 3))
# print(b)
# b.shot(Dot(4, 3))
# print(b)
# b.shot(Dot(5, 3))
# print(b)
