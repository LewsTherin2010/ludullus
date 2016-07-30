from white_piece_class import *
from logger_class import *

class WhiteBishop(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()

		board.all_white_moves = board.all_white_moves | self.moves
