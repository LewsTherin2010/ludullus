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
		if self.x == 7 and self.y == 7:
			pieces[1<<31].castle_h = False
		elif self.x == 0 and self.y == 7:
			pieces[1<<31].castle_a = False

		BlackPiece.leave_square(self, captured)