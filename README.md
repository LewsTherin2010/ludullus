Ludullus
========
Ludullus is chess engine written in Python. "Ludullus" is a diminutive form of the Latin word "ludus", which means "game". So, it's a little game.

Screenshot
==========
![Screenshot](https://cloud.githubusercontent.com/assets/3838367/18210411/592c9e90-7106-11e6-83af-a51321de8f6d.png)

Features
========
Right now the engine is pretty weak, but it's in active development, and it's getting stronger pretty quickly.

1. Bitboard-based move generation.
2. A custom UI.
3. The ability to play against a computer as white or black, or against no computer at all.
4. The ability to start a game from a FEN string, with a computer opponent, or with none.
5. A [perft](https://chessprogramming.wikispaces.com/Perft) function.
6. Alpha-beta pruning search with a transposition table and iterative deepening.

Commands
========

Once the files have been checked out, it can be started with the following commands:

"python chessboard.py {white/black}" - Begins the program with the starting position, with the computer optionally playing black or white.

"python chessboard.py fen [FEN] {white/black}" - Begins the program in a position dictated by a string in Forsyth-Edwards notation. (https://www.chessclub.com/user/help/PGN-spec, section 16.1) Optionally, the computer will play black or white.

"python chessboard.py perft [FEN] [DEPTH] - This command will start the program in a position dictated by a FEN string, and calculate perft to a specific depth"

Limitations
===========

1. It's written in Python, which I'm beginning to suspect puts a ceiling on its performance. Right now, the move generation clocks in at about 400,000 positions per second in the perft function, which I think is at least an order of magnitude slower than other engines, for instance [weak](https://github.com/lorenzo-stoakes/weak) by Lorenzo Stoaks, who is a very friendly and helpful man. During search with evaluation, it clocks in at around 10,000 positions per second. (The difference because it has to make the move, evaluate the position, then unmake the move, whereas the perft function can just count the leaf nodes.)

2. Evaluation is the sum of the pieces on the board. The white pieces have positive values, and the black pieces have negative values.

Whither Ludullus?
=================

1. Running this program on my computer does not use all available processing power. I think it's just using one core, and I know my machine has 4 cores. So, I think I can quadruple performance by working more intelligently with the machine.

2. Position-based evaluation?!?!?