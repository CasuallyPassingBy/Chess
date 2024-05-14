import pygame
from pieces import Piece
from board import Board, MoveManager
from constants import WIDTH,HEIGHT,SQUARE_SIZE
from typing import Optional

pygame.font.init()

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
# [x] pawn promotion

def draw(board:Board, legal_moves:list[list[int]]) -> None:
    board.DrawBoard()
    board.DrawSelectedSquares(legal_moves)
    board.DrawPieces()
    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    board = Board(WIN, IMAGES)
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
