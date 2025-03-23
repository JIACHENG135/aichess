from abc import ABC, abstractmethod


def is_legal_by_bound(x, y):
    return 0 <= x < 10 and 0 <= y < 9


def is_legal_by_state(state, color, x, y):
    target = state[x][y]
    if target == "一一":
        return True
    if target.startswith(color):
        return False
    return True


def filter_legal_moves(color, customize_filter=None):
    def decorator(func):
        def wrapper(cur_state, x, y):
            moves = func(cur_state, x, y)
            return list(
                filter(
                    lambda pos: (
                        is_legal_by_bound(*pos)
                        and is_legal_by_state(cur_state, color, *pos)
                        and True
                        if customize_filter is None
                        else customize_filter(cur_state, x, y, moves)
                    ),
                    moves,
                )
            )

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


class BlackCannon(Piece):
    name = "黑炮"

    @staticmethod
    @filter_legal_moves("黑")
    def get_next_legal_move(cur_state, x, y):
        moves = []
        for i in range(1, 10):
            moves.append((x + i, y))
            moves.append((x - i, y))
            moves.append((x, y + i))
            moves.append((x, y - i))
        return moves


class RedCannon(Piece):
    name = "红炮"

    @staticmethod
    @filter_legal_moves("红")
    def get_next_legal_move(cur_state, x, y):
        moves = []
        for i in range(1, 10):
            moves.append((x + i, y))
            moves.append((x - i, y))
            moves.append((x, y + i))
            moves.append((x, y - i))
        return moves


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

    unittest.main()
