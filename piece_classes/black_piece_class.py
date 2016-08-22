from globals_file import *

class BlackPiece():
	def __init__(self, x, y, white, index, piece_type):
		self.x = x
		self.y = y
		self.eightx_y = 8*x+y
		self.white = white
		self.moves = 0
		self.index = index
		self.type = piece_type

		squares[self.eightx_y].occupied_by = self.index

	def move_piece(self, x, y):
		# If it's not a pawn, increment the halfmove clock
		if self.type != 5:
			board.halfmove_clock += 1

		board.all_black_positions += 1 << 8*x+y

		# Leave the current square
		self.leave_square()

		# Kill the opposing piece, if any
		if squares[8*x+y].occupied_by != 0:
			pieces[squares[8*x+y].occupied_by].leave_square(True)

		# Reset en passant variables
		board.en_passant = False
		board.en_passant_pieces = []
		board.en_passant_victim = 0

		# Reset last move variables
		board.last_move_piece_type = self.type
		board.last_move_origin_eightx_y = self.eightx_y
		board.last_move_destination_eightx_y = 8*x+y

		#update current piece coordinates
		self.x = x
		self.y = y
		self.eightx_y = 8*x+y

		#update occupied status of target square
		squares[8*x+y].occupied_by = self.index

	# This method is overwritten by the black rook class, to deal with castling.
	def leave_square(self, captured = False):
		#logger.log('piece.leave_square')
		squares[self.eightx_y].occupied_by = 0

		board.all_black_positions -= 1 << squares[self.eightx_y].bitwise_position
		if captured:
			board.active_black_pieces -= self.index
			board.halfmove_clock = 0

	# This is an interface method that is overwritten by every type of piece
	def calculate_moves(self):
		dummy = 1

	def add_moves_to_all_move_bitboard(self, board):
		board.all_black_moves = board.all_black_moves | self.moves

	def calculate_file_moves(self):
		occupancy = (board.all_piece_positions >> (8 * self.x)) & 255

		potential_moves = board.file_bitboards[self.y][occupancy] << 8 * self.x

		self.moves += potential_moves & ~board.all_black_positions

		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)

	def calculate_rank_moves(self):
		occupancy = (board.all_piece_positions >> self.y) & 0x101010101010101
		potential_moves = board.rank_bitboards[occupancy][self.x] << self.y

		self.moves += potential_moves & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)

	def calculate_a1_h8_diagonal_moves(self):
		bitshift_amount = squares[self.eightx_y].a1_h8_bitshift_amount
		position = squares[self.eightx_y].a1_h8_position
		length = squares[self.eightx_y].a1_h8_length

		occupancy = (board.all_piece_positions >> bitshift_amount) & 0x8040201008040201
		potential_moves = (board.a1_h8_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)

	def calculate_a8_h1_diagonal_moves(self):
		bitshift_amount = squares[self.eightx_y].a8_h1_bitshift_amount
		position = squares[self.eightx_y].a8_h1_position
		length = squares[self.eightx_y].a8_h1_length

		if bitshift_amount < 0:
			occupancy = (board.all_piece_positions << abs(bitshift_amount)) & 0x102040810204080
			potential_moves = (board.a8_h1_diagonal_bitboards[occupancy][position] & length) >> abs(bitshift_amount)
		else:
			occupancy = (board.all_piece_positions >> bitshift_amount) & 0x102040810204080
			potential_moves = (board.a8_h1_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)
