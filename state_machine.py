from abc import ABC, abstractmethod
from calendar import c
from functools import cache
import stat


def is_legal_by_bound(state, x, y):
    return 0 <= x < len(state) and 0 <= y < len(state[0])


def is_legal_by_state(state, color, x, y):
    target = state[x][y]
    if target == "一一":
        return True
    if target.startswith(color):
        return False
    return True


def raw_moves(cur_state, x, y):
    moves = []
    for i in range(1, 10):
        moves.append((x + i, y))
        moves.append((x - i, y))
        moves.append((x, y + i))
        moves.append((x, y - i))
    return moves


def linear_move_filter(cur_state, x, y, new_x, new_y, *, allow_jump=False):

    src_piece = cur_state[x][y]
    dst_piece = cur_state[new_x][new_y]

    if x != new_x and y != new_y:
        return False

    count = 0
    if x != new_x:
        step = 1 if new_x > x else -1
        for i in range(x + step, new_x, step):
            if cur_state[i][y] != "一一":
                count += 1
    elif y != new_y:
        step = 1 if new_y > y else -1
        for i in range(y + step, new_y, step):
            if cur_state[x][i] != "一一":
                count += 1

    dst_empty = dst_piece == "一一"
    dst_enemy = dst_piece != "一一" and not dst_piece.startswith(src_piece[0])

    if allow_jump:
        return (count == 1 and dst_enemy) or (count == 0 and dst_empty)
    else:
        return count == 0 and (dst_empty or dst_enemy)


car_filter = lambda cur_state, x, y, new_x, new_y: linear_move_filter(
    cur_state, x, y, new_x, new_y, allow_jump=False
)

cannon_filter = lambda cur_state, x, y, new_x, new_y: linear_move_filter(
    cur_state, x, y, new_x, new_y, allow_jump=True
)


def filter_legal_moves(color, customize_filter=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cur_state, x, y = args[-3], args[-2], args[-1]
            moves = func(*args, **kwargs)

            moves = [pos for pos in moves if is_legal_by_bound(cur_state, *pos)]

            moves = [pos for pos in moves if is_legal_by_state(cur_state, color, *pos)]

            if customize_filter is not None:
                moves = [
                    pos for pos in moves if customize_filter(cur_state, x, y, *pos)
                ]

            return set(moves)

        return wrapper

    return decorator


class AbstractPiece(ABC):
    @classmethod
    @abstractmethod
    def _is(cls, cur_state, x, y):
        pass


class Piece(AbstractPiece):
    available_pieces = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Piece.available_pieces.append(cls)

    @classmethod
    def _is(cls, cur_state, x, y):
        return cur_state[x][y] == cls.name

    @staticmethod
    def get_all_available_pieces():
        return Piece.available_pieces

    @staticmethod
    def get_name_to_cls_mapping():
        return {piece.name: piece for piece in Piece.available_pieces}


class BlackMinion(Piece):
    name = "黑兵"

    @staticmethod
    @filter_legal_moves("黑")
    def get_next_legal_move(cur_state, x, y):
        if x <= 4:
            return [(x - 1, y), (x, y + 1), (x, y - 1)]
        return [(x - 1, y)]


class RedMinion(Piece):
    name = "红兵"

    @staticmethod
    @filter_legal_moves("红")
    def get_next_legal_move(cur_state, x, y):
        if x > 4:
            return [(x + 1, y), (x, y + 1), (x, y - 1)]
        return [(x + 1, y)]


class BlackGeneral(Piece):
    name = "黑帅"

    @staticmethod
    def _filter(cur_state, x, y, new_x, new_y):
        if new_x < 7 or new_y < 3 or new_y > 5:
            return False
        return True

    @staticmethod
    @filter_legal_moves("黑", customize_filter=_filter)
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class RedGeneral(Piece):
    name = "红帅"

    @staticmethod
    def _filter(cur_state, x, y, new_x, new_y):
        if new_x > 2 or new_y < 3 or new_y > 5:
            return False
        return True

    @staticmethod
    @filter_legal_moves("红", customize_filter=_filter)
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class Cannon(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color, cannon_filter)(raw_moves)


class BlackCannon(Cannon):
    name = "黑炮"


class RedCannon(Cannon):
    name = "红炮"


class Car(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color, car_filter)(raw_moves)


class BlackCar(Car):
    name = "黑车"


class RedCar(Car):
    name = "红车"


def horse_move(cur_state, x, y):
    moves = []
    for dx, dy in [
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    ]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if cur_state[new_x][new_y] == "一一" or not cur_state[new_x][
                new_y
            ].startswith(cur_state[x][y][0]):
                if (
                    (dx == 2 and cur_state[x + 1][y] == "一一")
                    or (dx == -2 and cur_state[x - 1][y] == "一一")
                    or (dy == 2 and cur_state[x][y + 1] == "一一")
                    or (dy == -2 and cur_state[x][y - 1] == "一一")
                ):
                    moves.append((new_x, new_y))

    return moves


class Horse(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(horse_move)


class BlackHorse(Horse):
    name = "黑马"


class RedHorse(Horse):
    name = "红马"


def elephant_move(cur_state, x, y):
    moves = []
    black_bound = 5
    red_bound = 4
    for dx, dy in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if cur_state[new_x][new_y] == "一一" or not cur_state[new_x][
                new_y
            ].startswith(cur_state[x][y][0]):
                midx = (x + new_x) // 2
                midy = (y + new_y) // 2
                if cur_state[midx][midy] == "一一":
                    if (cur_state[x][y].startswith("黑") and midx >= black_bound) or (
                        cur_state[x][y].startswith("红") and midx <= red_bound
                    ):
                        moves.append((new_x, new_y))
    return moves


class Elephant(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(elephant_move)


class BlackElephant(Elephant):
    name = "黑象"


class RedElephant(Elephant):
    name = "红象"


def gurdian_move(cur_state, x, y):
    moves = []
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if (
                (
                    cur_state[new_x][new_y] == "一一"
                    or not cur_state[new_x][new_y].startswith(cur_state[x][y][0])
                )
                and new_y >= 3
                and new_y <= 5
            ):
                if (cur_state[x][y].startswith("黑") and new_x >= 7) or (
                    cur_state[x][y].startswith("红") and new_x <= 2
                ):
                    moves.append((new_x, new_y))
    return moves


class Gurdian(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(gurdian_move)


class BlackGurdian(Gurdian):
    name = "黑士"


class RedGurdian(Gurdian):
    name = "红士"


class StateMachine:
    @staticmethod
    def get_all_legal_mutates(state, player):
        yielded = set()
        for _row in state:
            for _piece in _row:
                if _piece != "一一":
                    piece_cls = Piece.get_name_to_cls_mapping().get(_piece)
                    if piece_cls and _piece.startswith(player):
                        for x in range(len(state)):
                            for y in range(len(state[0])):
                                if piece_cls._is(state, x, y):
                                    moves = piece_cls.get_next_legal_move(state, x, y)
                                    for move in moves:
                                        if (x, y, move[0], move[1]) not in yielded:
                                            yielded.add((x, y, move[0], move[1]))
                                            yield (x, y), move

    @staticmethod
    def get_a_random_mutate(state, player):
        from random import choice

        moves = list(StateMachine.get_all_legal_mutates(state, player))
        if moves:
            return choice(moves)
        return None

    @staticmethod
    def make_move(state, from_pos, to_pos):
        x_from, y_from = from_pos
        x_to, y_to = to_pos
        new_state = [row[:] for row in state]
        new_state[x_to][y_to] = new_state[x_from][y_from]
        new_state[x_from][y_from] = "一一"
        return new_state


if __name__ == "__main__":
    import unittest

    class TestStateMachine(unittest.TestCase):
        def test_piece_is(self):
            state = [["黑兵"]]
            x, y = 0, 0
            self.assertTrue(BlackMinion._is(state, x, y))

        def test_get_all_pieces(self):
            pieces = Piece.get_all_available_pieces()
            self.assertIn(BlackMinion, pieces)
            self.assertIn(RedMinion, pieces)
            self.assertIn(BlackGeneral, pieces)
            self.assertIn(RedGeneral, pieces)
            self.assertIn(BlackCannon, pieces)
            self.assertIn(RedCannon, pieces)

        def test_get_name_to_cls_mapping(self):
            mapping = Piece.get_name_to_cls_mapping()
            self.assertEqual(mapping["黑兵"], BlackMinion)
            self.assertEqual(mapping["红兵"], RedMinion)

        def test_cannon_filter(self):
            state = [
                ["一一", "一一", "一一"],
                ["一一", "黑炮", "一一"],
                ["一一", "一一", "红车"],
            ]
            self.assertTrue(cannon_filter(state, 1, 1, 2, 1))
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "黑炮", "黑兵", "一一"],
                ["黑炮", "红车", "一一", "红车"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "黑车", "一一", "一一"],
            ]
            actual_moves = BlackCannon.get_next_legal_move(state, 1, 1)
            expect_moves = {(0, 1), (1, 0)}
            self.assertEqual(actual_moves, expect_moves)
            actual_moves = BlackCannon.get_next_legal_move(state, 2, 0)
            expect_moves = {(0, 0), (1, 0), (3, 0), (4, 0), (2, 3)}
            self.assertEqual(actual_moves, expect_moves)

        def test_state_machine(self):
            state = [
                ["一一", "一一", "一一"],
                ["一一", "黑炮", "一一"],
                ["一一", "红车", "一一"],
            ]
            player = "黑"
            moves = list(StateMachine.get_all_legal_mutates(state, player))
            self.assertEqual(len(moves), 3)

        def test_car_filter(self):
            state = [
                ["一一", "一一", "一一", "一一"],
                ["黑车", "一一", "红车", "红车"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["黑炮", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
            ]
            actual_moves = BlackCar.get_next_legal_move(state, 1, 0)
            expect_moves = {(0, 0), (1, 1), (1, 2), (2, 0), (3, 0)}
            self.assertEqual(actual_moves, expect_moves)

        def test_horse_move(self):
            state = [
                ["一一", "一一", "一一", "一一"],
                ["红车", "一一", "一一", "一一"],
                ["黑马", "一一", "红车", "红车"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["黑炮", "一一", "一一", "黑车"],
                ["一一", "黑车", "红车", "红车"],
            ]
            actual_moves = BlackHorse.get_next_legal_move(state, 2, 0)
            expect_moves = {(3, 2), (1, 2), (4, 1)}
            self.assertEqual(actual_moves, expect_moves)

        def test_elephant_move(self):
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["黑象", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 9, 0)
            expect_moves = {(7, 2)}
            self.assertEqual(actual_moves, expect_moves)
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "黑象", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
            expect_moves = {(9, 0), (5, 0)}
            self.assertEqual(actual_moves, expect_moves)

            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "黑象", "一一"],
                ["一一", "红兵", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
            expect_moves = {(5, 0)}
            self.assertEqual(actual_moves, expect_moves)
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "黑象", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["红兵", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
            expect_moves = {(5, 0), (9, 0)}
            self.assertEqual(actual_moves, expect_moves)
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "黑象", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["黑车", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
            expect_moves = {(5, 0)}
            self.assertEqual(actual_moves, expect_moves)
            state = [
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["黑象", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一"],
            ]
            actual_moves = BlackElephant.get_next_legal_move(state, 5, 0)
            expect_moves = {(7, 2)}
            self.assertEqual(actual_moves, expect_moves)

        def test_gurdian_move(self):
            # fmt: off
            state = [
                ["红车", "红马", "红象", "红士", "红帅", "红士", "红象", "红马", "红车"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["一一", "红炮", "一一", "一一", "一一", "一一", "一一", "红炮", "一一"],
                ["红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵"],
                ["一一", "黑炮", "一一", "一一", "一一", "一一", "一一", "黑炮", "一一"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["黑车", "黑马", "黑象", "黑士", "黑帅", "黑士", "黑象", "黑马", "黑车"],
            ]
            # fmt: on
            actual_moves = BlackGurdian.get_next_legal_move(state, 0, 3)
            expect_moves = {(1, 4)}
            self.assertEqual(actual_moves, expect_moves)
            # fmt: off
            state = [
                ["红车", "红马", "红象", "红士", "红帅", "一一", "红象", "红马", "红车"],
                ["一一", "一一", "一一", "一一", "红士", "一一", "一一", "一一", "一一"],
                ["一一", "红炮", "一一", "一一", "一一", "一一", "一一", "红炮", "一一"],
                ["红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
                ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵"],
                ["一一", "黑炮", "一一", "一一", "一一", "一一", "一一", "黑炮", "一一"],
                ["一一", "一一", "一一", "一一", "黑士", "一一", "一一", "一一", "一一"],
                ["黑车", "黑马", "黑象", "黑士", "黑帅", "一一", "黑象", "黑马", "黑车"],
            ]
            # fmt: on
            actual_moves = BlackGurdian.get_next_legal_move(state, 1, 4)
            expect_moves = {(0, 5), (2, 3), (2, 5)}
            actual_moves = BlackGurdian.get_next_legal_move(state, 8, 4)
            expect_moves = {(7, 3), (7, 5), (9, 5)}
            self.assertEqual(actual_moves, expect_moves)

    unittest.main()
