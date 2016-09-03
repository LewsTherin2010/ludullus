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

Commands
========

Once the files have been checked out, it can be started with the following commands:

"python chessboard.py {white/black}" - Begins the program with the starting position, with the computer optionally playing black or white.

"python chessboard.py fen [FEN] {white/black}" - Begins the program in a position dictated by a string in Forsyth-Edwards notation. (https://www.chessclub.com/user/help/PGN-spec, section 16.1) Optionally, the computer will play black or white.

"python chessboard.py perft [FEN] [DEPTH] - This command will start the program in a position dictated by a FEN string, and calculate perft to a specific depth"

Limitations
===========

1. It's written in Python, which I'm beginning to suspect puts a ceiling on its performance. Right now, the move generation clocks in at about 350,000 positions per second in the perft function, which I think is at least an order of magnitude slower than other engines, for instance [weak](https://github.com/lorenzo-stoakes/weak) by Lorenzo Stoaks, who is a very friendly and helpful man. During search with evaluation, it clocks in at about 55,000 positions per second. (The difference because it has to make the move, evaluate the position, then unmake the move, whereas the perft function can just count the leaf nodes.)

2. Search is alpha-beta pruning.

3. Evaluation is the sum of the pieces on the board. The white pieces have positive values, and the black pieces have negative values.

4. There are a couple open issues. 

5. The perft function, calculated from the start position, is off by 18 at perft(5).

6. The branch called stringboard is completely broken at the moment, due to on-going development.

Whither Ludullus?
=================

1. After I'm done rewriting it with the board represented as a string, and I've confirmed that the string representation does perform faster than the array representation (I am uncertain), I will hopefully merge the stringboard branch back into the master branch.

2. A big reason for switching to a string representation is the use of a hash table, which will hopefully allow me to add a couple plies of depth to the search.

3. The engine has a huge problem with horizon effects at the moment. For example, right now it is capable of playing a game within a reasonable time frame using an alpha-beta search at depth 4. But, this usually means that the last move that the computer sees has been played by its opponent. It happens quite often, then, that the computer thinks that, whatever it does, it's going to end up losing material, and so the computer becomes indifferent to the move it has to make now, and blunders. I'm hoping that implementing iterative deepening, which is typicallly used to speed up the alpha-beta search, will address this problem as well. If the moves of the first ply are ordered by position value, and then searched to whatever depth, then even if the computer is ultimately indifferent, at least it will not choose a move that will immediately cause it to lose material. I think the canonical method of dealing with the horizon effect is a quiescence search, but honestly that sounds like overkill for this simple problem.

4. Right now, running this program on my computer does not use all available processing power. I think it's just using one core, and I know my machine has 4 cores. So, I think I can quadruple performance by working more intelligently with the machine.

5. Position-based evaluation?!?!?