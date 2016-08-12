from globals_file import *

class BlackPiece():
	def __init__(self, x, y, white, index, piece_type):
		self.x = x
		self.y = y
		self.white = white
		self.moves = 0
		self.index = index
		self.type = piece_type

		squares[x][y].occupied_by = self.index

	def move_piece(self, x, y):
		board.all_black_positions += 1 << squares[x][y].bitwise_position

		# Leave the current square
		self.leave_square()

		# Kill the opposing piece, if any
		if squares[x][y].occupied_by != 9999:
			pieces[squares[x][y].occupied_by].leave_square(True)

		# Reset en passant variables
		board.en_passant = False
		board.en_passant_pieces = []
		board.en_passant_victim = 9999

		# Reset last move variables
		board.last_move_piece_type = self.type
		board.last_move_origin_x = self.x
		board.last_move_origin_y = self.y
		board.last_move_destination_x = x
		board.last_move_destination_y = y

		#update current piece coordinates
		self.x = x
		self.y = y

		#update occupied status of target square
		squares[x][y].occupied_by = self.index

	# This method is overwritten by the black rook class, to deal with castling.
	def leave_square(self, captured = False):
		#logger.log('piece.leave_square')
		squares[self.x][self.y].occupied_by = 9999

		board.all_black_positions -= 1 << squares[self.x][self.y].bitwise_position
		if captured:
			board.active_black_pieces -= self.index

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
		bitshift_amount = squares[self.x][self.y].a1_h8_bitshift_amount
		position = squares[self.x][self.y].a1_h8_position
		length = squares[self.x][self.y].a1_h8_length

		occupancy = (board.all_piece_positions >> bitshift_amount) & 0x8040201008040201
		potential_moves = (board.a1_h8_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)

	def calculate_a8_h1_diagonal_moves(self):
		bitshift_amount = squares[self.x][self.y].a8_h1_bitshift_amount
		position = squares[self.x][self.y].a8_h1_position
		length = squares[self.x][self.y].a8_h1_length

		if bitshift_amount < 0:
			occupancy = (board.all_piece_positions << abs(bitshift_amount)) & 0x102040810204080
			potential_moves = (board.a8_h1_diagonal_bitboards[occupancy][position] & length) >> abs(bitshift_amount)
		else:
			occupancy = (board.all_piece_positions >> bitshift_amount) & 0x102040810204080
			potential_moves = (board.a8_h1_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)
