from white_piece_class import *

class WhiteRook(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		board.all_white_moves = board.all_white_moves | self.moves

	# Whenever a rook leaves a square (captured or not), shut off the castle.
	def leave_square(self, captured = False):
		if self.index == 1<<17:
			pieces[1<<30].castle_h = False
		else:
			pieces[1<<30].castle_a = False

		WhitePiece.leave_square(self, captured)