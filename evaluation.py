# Description: This file contains the Evaluator class which is responsible for evaluating the board state.
from pieces import *
from board import Board

class Evaluator:
    @staticmethod
    def evaluate(piece:'Piece') -> int:
        if isinstance(piece, Pawn):
            return 1
        elif isinstance(piece, Knight):
            return 3
        elif isinstance(piece, Bishop):
            return 3
        elif isinstance(piece, Rook):
            return 5
        elif isinstance(piece, Queen):
            return 9
        elif isinstance(piece, King):
            return 1000
        else:
            return 0
    
    @staticmethod
    def material_value(board:'Board') -> int:
        white_value = sum([Evaluator.evaluate(piece) for piece in board.board if piece.color == 1])
        black_value = sum([Evaluator.evaluate(piece) for piece in board.board if piece.color == 0])
        return white_value - black_value
    