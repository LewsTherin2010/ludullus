from black_piece_class import *

class BlackRook(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	# When a rook moves for the first time, he needs to update his king to let the king know that he may not castle.
	# Otherwise, a rook moves normally
	def move_piece(self, x, y):
		if self.index == 1<<19:
			pieces[1<<31].castle_h = False
		else:
			pieces[1<<31].castle_a = False

		BlackPiece.move_piece(self, x, y)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		board.all_black_moves = board.all_black_moves | self.moves
