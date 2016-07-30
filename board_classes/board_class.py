from logger_class import *

class Board():
	def __init__(self):
		self.nodes = 0

		# Piece variables
		self.piece_type_definitions = {0:'King', 1:'Queen', 2:'Rook', 3:'Bishop', 4:'Knight', 5:'Pawn'}
		self.piece_indexes = [1<<x for x in range(32)]
		self.piece_values = {1<<0:1, 1<<1:1, 1<<2:1, 1<<3:1, 1<<4:1, 1<<5:1, 1<<6:1, 1<<7:1, 1<<8:-1, 1<<9:-1, 1<<10:-1, 1<<11:-1, 1<<12:-1, 1<<13:-1, 1<<14:-1, 1<<15:-1, 1<<16:5, 1<<17:5, 1<<18:-5, 1<<19:-5, 1<<20:3, 1<<21:3, 1<<22:-3, 1<<23:-3, 1<<24:3, 1<<25:3, 1<<26:-3, 1<<27:-3, 1<<28: 9, 1<<29:-9, 1<<30:10000, 1<<31:-10000}
		
		self.all_white_pieces = 0x533300ff # 16 bits
		self.all_black_pieces = 0xacccff00 # 32 bits

		self.black_pinners = set([1<<29, 1<<18, 1<<19, 1<<26, 1<<27]) # Queen, rooks, and bishops
		self.white_pinners = set([1<<28, 1<<16, 1<<17, 1<<24, 1<<25]) # Queen, rooks, and bishops

		self.active_white_pieces = 0x533300ff # 16 bits
		self.active_black_pieces = 0xacccff00 # 32 bits

		# En passant variables
		self.en_passant = False
		self.en_passant_pieces = []
		self.en_passant_victim = 9999

		# Move variables
		self.white_to_move = True

		self.last_move_piece_type = -1
		self.last_move_origin_x = -1
		self.last_move_origin_y = -1
		self.last_move_destination_x = -1
		self.last_move_destination_y = -1

		# Check variables
		self.checker_types = []
		self.checker_positions = []

		###### BOARD STATE BITBOARDS ######
		self.all_white_moves = 0
		self.all_black_moves = 0

		self.all_defended_white_pieces = 0
		self.all_defended_black_pieces = 0

		self.all_white_positions = 0x303030303030303
		self.all_black_positions = 0xc0c0c0c0c0c0c0c0

		self.all_piece_positions = 0

		self.white_removed_pin_moves = 0
		self.black_removed_pin_moves = 0

		self.unrealized_white_pawn_attacks = 0
		self.unrealized_black_pawn_attacks = 0

		self.third_rank_shifted_to_fourth = 0 # For use in calculating white pawns' first moves
		self.sixth_rank_shifted_to_fifth = 0 # For use in calculating black pawns' first moves

		###### REFERENCE BITBOARDS ######
		# The file_bitboards array should be accessed with the convention file_bitboards[y][occupancy]
		# It stores all move possibilities for the A column, given the piece's position in that column (y)
		# and the configuration of other pieces in the column (occupancy)
		self.file_bitboards = [[0 for occupancy in range(256)] for position in range(8)]

		self.rank_bitboards = {}

		self.a1_h8_diagonal_bitboards = {}
		self.a8_h1_diagonal_bitboards = {}

		# Knight move bitboards
		self.knight_move_bitboards = [[int(0) for y in range(8)] for x in range(8)]

		# King move bitboards
		self.king_move_bitboards = [[0 for y in range(8)] for x in range(8)]

		# Pawn move bitboards
		self.white_pawn_moves = [[0 for y in range(8)] for x in range(8)]
		self.black_pawn_moves = [[0 for y in range(8)] for x in range(8)]

		self.white_pawn_attacks = [[0 for y in range(8)] for x in range(8)]
		self.black_pawn_attacks = [[0 for y in range(8)] for x in range(8)]

		# X 1 1 1 1 1 1 X 		X 0 0 0 0 0 0 0 	 0 0 0 0 0 0 0 0
		# 0 0 0 0 0 0 0 0		0 1 0 0 0 0 0 0		 0 0 0 0 X 0 0 0
		# 0 0 0 0 0 0 0 0		0 0 1 0 0 0 0 0		 0 0 0 0 1 0 0 0 
		# 0 0 0 0 0 0 0 0		0 0 0 1 0 0 0 0		 0 0 0 0 1 0 0 0
		# 0 0 0 0 0 0 0 0  OR 	0 0 0 0 1 0 0 0  OR  0 0 0 0 1 0 0 0
		# 0 0 0 0 0 0 0 0		0 0 0 0 0 1 0 0		 0 0 0 0 1 0 0 0 
		# 0 0 0 0 0 0 0 0		0 0 0 0 0 0 1 0      0 0 0 0 X 0 0 0
		# 0 0 0 0 0 0 0 0		0 0 0 0 0 0 0 X      0 0 0 0 0 0 0 0
		self.intervening_squares_bitboards = {}

		# Run init functions
		self.initialize_knight_bitboards()
		self.initialize_king_bitboards()
		self.initialize_pawn_bitboards()
		self.initialize_file_bitboards()
		self.initialize_rank_bitboards()
		self.initialize_a1_h8_diagonal_bitboards()
		self.initialize_a8_h1_diagonal_bitboards()
		self.initialize_intervening_square_bitboards()

	def get_position(self, squares):
		#logger.log('board.get_position')

		position = [[9999 for x in range(8)] for y in range(8)]

		for x in range (0, 8):
			for y in range(0, 8):
				position[x][y] = squares[x][y].occupied_by

		return position

	def evaluate_position(self, position):
		#logger.log('board.evaluate_position')

		position_value = 0

		for x in range(8):
			for y in range(8):
				if position[x][y] != 9999:
					position_value += self.piece_values[position[x][y]]

		self.nodes += 1

		return position_value

	def erase_all_bitboards(self):
		#logger.log('board.erase_all_bitboards')

		self.all_white_moves = 0
		self.all_black_moves = 0
		self.all_piece_positions = 0
		self.all_defended_white_pieces = 0
		self.all_defended_black_pieces = 0
		self.unrealized_white_pawn_attacks = 0
		self.unrealized_black_pawn_attacks = 0
		self.white_removed_pin_moves = 0
		self.black_removed_pin_moves = 0
		self.third_rank_shifted_to_fourth = 0
		self.sixth_rank_shifted_to_fifth = 0

	def reset_board_variables(self, position):
		#logger.log('board.reset_board_variables')

		# Reset checked variables
		self.checker_types = []
		self.checker_positions = []

	def initialize_knight_bitboards(self):
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
				self.knight_move_bitboards[x][y] = int(knight_moves)

	def initialize_king_bitboards(self):
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
				self.king_move_bitboards[x][y] = int(king_moves)

	# This function creates 2^11 words up to 8 bits in size, which in total equal 128 bytes.
	# Within a file, there are 8 (2^3) positions a piece can occupy.
	# Within a file, there are 256 (2^8) different configurations that pieces can form.
	# For each position and configuration (occupancy), there is a set of moves that a rook or queen can make. 
	# The ray piece's move calculation function will deal with discerning between friend and foe.
	# These are also used, along with bitboard rotation, to calculate rank moves as well.
	# Credit to Colin Frayn for an excellent explanation of this method (http://www.frayn.net/beowulf/theory.html#bitboards)
	def initialize_file_bitboards(self):
		for position in range(8):
			for occupancy in range(256):
				if position > 0:
					possible_move = position - 1
					while possible_move >= 0:
						if (1<<possible_move) & occupancy == 0:
							self.file_bitboards[position][occupancy] += 1<<possible_move
						else:
							self.file_bitboards[position][occupancy] += 1<<possible_move
							break

						possible_move -= 1

				if position < 7:
					possible_move = position + 1
					while possible_move <= 7:
						if (1<<possible_move) & occupancy == 0:
							self.file_bitboards[position][occupancy] += 1<<possible_move
						else:
							self.file_bitboards[position][occupancy] += 1<<possible_move
							break

						possible_move += 1

	# See comment for initialize_file_bitboards()
	# This must be accessed by self.rank_bitboards[occupancy][position]
	def initialize_rank_bitboards(self):
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
			self.rank_bitboards[occupancy] = [0 for x in range(8)]

		for occupancy in occupancy_array:
			for position in range(8):

				if position > 0:
					possible_move = position - 1
					while possible_move >= 0:
						self.rank_bitboards[occupancy][position] += 1<<(possible_move * 8)
						if (1 << (possible_move * 8)) & occupancy != 0:
							break

						possible_move -= 1

				if position < 7:
					possible_move = position + 1
					while possible_move <= 7:
						self.rank_bitboards[occupancy][position] += 1<<(possible_move * 8)
						if (1 << (possible_move * 8)) & occupancy != 0:
							break

						possible_move += 1

	# See comment for initialize_file_bitboards()
	# This must be accessed by self.a1_h8_diagonal_bitboards[occupancy][position]
	def initialize_a1_h8_diagonal_bitboards(self):
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
			self.a1_h8_diagonal_bitboards[occupancy] = [0 for x in range(8)]

		for occupancy in occupancy_array:
			for position in range(8):

				if position > 0:
					possible_move = position - 1
					while possible_move >= 0:
						self.a1_h8_diagonal_bitboards[occupancy][position] += 1<<(possible_move * 9)
						if (1 << (possible_move * 9)) & occupancy != 0:
							break

						possible_move -= 1

				if position < 7:
					possible_move = position + 1
					while possible_move <= 7:
						self.a1_h8_diagonal_bitboards[occupancy][position] += 1<<(possible_move * 9)
						if (1 << (possible_move * 9)) & occupancy != 0:
							break

						possible_move += 1

	# See comment for initialize_file_bitboards()
	# This must be accessed by self.a8_h1_diagonal_bitboards[occupancy][position]
	def initialize_a8_h1_diagonal_bitboards(self):
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
			self.a8_h1_diagonal_bitboards[occupancy] = [0 for x in range(8)]

		for occupancy in occupancy_array:
			for position in range(8):

				if position > 0:
					possible_move = position - 1
					while possible_move >= 0:
						self.a8_h1_diagonal_bitboards[occupancy][position] += 1<<((possible_move + 1) * 7)
						if (1 << ((possible_move + 1) * 7)) & occupancy != 0:
							break

						possible_move -= 1

				if position < 7:
					possible_move = position + 1
					while possible_move <= 7:
						self.a8_h1_diagonal_bitboards[occupancy][position] += 1<<((possible_move + 1) * 7)
						if (1 << ((possible_move + 1) * 7)) & occupancy != 0:
							break

						possible_move += 1

	def initialize_pawn_bitboards(self):
		# Calculate the white pawn moves
		for x in range(8):
			for y in range(8):
				if y == 1:
					self.white_pawn_moves[x][y] += 1 << (x * 8 + (y + 1))
					self.white_pawn_moves[x][y] += 1 << (x * 8 + (y + 2))
				if y > 1 and y < 7:
					self.white_pawn_moves[x][y] += 1 << (x * 8 + (y + 1))

		# Calculate the black pawn moves
		for x in range(8):
			for y in range(8):
				if y == 6:
					self.black_pawn_moves[x][y] += 1 << (x * 8 + (y - 1))
					self.black_pawn_moves[x][y] += 1 << (x * 8 + (y - 2))
				if y > 0 and y < 6:
					self.black_pawn_moves[x][y] += 1 << (x * 8 + (y - 1))

		# Calculate white pawn attacks
		for x in range(8):
			for y in range(8):
				if x > 0 and y > 0 and y < 7:
					self.white_pawn_attacks[x][y] += 1 << (x * 8 + (y - 7))
				if x < 7 and y > 0 and y < 7:
					self.white_pawn_attacks[x][y] += 1 << (x * 8 + (y + 9))

		# Calculate black pawn attacks
		for x in range(8):
			for y in range(8):
				if x > 0 and y < 7 and y > 0:
					self.black_pawn_attacks[x][y] += 1 << (x * 8 + (y - 9))
				if x < 7 and y < 7 and y > 0:
					self.black_pawn_attacks[x][y] += 1 << (x * 8 + (y + 7))

	def shift_third_rank_to_fourth(self, original_bitboard):
		return (original_bitboard & 0x404040404040404) << 1

	def shift_sixth_rank_to_fifth(self, original_bitboard):
		return (original_bitboard & 0x2020202020202020) >> 1

	# This may be quite a large array. For every combination of two squares on a line, it will store 
	# all squares between those two. The keys of the array will be bitboard representations of the two
	# squares.
	#
	# In order to calculate these boards, I will add the keys in four loops: one for pairs on files,
	# one for pairs on ranks, one for pairs on A1H8 diagonals, and one for pairs on A8H1 diagonals.
	def initialize_intervening_square_bitboards(self):
		# Files loop
		for first_square in range(64):
			for second_square in range(64):
				if first_square < second_square and first_square // 8 == second_square // 8:
					key = (1 << first_square) + (2 << second_square)

					i = first_square + 1
					bitboard = 0
					while i < second_square:
						bitboard += 1 << i
						i += 1

					if bitboard != 0:
						self.intervening_squares_bitboards[key] = bitboard

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
						self.intervening_squares_bitboards[key] = bitboard

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
						self.intervening_squares_bitboards[key] = bitboard

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
						self.intervening_squares_bitboards[key] = bitboard