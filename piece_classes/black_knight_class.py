from black_piece_class import *

class BlackKnight(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	# The board stores 64 bitboards for knight moves, 1 for the set of moves a knight can make from each square.
	# I store them in the board, rather than in the piece, because if they were stored in the piece, then there would
	# be a copy of all the bitboards for each knight.
	def calculate_moves(self):
		self.moves = board.knight_move_bitboards[self.eightx_y] & ~board.all_black_positions
		board.all_defended_black_pieces = board.all_defended_black_pieces | (board.knight_move_bitboards[self.eightx_y] & board.all_black_positions)

		board.all_black_moves = board.all_black_moves | self.moves
