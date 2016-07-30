from black_piece_class import *

class BlackBishop(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()

		board.all_black_moves = board.all_black_moves | self.moves
