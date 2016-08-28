# ****************************************
# ************** FUNCTIONS ***************
# ****************************************

# This may be quite a large array. For every combination of two squares on a line, it will store 
# all squares between those two. The keys of the array will be bitboard representations of the two
# squares.
#
# In order to calculate these boards, I will add the keys in four loops: one for pairs on files,
# one for pairs on ranks, one for pairs on A1H8 diagonals, and one for pairs on A8H1 diagonals.
def initialize_intervening_square_bitboards():
	global intervening_squares_bitboards
	# Files loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and first_square // 8 == second_square // 8:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 1
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 1

				if bitboard != 0:
					intervening_squares_bitboards[key] = bitboard

	# Ranks loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and first_square % 8 == second_square % 8:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 8
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 8

				if bitboard != 0:
					intervening_squares_bitboards[key] = bitboard

	# A1H8 diagonals loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and (second_square - first_square) % 9 == 0:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 9
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 9

				if bitboard != 0:
					intervening_squares_bitboards[key] = bitboard

	# A8H1 diagonals loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and (second_square - first_square) % 7 == 0:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 7
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 7

				if bitboard != 0:
					intervening_squares_bitboards[key] = bitboard

def initialize_intervening_square_rank_and_file_bb():
	global intervening_squares_rank_and_file_bb

	# Files loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and first_square // 8 == second_square // 8:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 1
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 1

				if bitboard != 0:
					intervening_squares_rank_and_file_bb[key] = bitboard

	# Ranks loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and first_square % 8 == second_square % 8:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 8
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 8

				if bitboard != 0:
					intervening_squares_rank_and_file_bb[key] = bitboard

def initialize_intervening_square_diagonal_bb():
	global intervening_squares_diagonal_bb

	# A1H8 diagonals loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and (second_square - first_square) % 9 == 0:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 9
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 9

				if bitboard != 0:
					intervening_squares_diagonal_bb[key] = bitboard

	# A8H1 diagonals loop
	for first_square in range(64):
		for second_square in range(64):
			if first_square < second_square and (second_square - first_square) % 7 == 0:
				key = (1 << first_square) + (1 << second_square)

				i = first_square + 7
				bitboard = 0
				while i < second_square:
					bitboard += 1 << i
					i += 7

				if bitboard != 0:
					intervening_squares_diagonal_bb[key] = bitboard



def initialize_knight_bitboards():
	for x in range(8):
		for y in range(8):

			# Conditions are necessary to ensure that the knight neither "wraps around" rows nor goes off the board
			# A1 = 2^0; H8 = 2^63
			piece_location = 1<<(8 * x + y)
			knight_moves = 0

			# Up two, left one (from white's perspective)
			if x > 0 and y < 6:
				knight_moves += piece_location / 0x40
			# Up two, right one (from white's perspective)
			if x < 7 and y < 6:
				knight_moves += piece_location * 0x400
			# Up one, right two (from white's perspective)
			if x < 6 and y < 7:
				knight_moves += piece_location * 0x20000
			# Down one, right two (from white's perspective)
			if x < 6 and y > 0:
				knight_moves += piece_location * 0x8000
			# Down two, right one (from white's perspective)
			if x < 7 and y > 1:
				knight_moves += piece_location * 0x40
			# Down two, left one (from white's perspective)
			if x > 0 and y > 1:
				knight_moves += piece_location / 0x400
			# Down one, left two (from white's perspective)
			if x > 1 and y > 0:
				knight_moves += piece_location / 0x20000
			# Done one right two (from white's perspective)
			if x > 1 and y < 7:
				knight_moves += piece_location / 0x8000

			knight_move_bitboards[8 * x + y] = int(knight_moves)

def initialize_king_bitboards():
	for x in range(8):
		for y in range(8):

			# Conditions are necessary to ensure that the king doesn't fall off the edge of the board
			# A1 = 2^0; H8 = 2^63
			piece_location = 1<<(8 * x + y)
			king_moves = 0

			# Up left (from white's perspective)
			if x > 0 and y < 7:
				king_moves += piece_location / (1<<7)
			# Up (from white's perspective)
			if y < 7:
				king_moves += piece_location * 2
			# Up right (from white's perspective)
			if x < 7 and y < 7:
				king_moves += piece_location * (1<<9)
			# Right (from white's perspective)
			if x < 7:
				king_moves += piece_location * (1<<8)
			# Down right (from white's perspective)
			if x < 7 and y > 0:
				king_moves += piece_location * (1<<7)
			# Down (from white's perspective)
			if y > 0:
				king_moves += piece_location / (1<<1)
			# Down left (from white's perspective)
			if x > 0 and y > 0:
				king_moves += piece_location / (1<<9)
			# Left (from white's perspective)
			if x > 0:
				king_moves += piece_location / (1<<8)
			king_move_bitboards[8*x+y] = int(king_moves)


def initialize_pawn_bitboards():
	# Calculate the white pawn moves
	for x in range(8):
		for y in range(8):
			if y == 1:
				white_pawn_moves[8*x+y] += 1 << (x * 8 + (y + 1))
				white_pawn_moves[8*x+y] += 1 << (x * 8 + (y + 2))
			if y > 1 and y < 7:
				white_pawn_moves[8*x+y] += 1 << (x * 8 + (y + 1))

	# Calculate the black pawn moves
	for x in range(8):
		for y in range(8):
			if y == 6:
				black_pawn_moves[8*x+y] += 1 << (x * 8 + (y - 1))
				black_pawn_moves[8*x+y] += 1 << (x * 8 + (y - 2))
			if y > 0 and y < 6:
				black_pawn_moves[8*x+y] += 1 << (x * 8 + (y - 1))

	# Calculate white pawn attacks
	for x in range(8):
		for y in range(8):
			if x > 0 and y > 0 and y < 7:
				white_pawn_attacks[8*x+y] += 1 << (x * 8 + (y - 7))
			if x < 7 and y > 0 and y < 7:
				white_pawn_attacks[8*x+y] += 1 << (x * 8 + (y + 9))

	# Calculate black pawn attacks
	for x in range(8):
		for y in range(8):
			if x > 0 and y < 7 and y > 0:
				black_pawn_attacks[8*x+y] += 1 << (x * 8 + (y - 9))
			if x < 7 and y < 7 and y > 0:
				black_pawn_attacks[8*x+y] += 1 << (x * 8 + (y + 7))


# This function creates 2^11 words up to 8 bits in size, which in total equal 128 bytes.
# Within a file, there are 8 (2^3) positions a piece can occupy.
# Within a file, there are 256 (2^8) different configurations that pieces can form.
# For each position and configuration (occupancy), there is a set of moves that a rook or queen can make. 
# The ray piece's move calculation function will deal with discerning between friend and foe.
# These are also used, along with bitboard rotation, to calculate rank moves as well.
# Credit to Colin Frayn for an excellent explanation of this method (http://www.frayn.net/beowulf/theory.html#bitboards)
def initialize_file_bitboards():
	for position in range(8):
		for occupancy in range(256):
			if position > 0:
				possible_move = position - 1
				while possible_move >= 0:
					if (1<<possible_move) & occupancy == 0:
						file_bitboards[position][occupancy] += 1<<possible_move
					else:
						file_bitboards[position][occupancy] += 1<<possible_move
						break

					possible_move -= 1

			if position < 7:
				possible_move = position + 1
				while possible_move <= 7:
					if (1<<possible_move) & occupancy == 0:
						file_bitboards[position][occupancy] += 1<<possible_move
					else:
						file_bitboards[position][occupancy] += 1<<possible_move
						break

					possible_move += 1


# See comment for initialize_file_bitboards()
# This must be accessed by rank_bitboards[occupancy][position]
def initialize_rank_bitboards():
	square_array = [1<<0, 1<<8, 1<<16, 1<<24, 1<<32, 1<<40, 1<<48, 1<<56]

	occupancy_array = []

	for a in range(2):
		for b in range(2):
			for c in range(2):
				for d in range(2):
					for e in range(2):
						for f in range(2):
							for g in range(2):
								for h in range(2):
									occupancy_array.append(a*square_array[0] + b*square_array[1] + c*square_array[2] + d*square_array[3] + e*square_array[4] + f*square_array[5] + g*square_array[6] + h*square_array[7])

	for occupancy in occupancy_array:
		rank_bitboards[occupancy] = [0 for x in range(8)]

	for occupancy in occupancy_array:
		for position in range(8):

			if position > 0:
				possible_move = position - 1
				while possible_move >= 0:
					rank_bitboards[occupancy][position] += 1<<(possible_move * 8)
					if (1 << (possible_move * 8)) & occupancy != 0:
						break

					possible_move -= 1

			if position < 7:
				possible_move = position + 1
				while possible_move <= 7:
					rank_bitboards[occupancy][position] += 1<<(possible_move * 8)
					if (1 << (possible_move * 8)) & occupancy != 0:
						break

					possible_move += 1


# See comment for initialize_file_bitboards()
# This must be accessed by a1_h8_diagonal_bitboards[occupancy][position]
def initialize_a1_h8_diagonal_bitboards():
	square_array = [1<<0, 1<<9, 1<<18, 1<<27, 1<<36, 1<<45, 1<<54, 1<<63]

	occupancy_array = []

	for a in range(2):
		for b in range(2):
			for c in range(2):
				for d in range(2):
					for e in range(2):
						for f in range(2):
							for g in range(2):
								for h in range(2):
									occupancy_array.append(a*square_array[0] + b*square_array[1] + c*square_array[2] + d*square_array[3] + e*square_array[4] + f*square_array[5] + g*square_array[6] + h*square_array[7])

	for occupancy in occupancy_array:
		a1_h8_diagonal_bitboards[occupancy] = [0 for x in range(8)]

	for occupancy in occupancy_array:
		for position in range(8):

			if position > 0:
				possible_move = position - 1
				while possible_move >= 0:
					a1_h8_diagonal_bitboards[occupancy][position] += 1<<(possible_move * 9)
					if (1 << (possible_move * 9)) & occupancy != 0:
						break

					possible_move -= 1

			if position < 7:
				possible_move = position + 1
				while possible_move <= 7:
					a1_h8_diagonal_bitboards[occupancy][position] += 1<<(possible_move * 9)
					if (1 << (possible_move * 9)) & occupancy != 0:
						break

					possible_move += 1


# See comment for initialize_file_bitboards()
# This must be accessed by a8_h1_diagonal_bitboards[occupancy][position]
def initialize_a8_h1_diagonal_bitboards():
	square_array = [1<<7, 1<<14, 1<<21, 1<<28, 1<<35, 1<<42, 1<<49, 1<<56]

	occupancy_array = []

	for a in range(2):
		for b in range(2):
			for c in range(2):
				for d in range(2):
					for e in range(2):
						for f in range(2):
							for g in range(2):
								for h in range(2):
									occupancy_array.append(a*square_array[0] + b*square_array[1] + c*square_array[2] + d*square_array[3] + e*square_array[4] + f*square_array[5] + g*square_array[6] + h*square_array[7])

	for occupancy in occupancy_array:
		a8_h1_diagonal_bitboards[occupancy] = [0 for x in range(8)]

	for occupancy in occupancy_array:
		for position in range(8):

			if position > 0:
				possible_move = position - 1
				while possible_move >= 0:
					a8_h1_diagonal_bitboards[occupancy][position] += 1<<((possible_move + 1) * 7)
					if (1 << ((possible_move + 1) * 7)) & occupancy != 0:
						break

					possible_move -= 1

			if position < 7:
				possible_move = position + 1
				while possible_move <= 7:
					a8_h1_diagonal_bitboards[occupancy][position] += 1<<((possible_move + 1) * 7)
					if (1 << ((possible_move + 1) * 7)) & occupancy != 0:
						break

					possible_move += 1

def calculate_a1_h8_diagonal_bitboard_variables():
	for x in range(8):
		for y in range(8):
			if x - y == -7:
				a1_h8_bitshift_amounts.append(7)
				a1_h8_lengths.append(0b1)
				a1_h8_positions.append(x)
			elif x - y == -6:
				a1_h8_bitshift_amounts.append(6)
				a1_h8_lengths.append(0b1000000001)
				a1_h8_positions.append(x)
			elif x - y == -5:
				a1_h8_bitshift_amounts.append(5)
				a1_h8_lengths.append(0b1000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == -4:
				a1_h8_bitshift_amounts.append(4)
				a1_h8_lengths.append(0b1000000001000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == -3:
				a1_h8_bitshift_amounts.append(3)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == -2:
				a1_h8_bitshift_amounts.append(2)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == -1:
				a1_h8_bitshift_amounts.append(1)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == 0:
				a1_h8_bitshift_amounts.append(0)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001000000001000000001000000001)
				a1_h8_positions.append(x)
			elif x - y == 1:
				a1_h8_bitshift_amounts.append(8)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001000000001000000001)
				a1_h8_positions.append(y)
			elif x - y == 2:
				a1_h8_bitshift_amounts.append(16)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001000000001)
				a1_h8_positions.append(y)
			elif x - y == 3:
				a1_h8_bitshift_amounts.append(24)
				a1_h8_lengths.append(0b1000000001000000001000000001000000001)
				a1_h8_positions.append(y)
			elif x - y == 4:
				a1_h8_bitshift_amounts.append(32)
				a1_h8_lengths.append(0b1000000001000000001000000001)
				a1_h8_positions.append(y)
			elif x - y == 5:
				a1_h8_bitshift_amounts.append(40)
				a1_h8_lengths.append(0b1000000001000000001)
				a1_h8_positions.append(y)
			elif x - y == 6:
				a1_h8_bitshift_amounts.append(48)
				a1_h8_lengths.append(0b1000000001)
				a1_h8_positions.append(y)
			elif x - y == 7:
				a1_h8_bitshift_amounts.append(56)
				a1_h8_lengths.append(0b1)
				a1_h8_positions.append(y)

def calculate_a8_h1_diagonal_bitboard_variables():
	for x in range(8):
		for y in range(8):
			if x + y == 0:
				a8_h1_bitshift_amounts.append(-7)
				a8_h1_lengths.append(0b10000000)
				a8_h1_positions.append(x)
			elif x + y == 1:
				a8_h1_bitshift_amounts.append(-6)
				a8_h1_lengths.append(0b100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 2:
				a8_h1_bitshift_amounts.append(-5)
				a8_h1_lengths.append(0b1000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 3:
				a8_h1_bitshift_amounts.append(-4)
				a8_h1_lengths.append(0b10000001000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 4:
				a8_h1_bitshift_amounts.append(-3)
				a8_h1_lengths.append(0b100000010000001000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 5:
				a8_h1_bitshift_amounts.append(-2)
				a8_h1_lengths.append(0b1000000100000010000001000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 6:
				a8_h1_bitshift_amounts.append(-1)
				a8_h1_lengths.append(0b10000001000000100000010000001000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 7:
				a8_h1_bitshift_amounts.append(0)
				a8_h1_lengths.append(0b100000010000001000000100000010000001000000100000010000000)
				a8_h1_positions.append(x)
			elif x + y == 8:
				a8_h1_bitshift_amounts.append(8)
				a8_h1_lengths.append(0b10000001000000100000010000001000000100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 9:
				a8_h1_bitshift_amounts.append(16)
				a8_h1_lengths.append(0b1000000100000010000001000000100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 10:
				a8_h1_bitshift_amounts.append(24)
				a8_h1_lengths.append(0b100000010000001000000100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 11:
				a8_h1_bitshift_amounts.append(32)
				a8_h1_lengths.append(0b10000001000000100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 12:
				a8_h1_bitshift_amounts.append(40)
				a8_h1_lengths.append(0b1000000100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 13:
				a8_h1_bitshift_amounts.append(48)
				a8_h1_lengths.append(0b100000010000000)
				a8_h1_positions.append(7 - y)
			elif x + y == 14:
				a8_h1_bitshift_amounts.append(56)
				a8_h1_lengths.append(0b10000000)
				a8_h1_positions.append(7 - y)

# ****************************************
# ************ DECLARATIONS **************
# ****************************************

# X 1 1 1 1 1 1 X 		X 0 0 0 0 0 0 0 	 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0		0 1 0 0 0 0 0 0		 0 0 0 0 X 0 0 0
# 0 0 0 0 0 0 0 0		0 0 1 0 0 0 0 0		 0 0 0 0 1 0 0 0 
# 0 0 0 0 0 0 0 0		0 0 0 1 0 0 0 0		 0 0 0 0 1 0 0 0
# 0 0 0 0 0 0 0 0  OR 	0 0 0 0 1 0 0 0  OR  0 0 0 0 1 0 0 0
# 0 0 0 0 0 0 0 0		0 0 0 0 0 1 0 0		 0 0 0 0 1 0 0 0 
# 0 0 0 0 0 0 0 0		0 0 0 0 0 0 1 0      0 0 0 0 X 0 0 0
# 0 0 0 0 0 0 0 0		0 0 0 0 0 0 0 X      0 0 0 0 0 0 0 0
intervening_squares_bitboards = {}
initialize_intervening_square_bitboards()

intervening_squares_rank_and_file_bb = {}
initialize_intervening_square_rank_and_file_bb()

intervening_squares_diagonal_bb = {}
initialize_intervening_square_diagonal_bb()

# Knight move bitboards
knight_move_bitboards = [0 for x in range(64)]
initialize_knight_bitboards()

# King move bitboards
king_move_bitboards = [0 for x in range(64)]
initialize_king_bitboards()

# Pawn move bitboards
white_pawn_moves = [0 for x in range(64)]
black_pawn_moves = [0 for x in range(64)]

white_pawn_attacks = [0 for x in range(64)]
black_pawn_attacks = [0 for x in range(64)]
initialize_pawn_bitboards()

# The file_bitboards array should be accessed with the convention file_bitboards[y][occupancy]
# It stores all move possibilities for the A column, given the piece's position in that column (y)
# and the configuration of other pieces in the column (occupancy)
file_bitboards = [[0 for occupancy in range(256)] for position in range(8)]
initialize_file_bitboards()

# Rank bitboards
rank_bitboards = {}
initialize_rank_bitboards()

# Diagonal bitboards
a1_h8_diagonal_bitboards = {}
initialize_a1_h8_diagonal_bitboards()

a8_h1_diagonal_bitboards = {}
initialize_a8_h1_diagonal_bitboards()

a1_h8_bitshift_amounts = []
a1_h8_lengths = []
a1_h8_positions = []
calculate_a1_h8_diagonal_bitboard_variables()

a8_h1_bitshift_amounts = []
a8_h1_lengths = []
a8_h1_positions = []
calculate_a8_h1_diagonal_bitboard_variables()
