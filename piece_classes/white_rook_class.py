from white_piece_class import *

class WhiteRook(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	# When a rook moves for the first time, he needs to update his king to let the king know that he may not castle.
	# Otherwise, a rook moves normally
	def move_piece(self, x, y):
		#logger.log('rook.move_piece')
		if self.index == 1<<17:
			pieces[1<<30].castle_h = False
		else:
			pieces[1<<30].castle_a = False

		WhitePiece.move_piece(self, x, y)

	def calculate_moves(self):
		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		board.all_white_moves = board.all_white_moves | self.moves
