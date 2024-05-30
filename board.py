import pygame
from typing import Optional
from constants import WHITE, BLACK, SQUARE_SIZE, SELECTED_WHITE, SELECTED_BLACK
from pieces import *

class Board:
    """
    Represents the chess board.

    Attributes:
    - WIN (pygame.surface): The Pygame surface to draw the board on.
    - IMAGES (list[list[pygame.Surface]]): The images of the chess pieces.
    - board (list[Piece]): The list of pieces on the board.
    - graphical_board (list[pygame.Rect]): The list of graphical rectangles representing each square on the board.

    Methods:
    - __init__(self, win: pygame.surface, images: list[list[pygame.Surface]]): Initializes the Board object.
    - DrawBoard(self) -> None: Draws the chess board on the Pygame surface.
    - DrawPieces(self) -> None: Draws the chess pieces on the board.
    - DrawSelectedSquares(self, legal_moves: list[list[int]]) -> None: Draws the selected squares on the board.
    - FindKing(self, color: int) -> Optional[list[int]]: Finds the position of the king of the specified color.
    - IsSquareAttacked(self, square: list[int], attacker_color: int) -> bool: Checks if a square is attacked by any piece of the specified color.
    - IsEmpty(self, position: list[int]) -> bool: Checks if a square is empty.
    - IsKingInCheck(self, color: int) -> bool: Checks if the king of the specified color is in check.
    - IsCheckmate(self, color: int) -> bool: Checks if the specified color is in checkmate.
    - TranslateFen(self, fen: str) -> None: Translates the FEN string representation of the board to the internal board representation.
    """

    def __init__(self, win: pygame.surface, images: list[list[pygame.Surface]]):
        self.board: 'list[Piece]' = []
        self.WIN = win
        self.IMAGES = images
        self.graphical_board: 'list[pygame.Rect]' = [
            pygame.Rect(i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            for i in range(8) for j in range(8)
        ]

    def DrawBoard(self) -> None:
        """
        Draws the chess board on the Pygame surface.
        """
        for rank in range(8):
            for file in range(8):
                square_color = WHITE if (rank + file) % 2 == 0 else BLACK
                pygame.draw.rect(self.WIN, square_color, self.graphical_board[rank + 8 * file])

    def DrawPieces(self) -> None:
        """
        Draws the chess pieces on the board.
        """
        for piece in self.board:
            self.WIN.blit(self.IMAGES[1 - piece.color][piece.piece_type], piece.rect)

    def DrawSelectedSquares(self, legal_moves: list[list[int]]) -> None:
        """
        Draws the selected squares on the board.

        Args:
        - legal_moves (list[list[int]]): The list of legal moves represented as [file, rank] pairs.
        """
        if legal_moves == []:
            return
        for position in legal_moves:
            file, rank = position
            square = self.graphical_board[rank + 8 * file]
            square_color = SELECTED_WHITE if ((file + rank) % 2 == 0) else SELECTED_BLACK
            pygame.draw.rect(self.WIN, square_color, square)

    def FindKing(self, color: int) -> Optional[list[int]]:
        """
        Finds the position of the king of the specified color.

        Args:
        - color (int): The color of the king to find.

        Returns:
        - Optional[list[int]]: The position of the king as [file, rank] pair, or None if the king is not found.
        """
        for piece in self.board:
            if isinstance(piece, King) and piece.color == color:
                return piece.position

        return None

    def IsSquareAttacked(self, square: list[int], attacker_color: int) -> bool:
        """
        Checks if a square is attacked by any piece of the specified color.

        Args:
        - square (list[int]): The position of the square to check as [file, rank] pair.
        - attacker_color (int): The color of the attacking pieces.

        Returns:
        - bool: True if the square is attacked, False otherwise.
        """
        for piece in self.board:
            if piece.color == attacker_color:
                legal_moves = MoveManager.AttackedSquares(piece, self)
                if square in legal_moves:
                    return True
        return False

    def IsEmpty(self, position: list[int]) -> bool:
        """
        Checks if a square is empty.

        Args:
        - position (list[int]): The position of the square to check as [file, rank] pair.

        Returns:
        - bool: True if the square is empty, False otherwise.
        """
        for piece in self.board:
            if piece.position == position:
                return False
        return True

    def IsKingInCheck(self, color: int) -> bool:
        """
        Checks if the king of the specified color is in check.

        Args:
        - color (int): The color of the king to check.

        Returns:
        - bool: True if the king is in check, False otherwise.
        """
        king_position = self.FindKing(color)
        opponent_color = 1 - color
        return self.IsSquareAttacked(king_position, opponent_color)

    def IsCheckmate(self, color: int) -> bool:
        """
        Checks if the specified color is in checkmate.

        Args:
        - color (int): The color to check for checkmate.

        Returns:
        - bool: True if the color is in checkmate, False otherwise.
        """
        # Check if the opponent's king is in check
        if not self.IsKingInCheck(color):
            return False

        # Generate legal moves for all opponent's pieces
        for piece in self.board:
            if piece.color != color:
                continue

            legal_moves = MoveManager.LegalMoves(piece, self)
            original_position = piece.position[:]

            # Test each move
            for move in legal_moves:
                # Apply the move temporarily
                piece.position = move

                # If the opponent's king is not in check after the move, it's not checkmate
                if not self.IsKingInCheck(color):
                    piece.position = original_position
                    return False

                # Revert the move
                piece.position = original_position

        # If no legal move can remove the check, it's checkmate
        return True

    def TranslateFen(self, fen: str) -> None:
        """
        Translates the FEN string representation of the board to the internal board representation.

        Args:
        - fen (str): The FEN string representation of the board.
        """
        self.board = ChessParser.TranslateFen(fen)
class ChessParser:
    """
    This class is specifically to initialize the chess board, 
    so given a FEN, all the pieces are created and set-up in the right space
    """
    @staticmethod
    def TranslateFen(fen:str) -> 'list[Piece]':
        '''
        Translates the first part of a FEN into the initial conditions 
        of the board, letting you have more flexibility
        '''
        pieces = []
        position = [0, 0]
        splitted_fen = fen.split(' ')
        board_position, turn, castling, en_passant, halfmove, fullmove = splitted_fen
        for character in board_position:
            if character == '/':
                position[0] = 0
                position[1] += 1
                continue

            elif character.lower() in 'kqrbnp':
                color = 0 if (character == character.lower()) else 1
                piece = ChessParser.create_piece(color, character.lower(), position[:])
                if piece is not None:
                    pieces.append(piece)
                    position[0] += 1
                continue

            elif character in '12345678':
                position[0] += int(character)

        MoveManager.turn = 0 if (turn == 'b') else 1

        rooks = [piece for piece in pieces if isinstance(piece, Rook)]
        if castling == '-': 
            for rook in rooks:
                rook.castling = False
        else:
            for character in castling:
                if character == 'K':
                    castling_rook_pos = [7, 7]
                elif character == 'Q':
                    castling_rook_pos = [0, 7]
                elif character == 'k':
                    castling_rook_pos = [7, 0]
                elif character == 'q':
                    castling_rook_pos = [0, 0]
                for rook in rooks:
                    if rook.position == castling_rook_pos:
                        rook.castling = True
                        break

        return pieces
    
    @staticmethod
    def create_piece(color: int, piece_type: str, pos: list[int]) -> 'Optional[Piece]':
        """
        Create a new chess piece based on the given color, piece type, and position.

        Parameters:
        color (int): The color of the piece. 0 for white, 1 for black.
        piece_type (str): The type of the piece. Valid values are 'p' for pawn, 'n' for knight,
                          'b' for bishop, 'r' for rook, 'q' for queen, and 'k' for king.
        pos (list[int]): The position of the piece on the chessboard.

        Returns:
        Optional[Piece]: The created piece object if the piece type is valid, None otherwise.
        """
        if piece_type == 'p':
            return Pawn(color, pos)
        elif piece_type == 'n':
            return Knight(color, pos)
        elif piece_type == 'b':
            return Bishop(color, pos)
        elif piece_type == 'r':
            return Rook(color, pos)
        elif piece_type == 'q':
            return Queen(color, pos)
        elif piece_type == 'k':
            return King(color, pos)
        return None
class MoveManager:
    """
    The MoveManager class handles the movement of chess pieces on the board.
    It provides methods to calculate legal moves, check for attacked squares,
    validate moves, capture pieces, handle en passant, and perform castling.
    """

    turn = 0

    @staticmethod
    def LegalMoves(piece:'Optional[Piece]', board:'Board') -> list[list[int]]:
        '''
        Given a piece and the board state, we can calculate their legal moves of the piece.
        '''
        if piece is None:
            return []

        if piece.color != MoveManager.turn:
            return []
    
        legal_moves = piece.legal_moves(board)

        legal_moves = [pos for pos in legal_moves if ((0 <= pos[0] <= 7) and (0 <= pos[1]<= 7))]
        same_color_occupied_positions = [dummy_piece.position for dummy_piece in board.board if dummy_piece.color == piece.color]
        legal_moves = list(filter(lambda x: x not in same_color_occupied_positions, legal_moves))
        
        if isinstance(piece, King) and piece.possible_castle:
            legal_moves += piece.castling(board)

        filtered_moves = []
        
        for move in legal_moves:
            original_position = piece.position[:]
            # Apply the move temporarily
            piece.position = move
            # Check if the player's king is still in check after the move
            if not board.IsKingInCheck(piece.color):
                filtered_moves.append(move)
            # Revert the move
            piece.position = original_position

        return filtered_moves
    
    @staticmethod
    def AttackedSquares(piece:'Piece', board:'Board'):
        """
        Given a piece and the board state, this method returns a list of squares
        that are attacked by the piece.
        """
        attacking_squares = piece.attacking_squares(board)
        attacking_squares = [pos for pos in attacking_squares if ((0 <= pos[0]<= 7) and (0 <= pos[1]<= 7))]
        return attacking_squares
    
    @staticmethod
    def IsLegalMove(piece:'Piece', board:'Board', move:list[int]) -> bool:
        """
        Given a piece, the board state, and a move, this method checks if the move
        is a legal move for the piece.
        """
        legal_moves = MoveManager.LegalMoves(piece, board)
        return move in legal_moves
    
    @staticmethod
    def capturePiece(selected_piece: 'Piece', board: 'Board', position: list[int]) -> None:
        """
        Given a selected piece, the board state, and a position, this method captures
        the piece at the given position on the board.
        """
        for piece in board.board:
            if piece.color != selected_piece.color and piece.position == position:
                board.board.remove(piece)
                del piece
                break
        return

    @staticmethod
    def En_passant_takinator(selected_piece: 'Optional[Piece]', board: 'Board', position: list[int]) -> None:
        """
        Given a selected piece, the board state, and a position, this method handles
        en passant capture if applicable.
        """
        if isinstance(selected_piece, Pawn):
            for piece in board.board:
                if isinstance(piece, Pawn) and piece.color != selected_piece.color and piece.en_passant_able and piece.position[1] == selected_piece.position[1]: 
                    if abs(piece.position[0] - selected_piece.position[0]) == 1:
                        board.board.remove(piece)
                        del piece
                    break
        
    @staticmethod
    def castle_inator(selected_piece: 'King', board: 'Board', position: list[int]) -> None:
        """
        Given a selected king piece, the board state, and a position, this method handles
        castling if applicable.
        """
        rank = position[0]
        if isinstance(selected_piece, King):
            castling_file = -1
            rook = selected_piece
            print(rank)
            # king-sided castling
            if rank == 6:
                castling_file = 7
                for possible_rook in board.board:
                    if possible_rook.position[0] == castling_file  and possible_rook.position[1] == selected_piece.position[1] and \
                    isinstance(possible_rook, Rook) and possible_rook.color == selected_piece.color:
                        if possible_rook.castling:
                            rook = possible_rook
                            break
                # move the rook
                rook.position[0] -= 2
                rook.rect.x = rook.position[0] * SQUARE_SIZE
                
            # Queen-sided castling
            elif rank == 2:
                castling_file = 0
                for possible_rook in board.board:
                    if possible_rook.position[0] == castling_file  and possible_rook.position[1] == selected_piece.position[1] and \
                    isinstance(possible_rook, Rook) and possible_rook.color == selected_piece.color:
                        if possible_rook.castling:
                            rook = possible_rook
                            break
                # move the rook
                rook.position[0] += 3
                rook.rect.x = rook.position[0] * SQUARE_SIZE

    @staticmethod
    def MovePiece(selected_piece:'Optional[Piece]', board:'Board', legal_moves: list[list[int]]) -> 'Optional[bool]':
        """
        Given a selected piece, the board state, and a list of legal moves, this method
        moves the piece on the board, captures pieces, handles en passant, and performs castling.
        """
        if selected_piece is None:
            return 

        x_position, y_position = selected_piece.rect.x, selected_piece.rect.y
        rank = round(x_position / SQUARE_SIZE)
        file = round(y_position / SQUARE_SIZE)
        position = [rank, file]

        # Checks if the move is legal
        if position not in legal_moves:
            selected_piece.rect.x = selected_piece.position[0] * SQUARE_SIZE
            selected_piece.rect.y = selected_piece.position[1] * SQUARE_SIZE
            return
        
        selected_piece.rect.x = rank * SQUARE_SIZE
        selected_piece.rect.y = file * SQUARE_SIZE

        # Checks if we need to take a piece
        MoveManager.capturePiece(selected_piece, board, position)

        # Checks if we need to do en passant
        MoveManager.En_passant_takinator(selected_piece, board, position)

        # move-rookinator (moves rook after castling)
        MoveManager.castle_inator(selected_piece, board, position)
    
        # Checks if the pawn double moved to see if it en passantable 
        if isinstance(selected_piece, Pawn) and abs(file - selected_piece.position[1]) == 2:
            selected_piece.en_passant_able = True

        # makes it so that en-passant is only possible right after
        for piece in board.board:
            if isinstance(piece, Pawn) and piece.color != selected_piece.color:
                piece.en_passant_able = False

        # Perform the move
        selected_piece.position = position
        MoveManager.turn ^= 1
        
        opponent_color = 1 - selected_piece.color

        if isinstance(selected_piece, King):
            selected_piece.possible_castle = False

        elif isinstance(selected_piece, Rook):
            selected_piece.castling = False

            # Check for pawn promotion
        if isinstance(selected_piece, Pawn):
            if selected_piece.position[1] == 0 or selected_piece.position[1] == 7:
                # Promote pawn to queen (you can adjust this if you want other piece types)
                board.board.append(Queen(selected_piece.color, selected_piece.position))
                board.board.remove(selected_piece)

        # Check for checkmate
        if board.IsCheckmate(opponent_color):
            # End the game with a victory for the player who delivered the checkmate
            return (selected_piece == 1)
