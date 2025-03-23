from PIL import Image
import numpy as np
import os
class Visualize:
    @staticmethod
    def render_board_with_state(state_matrix):
        """
        Renders the board with the given state.
        
        :param state: The current state of the board.
        """
        board_img = Image.open('./imgs/board.png')
        board_img = board_img.convert("RGBA")
        ROWS, COLS = 10, 9
        cell_width = board_img.width // COLS
        cell_height = board_img.height // ROWS
        pieces_folder = './imgs'
        piece_images = {}
        for filename in os.listdir(pieces_folder):
            if filename.endswith('.png'):
                piece_name = filename.replace('.png', '')
                piece_images[piece_name] = Image.open(os.path.join(pieces_folder, filename)).convert("RGBA")
        composite = board_img.copy()

        for row in range(ROWS):
            for col in range(COLS):
                piece_name = state_matrix[row][col]
                if piece_name != '一一':
                    piece_img = piece_images.get(piece_name)
                    if piece_img:
                        resized_piece = piece_img.resize((cell_width, cell_height), Image.LANCZOS)
                        x = col * cell_width
                        y = row * cell_height
                        composite.paste(resized_piece, (x, y), mask=resized_piece)
        composite.save("output_chessboard.png")
        composite.show()


if __name__ == "__main__":
    state_matrix = [
        ['一一', '红马', '一一', '红士', '红帅', '红士', '红象', '一一', '一一'],
        ['红车', '一一', '一一', '一一', '一一', '一一', '一一', '一一', '一一'],
        ['红车', '一一', '一一', '一一', '红象', '一一', '一一', '一一', '红马'],
        ['红兵', '一一', '红兵', '一一', '一一', '一一', '一一', '一一', '红兵'],
        ['一一', '一一', '一一', '一一', '红兵', '一一', '红兵', '一一', '一一'],
        ['黑兵', '一一', '黑兵', '一一', '黑兵', '一一', '一一', '一一', '一一'],
        ['一一', '一一', '一一', '一一', '一一', '黑炮', '黑兵', '一一', '一一'],
        ['一一', '一一', '黑炮', '一一', '黑象', '红炮', '一一', '红炮', '黑车'],
        ['黑车', '黑马', '一一', '一一', '黑帅', '一一', '一一', '一一', '一一'],
        ['一一', '一一', '一一', '黑士', '一一', '黑士', '黑象', '黑马', '一一'],
    ]
    Visualize.render_board_with_state(state_matrix)
