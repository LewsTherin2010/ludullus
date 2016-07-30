from globals_file import *
from white_piece_class import *
from white_queen_class import *

class WhitePawn(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def move_piece(self, x, y):
		#logger.log('pawn.move_piece')
		# ******* EN PASSANT ******* #
		# check to see if this pawn is performing en passant, and if so, remove the en passant victim from the board.
		if board.en_passant and self.index in board.en_passant_pieces and pieces[board.en_passant_victim].x == x:
			pieces[board.en_passant_victim].leave_square(True)

		WhitePiece.move_piece(self, x, y)

		# Queen promotion
		if y == 7:
			self.promote_to_queen()

	def calculate_moves(self):
		self.moves = board.white_pawn_moves[self.x][self.y] & ~board.all_piece_positions

		# The precalculated "third_rank_shifted_to_fourth" is used to prevent a pawn from hopping over a piece on its first move.
		if self.y == 1:
			self.moves = self.moves & ~board.third_rank_shifted_to_fourth

		# Deal with pawn attacks
		self.moves = self.moves + (board.white_pawn_attacks[self.x][self.y] & board.all_black_positions)
		board.all_defended_white_pieces = board.all_defended_white_pieces | (board.white_pawn_attacks[self.x][self.y] & board.all_white_positions)
		board.unrealized_white_pawn_attacks = board.unrealized_white_pawn_attacks | (board.white_pawn_attacks[self.x][self.y] & ~board.all_piece_positions)

		board.all_white_moves = board.all_white_moves | self.moves

	def promote_to_queen(self):

		# Leave the square
		self.leave_square(True)

		# Add a new white queen to the pieces array
		pieces.append(WhiteQueen(x, y, self.white, max(pieces).index + 1, 1))

		# Add queen to necessary bitboards



		max(pieces).calculate_moves()
