# ludullus
A DIY python-based chess engine.

Ludullus is a diminutive form of the Latin word "ludus", which means "game". So, it's a little game. It's an original and unique chess engine.

Once the files have been checked out, it can be started with the following commands:

"python chessboard.py {white/black}" - Begins the program with the starting position, with the computer optionally playing black or white.

"python chessboard.py fen [FEN] {white/black}" - Begins the program in a position dictated by a string in Forsyth-Edwards notation. (https://www.chessclub.com/user/help/PGN-spec, section 16.1) Optionally, the computer will play black or white.

"python chessboard.py perft [FEN] [DEPTH] - This command with start the program in a position dictated by a FEN string, and calculate perft to a specific depth"