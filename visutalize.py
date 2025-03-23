import time
from PIL import Image
import numpy as np
import os
from state_machine import StateMachine
import cv2


class MoveSeries:
    def __init__(self, init_state):
        """
        Initializes the MoveSeries with the initial state of the board.

        :param init_state: The initial state of the board.
        """
        self.state = init_state
        self.move_series = []

    def add_move(self, move):
        """
        Adds a move to the series.

        :param move: A tuple containing the from and to positions of the move.
        """
        self.move_series.append(move)

    def make_video(self):
        """
        Generates a video of the move series.
        based on generate images for each move in the series.

        """
        time_stamp = int(time.time())
        video_folder = f"/tmp/{time_stamp}"
        os.makedirs(video_folder, exist_ok=True)
        video_filename = f"{video_folder}/chess_video.mp4"
        for ind, (from_pos, to_pos) in enumerate(self.move_series):
            self.state = StateMachine.make_move(self.state, from_pos, to_pos)
            Visualize.render_board_with_state(
                self.state, filename=f"{video_folder}/frame_{ind:03d}.png"
            )
            print(f"Frame {ind} generated.")
        # Generate video from images
        images = []
        for ind in range(len(self.move_series)):
            img_path = f"{video_folder}/frame_{ind:03d}.png"
            images.append(cv2.imread(img_path))
            print(f"Image {ind} loaded.")
        height, width, layers = images[0].shape
        video = cv2.VideoWriter(
            video_filename, cv2.VideoWriter_fourcc(*"XVID"), 10, (width, height)
        )
        for img in images:
            video.write(img)
        video.release()
        self.move_series = []
        return video_filename


class Visualize:
    @staticmethod
    def render_board_with_state(state_matrix, filename="output_chessboard.png"):
        """
        Renders the board with the given state.

        :param state: The current state of the board.
        """
        board_img = Image.open("./imgs/board.png")
        board_img = board_img.convert("RGBA")
        ROWS, COLS = 10, 9
        cell_width = board_img.width // COLS
        cell_height = board_img.height // ROWS
        pieces_folder = "./imgs"
        piece_images = {}
        for _filename in os.listdir(pieces_folder):
            if _filename.endswith(".png"):
                piece_name = _filename.replace(".png", "")
                piece_images[piece_name] = Image.open(
                    os.path.join(pieces_folder, _filename)
                ).convert("RGBA")
        composite = board_img.copy()

        for row in range(ROWS):
            for col in range(COLS):
                piece_name = state_matrix[row][col]
                if piece_name != "一一":
                    piece_img = piece_images.get(piece_name)
                    if piece_img:
                        resized_piece = piece_img.resize(
                            (cell_width, cell_height), Image.LANCZOS
                        )
                        x = col * cell_width
                        y = row * cell_height
                        composite.paste(resized_piece, (x, y), mask=resized_piece)
        print(f"saving image to {filename}")
        composite.save(filename)


if __name__ == "__main__":
    state_matrix = [
        ["一一", "红马", "一一", "红士", "红帅", "红士", "红象", "一一", "一一"],
        ["红车", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
        ["红车", "一一", "一一", "一一", "红象", "一一", "一一", "一一", "红马"],
        ["红兵", "一一", "红兵", "一一", "一一", "一一", "一一", "一一", "红兵"],
        ["一一", "一一", "一一", "一一", "红兵", "一一", "红兵", "一一", "一一"],
        ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "一一", "一一", "一一"],
        ["一一", "一一", "一一", "一一", "一一", "黑炮", "黑兵", "一一", "一一"],
        ["一一", "一一", "黑炮", "一一", "黑象", "红炮", "一一", "红炮", "黑车"],
        ["黑车", "黑马", "一一", "一一", "黑帅", "一一", "一一", "一一", "一一"],
        ["一一", "一一", "一一", "黑士", "一一", "黑士", "黑象", "黑马", "一一"],
    ]
    init_state_matrix = [
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
    steps = 30
    move_series = MoveSeries(init_state_matrix)
    players = ["红", "黑"]
    for _ in range(steps):
        move = StateMachine.get_a_random_mutate(
            init_state_matrix, players[[0, 1][_ % 2]]
        )
        if move:
            from_pos, to_pos = move
            move_series.add_move(move)
            init_state_matrix = StateMachine.make_move(
                init_state_matrix, from_pos, to_pos
            )
    video_filename = move_series.make_video()
    print(f"Video saved as {video_filename}")
