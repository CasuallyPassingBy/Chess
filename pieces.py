import pygame
from typing import TYPE_CHECKING
from constants import SQUARE_SIZE
if TYPE_CHECKING:
    from board import Board

class Piece:
    def __init__(self, color:int, pos: list[int]) -> None:
        self.color : int = color
        self.position : list[int] = pos
        self.piece_type:int = -1
        self.rect : 'pygame.Rect' = pygame.Rect(pos[0] * SQUARE_SIZE, pos[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

    def __repr__(self) -> str:
        return f'piece type: {self.piece_type}, position: {self.position}, color: {self.color}'

    def legal_moves(self, board:'Board') -> list[list[int]]:
        pass
    
    def attacking_squares(self, board:'Board') -> list[list[int]]:
        pass

class King(Piece):
    def __init__(self, color:int, pos: list[int]) -> None:
        super().__init__(color, pos)
        self.piece_type = 0
        self.in_check:bool = False
        self.possible_castle:bool = True

    def legal_moves(self, board:'Board'):
        x, y = self.position
        legal_moves = [[x + i, y + j] for i in range(-1, 2) for j in range(-1, 2)]
        legal_moves.remove([x, y])
        return legal_moves
    
    def attacking_squares(self, board: 'Board') -> list[list[int]]:
        return self.legal_moves(board)
    
    def castling(self, board: 'Board')-> list[list[int]]:
        if not self.possible_castle:
            return []
        
        castling_moves = []
        king_side = [[i, self.position[1]] for i in range(5, 7)]
        queen_side = [[i, self.position[1]] for i in range(1, 4)]

        # checking king side
        rooks:list[Rook] = [piece for piece in board.board if isinstance(piece, Rook) and piece.color == self.color]
        for rook in rooks:
            if not rook.castling:
                continue
            # checking king side
            if rook.position[0] == 7 and all(map(board.IsEmpty, king_side)):
                castling_moves += [[self.position[0] + 2, self.position[1]]]

            elif rook.position[0] == 7 and all(map(board.IsEmpty, queen_side)):
                castling_moves += [[self.position[0] - 2, self.position[1]]]

        return castling_moves

class Queen(Piece):
    directions = [
        ( 0, 1), ( 0,-1),
        ( 1, 0), (-1, 0),
        ( 1, 1), (-1,-1),
        ( -1,1), ( 1,-1)
        ]
    
    def __init__(self, color:int, pos: list[int]) -> None:
        super().__init__(color, pos)
        self.piece_type = 1

    def legal_moves(self, board:'Board') -> list[list[int]]:
        x, y = self.position
        occupied_positions = [piece.position for piece in board.board]
        legal_moves = []
        for direction in Queen.directions:
            for i in range(1,8):
                possible_move = [x + i*direction[0], y +i*direction[1]]
                legal_moves.append(possible_move)
                if possible_move in occupied_positions:
                    break

        return legal_moves
    
    def attacking_squares(self, board:'Board') -> list[list[int]]:
        return self.legal_moves(board)

class Rook(Piece):
    directions = [
        ( 0, 1), ( 0,-1),
        ( 1, 0), (-1, 0)
        ]
    def __init__(self, color:int, pos: list[int]) -> None:
        super().__init__(color, pos)
        self.piece_type = 2
        self.castling = True

    def legal_moves(self, board:'Board') -> list[list[int]]:
        x, y = self.position
        occupied_positions = [piece.position for piece in board.board]
        legal_moves = []
        for direction in Rook.directions:
            for i in range(1,8):
                possible_move = [x + i*direction[0], y +i*direction[1]]
                legal_moves.append(possible_move)
                if possible_move in occupied_positions:
                    break

        return legal_moves
    
    def attacking_squares(self, board: 'Board') -> list[list[int]]:
        return self.legal_moves(board)

class Bishop(Piece):
    directions = [
        ( 1, 1), (-1,-1),
        ( -1,1), ( 1,-1)
        ]
    def __init__(self, color:int, pos: list[int])-> None:
        super().__init__(color, pos)
        self.piece_type = 3

    def legal_moves(self, board:'Board') -> list[list[int]]:
        x, y = self.position
        occupied_positions = [piece.position for piece in board.board]
        legal_moves = []
        for direction in Bishop.directions:
            for i in range(1,8):
                possible_move = [x + i * direction[0], y + i * direction[1]]
                legal_moves.append(possible_move)
                if possible_move in occupied_positions:
                    break

        return legal_moves
    
    def attacking_squares(self, board:'Board') -> list[list[int]]:
        return self.legal_moves(board)

class Knight(Piece):
    moves = [
        (-2,-1), (-2, 1),
        ( 2,-1), ( 2, 1),
        (-1, 2), (-1,-2),
        ( 1, 2), ( 1,-2)
        ]
    
    def __init__(self, color:int, pos: list[int]) -> None:
        super().__init__(color, pos)
        self.piece_type = 4

    def legal_moves(self, board:'Board') -> list[list[int]]:
        x, y = self.position
        legal_moves = [[x + move[0], y + move[1]] for move in Knight.moves]
        return legal_moves

    def attacking_squares(self, board: 'Board') -> list[list[int]]:
        return self.legal_moves(board)
    
class Pawn(Piece):
    special_ranks = (1, 6)
    directions = (1, -1)
    en_passant_rank = (4, 3)

    def __init__(self, color:int, pos: list[int]) -> None:
        super().__init__(color, pos)
        self.en_passant_able = False
        self.piece_type = 5

    def legal_moves(self, board:'Board') -> list[list[int]]:
        x, y = self.position
        occupied_positions = [piece.position for piece in board.board]
        legal_moves = []
        if y == Pawn.special_ranks[self.color]:
            double_forward = [x, y + 2 * Pawn.directions[self.color]]
            if double_forward not in occupied_positions:
                legal_moves.append(double_forward)

        forward = [x, y + Pawn.directions[self.color]]
        if forward not in occupied_positions:
            legal_moves.append(forward)
        else:
            legal_moves = []
        
        attacking_squares = self.attacking_squares(board)

        opposing_pieces_positions = [piece.position for piece in board.board if piece.color != self.color]

        for attacking_square in attacking_squares[:]:
            if attacking_square not in opposing_pieces_positions:
                attacking_squares.remove(attacking_square)
        if self.position[1] == Pawn.en_passant_rank[self.color]:
            attacking_squares += [self.check_for_en_passant(board)]
        legal_moves += attacking_squares
        legal_moves = [move for move in legal_moves if move is not None]
        return legal_moves
    
    def attacking_squares(self, board: 'Board') -> list[list[int]]:
        x, y = self.position
        attacking_squares = [[x + i , y + Pawn.directions[self.color]] for i in range(-1, 2, 2)]
        return attacking_squares
    
    def check_for_en_passant(self, board:'Board') -> list[int]:
        attacker_color = 1 - self.color
        for piece in board.board:
            if isinstance(piece, Pawn) and piece.color == attacker_color:
                if (not piece.en_passant_able):
                    continue

                if abs(piece.position[0] - self.position[0]) == 1:
                    return [piece.position[0], self.position[1] + Pawn.directions[self.color]]
        return None
