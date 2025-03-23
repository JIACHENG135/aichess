from abc import ABC, abstractmethod


def is_legal_by_bound(state, x, y):
    return 0 <= x < len(state) and 0 <= y < len(state[0])


def is_legal_by_state(state, color, x, y):
    target = state[x][y]
    if target == "一一":
        return True
    if target.startswith(color):
        return False
    return True


def cannon_filter(cur_state, x, y, new_x, new_y):
    not_occupied = cur_state[new_x][new_y] == "一一"
    count = 0
    move_direction = (new_x - x, new_y - y)
    if move_direction[0] != 0:
        step = 1 if move_direction[0] > 0 else -1
        for i in range(x + step, new_x, step):
            if cur_state[i][y] != "一一":
                count += 1
    if move_direction[1] != 0:
        step = 1 if move_direction[1] > 0 else -1
        for i in range(y + step, new_y, step):
            if cur_state[x][i] != "一一":
                count += 1
    return (count == 1 and not not_occupied) or (count == 0 and not_occupied)


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
    @filter_legal_moves("黑")
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class RedGeneral(Piece):
    name = "红帅"

    @staticmethod
    @filter_legal_moves("红")
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class Cannon(Piece):
    name = None

    @classmethod
    def raw_moves(cls, cur_state, x, y):
        moves = []
        for i in range(1, 10):
            moves.append((x + i, y))
            moves.append((x - i, y))
            moves.append((x, y + i))
            moves.append((x, y - i))
        return moves

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color, cannon_filter)(
            cls.raw_moves
        )


class BlackCannon(Cannon):
    name = "黑炮"


class RedCannon(Cannon):
    name = "红炮"


class StateMachine:
    @staticmethod
    def get_all_legal_mutates(state, player):
        return []


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

    unittest.main()
