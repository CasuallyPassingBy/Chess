import pygame
from typing import Optional

pygame.font.init()

WIDTH, HEIGHT = 512, 512
SQUARE_SIZE = min(WIDTH, HEIGHT)//8

WHITE = (232, 235, 239)
BLACK = (150, 150, 150)
SELECTED_WHITE = (255, 220, 224)
SELECTED_BLACK = (250, 150, 150)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('chess maybe 2')

def load_image_piece(path:str) -> pygame.Surface:
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return image

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
IMAGES = [[load_image_piece(f'./pieces_svgs/piece_{i}{j}.svg') for j in range(6)] for i in range(2)]

# To Do:
# [x] Board
# [x] pieces
# [x] basic legal moves
# [x] highlighting of legal moves
# [x] moving pieces
# [x] unsafe squares
# [x] checks
# [x] checkmates
# [x] castling
# [x] en passant 

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

class Board:
    def __init__(self):
        self.board:'list[Piece]' = []
        self.graphical_board:'list[pygame.Rect]' = [
            pygame.Rect(i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE) 
            for i in range(8) for j in range(8)
            ]
    
    def DrawBoard(self) -> None:
        for rank in range(8):
            for file in range(8):
                square_color = WHITE if (rank + file) % 2 == 0 else BLACK
                pygame.draw.rect(WIN, square_color, self.graphical_board[rank + 8 * file])
    
    def DrawPieces(self) -> None:
        '''
        Let's you draw every piece in the board, and letting the image 
        '''
        piece:Piece
        for piece in self.board:
            WIN.blit(IMAGES[1 - piece.color][piece.piece_type], piece.rect)

    def DrawSelectedSquares(self, legal_moves:list[list[int]]) -> None:
        if legal_moves == []:
            return
        for position in legal_moves:
            file, rank = position
            square = self.graphical_board[rank + 8 * file]
            square_color = SELECTED_WHITE if ((file + rank) % 2 == 0 ) else SELECTED_BLACK
            pygame.draw.rect(WIN, square_color, square)
    
    def FindKing(self, color:int) -> Optional[list[int]]:
        for piece in self.board:
            if isinstance(piece, King) and piece.color == color:
                return piece.position
        
        return None

    def IsSquareAttacked(self, square:list[int], attacker_color:int) -> bool:
        for piece in self.board:
            if piece.color == attacker_color:
                legal_moves = MoveManager.AttackedSquares(piece, self)
                if square in legal_moves:
                    return True
        return False
    
    def IsEmpty(self, position:list[int]) -> bool:
        for piece in self.board:
            if piece.position == position:
                return False
        return True

    def IsKingInCheck(self, color:int) -> bool:
        king_position = self.FindKing(color)
        opponent_color = 1- color
        return self.IsSquareAttacked(king_position, opponent_color)
    
    def IsCheckmate(self, color:int) -> bool:
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

    def TranslateFen(self, fen:str) -> None:
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
        for character in fen:
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

            elif character in 'wb':
                MoveManager.turn = 0 if (character == 'b') else 1

        return pieces
    
    @staticmethod
    def create_piece(color:int, piece_type:str, pos:list[int]) -> 'Optional[Piece]':
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
        elif piece_type =='k':
            return King(color, pos)
        return None

class MoveManager:
    turn = 0

    @staticmethod
    def LegalMoves(piece:'Optional[Piece]', board:'Board') -> list[list[int]]:
        '''
        Given a piece and the board state, we can calulate their legal moves of the piece.
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
        attacking_squares = piece.attacking_squares(board)
        attacking_squares = [pos for pos in attacking_squares if ((0 <= pos[0]<= 7) and (0 <= pos[1]<= 7))]
        return attacking_squares

    @staticmethod
    def MovePiece(selected_piece:'Optional[Piece]', board:'Board', legal_moves: list[list[int]]) -> 'Optional[bool]':
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
        for piece in board.board:
            if piece.color == selected_piece.color:
                continue

            elif piece.position == position:
                board.board.remove(piece)
                del piece
                break

            # En-passant-takinator (makes it so that en-passant is possible)
            elif isinstance(piece, Pawn) and isinstance(selected_piece, Pawn):
                if piece.en_passant_able and piece.position[1] == selected_piece.position[1]: 
                    if abs(piece.position[0] - selected_piece.position[0]) == 1:
                        board.board.remove(piece)
                        del piece
                    break

        # move-rookinator (moves rook after castling)
        if isinstance(selected_piece, King):
            castling_file = -1
            rook = selected_piece

            # king-sided castling
            if rank == 6:
                castling_file = 7
                for possible_rook in board.board:
                    if possible_rook.position[0] == castling_file  and possible_rook.position[1] == selected_piece.position[1] and \
                    isinstance(possible_rook, Rook) and possible_rook.color == selected_piece.color:
                        rook = possible_rook
                        break
                # move the rook
                rook.position[0] -= 2
                rook.rect.x = rook.position[0] * SQUARE_SIZE

            elif rank == 2:
                castling_file = 0
                for possible_rook in board.board:
                    if possible_rook.position[0] == castling_file  and possible_rook.position[1] == selected_piece.position[1] and \
                    isinstance(possible_rook, Rook) and possible_rook.color == selected_piece.color:
                        rook = possible_rook
                        break
                # move the rook
                rook.position[0] += 3
                rook.rect.x = rook.position[0] * SQUARE_SIZE

    
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

    def attacking_squares(self, board: Board) -> list[list[int]]:
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

def draw(board:Board, legal_moves:list[list[int]]) -> None:
    board.DrawBoard()
    board.DrawSelectedSquares(legal_moves)
    board.DrawPieces()
    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    board = Board()
    board.TranslateFen(STARTING_FEN)
    legal_moves = []
    selected_piece:'Optional[Piece]' = None
    endgame = None
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for piece in board.board:
                    if piece.rect.collidepoint(event.pos):
                        selected_piece = piece
                        legal_moves = MoveManager.LegalMoves(selected_piece, board)
            
            if event.type == pygame.MOUSEMOTION:
                if selected_piece is not None:
                    selected_piece.rect.move_ip(event.rel)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                endgame = MoveManager.MovePiece(selected_piece, board, legal_moves)
                selected_piece = None
                legal_moves = []

            if isinstance(endgame, bool):
                color = 'white' if endgame else 'black'
                print(f'{color} won')
                run = False

        draw(board, legal_moves)
    pygame.quit()

if __name__ == '__main__':
    main()
