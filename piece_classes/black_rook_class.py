from black_piece_class import *

class BlackRook(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		board.all_black_moves = board.all_black_moves | self.moves

	# Whenever a rook leaves a square (captured or not), shut off the castle.
	def leave_square(self, captured = False):
		if self.eightx_y == 63:
			board.castles = board.castles & 0b1101
		elif self.eightx_y == 7:
			board.castles = board.castles & 0b1110

		BlackPiece.leave_square(self, captured)