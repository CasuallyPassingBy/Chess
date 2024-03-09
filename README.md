# Pygame Chess Implementation

This is a Python implementation of a chess game using the Pygame library. The game allows players to play against each other on a graphical chessboard.

## Features

- Fully functional chess game with legal moves, check, and checkmate detection.
- Graphical interface using Pygame for an interactive gaming experience.
- Implements standard chess rules, including castling, en passant, and pawn promotion.
- Supports loading custom chess piece images.
- Parses FEN (Forsyth–Edwards Notation) to initialize the board with custom starting positions.

## Requirements

- Python 3.x
- Pygame library (`pip install pygame`)

## Usage

1. Clone the repository or download the source code.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the `main.py` script to start the game.

## How to Play

- Click on a chess piece to select it.
- Legal moves for the selected piece will be highlighted.
- Click on a highlighted square to move the selected piece.
- The game will automatically detect check and checkmate conditions.
- Enjoy playing chess!

## Customization

- Modify the `STARTING_FEN` variable in `main.py` to set custom starting positions.
- Replace the default chess piece images with your own images by placing them in the `pieces_svgs` directory and updating the file paths in the code.

## Contributors

- [Mauricio Moscoso](https://github.com/CasuallyPassingBy)

## Acknowledgments

- Thanks to the creators of the Pygame library for providing a powerful framework for game development in Python.
- Inspired by various online resources and tutorials on chess programming and game development.
