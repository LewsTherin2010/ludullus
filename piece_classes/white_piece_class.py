from globals_file import *
from constant_bitboards import *

class WhitePiece():
	def __init__(self, x, y, white, index, piece_type):
		self.eightx_y = 8*x+y
		self.white = white
		self.moves = 0
		self.index = index
		self.type = piece_type

		squares[self.eightx_y].occupied_by = self.index

	def move_piece(self, eightx_y):
		# If it's not a pawn, increment the halfmove clock
		if self.type != 5:
			board.halfmove_clock += 1

		board.all_white_positions += 1 << eightx_y

		# Leave the current square
		self.leave_square()

		# Kill the opposing piece, if any
		if squares[eightx_y].occupied_by != 0:
			pieces[squares[eightx_y].occupied_by].leave_square(True)

		# Reset en passant variables
		board.en_passant_pieces = []
		board.en_passant_victim = 0

		# Reset last move variables
		board.last_move_piece_type = self.type
		board.last_move_origin_eightx_y = self.eightx_y
		board.last_move_destination_eightx_y = eightx_y

		#update current piece coordinates
		self.eightx_y = eightx_y

		#update occupied status of target square
		squares[eightx_y].occupied_by = self.index

	# This method is overwritten by the white rook class, to deal with castling.
	def leave_square(self, captured = False):
		#logger.log('piece.leave_square')
		squares[self.eightx_y].occupied_by = 0

		board.all_white_positions -= 1 << self.eightx_y
		if captured:
			board.active_white_pieces -= self.index
			board.halfmove_clock = 0

	# This is an interface method that is overwritten by every type of piece
	def calculate_moves(self):
		dummy = 1

	def add_moves_to_all_move_bitboard(self, board):
		board.all_white_moves = board.all_white_moves | self.moves

	def calculate_file_moves(self):
		occupancy = (board.all_piece_positions >> (self.eightx_y - (self.eightx_y % 8))) & 255
		potential_moves = file_bitboards[self.eightx_y % 8][occupancy] << (self.eightx_y - (self.eightx_y % 8))

		self.moves += potential_moves & ~board.all_white_positions
		board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)

	def calculate_rank_moves(self):
		occupancy = (board.all_piece_positions >> (self.eightx_y % 8)) & 0x101010101010101
		potential_moves = rank_bitboards[occupancy][self.eightx_y // 8] << (self.eightx_y % 8)

		self.moves += potential_moves & ~board.all_white_positions
		board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)

	def calculate_a1_h8_diagonal_moves(self):
		bitshift_amount = squares[self.eightx_y].a1_h8_bitshift_amount
		position = squares[self.eightx_y].a1_h8_position
		length = squares[self.eightx_y].a1_h8_length

		occupancy = (board.all_piece_positions >> bitshift_amount) & 0x8040201008040201
		potential_moves = (a1_h8_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_white_positions
		board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)

	def calculate_a8_h1_diagonal_moves(self):
		bitshift_amount = squares[self.eightx_y].a8_h1_bitshift_amount
		position = squares[self.eightx_y].a8_h1_position
		length = squares[self.eightx_y].a8_h1_length

		if bitshift_amount < 0:
			occupancy = (board.all_piece_positions << abs(bitshift_amount)) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) >> abs(bitshift_amount)
		else:
			occupancy = (board.all_piece_positions >> bitshift_amount) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~board.all_white_positions
		board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)

