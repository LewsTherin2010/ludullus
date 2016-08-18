from globals_file import *
from black_piece_class import *
from black_queen_class import *
import math

class BlackPawn(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def move_piece(self, x, y):
		#logger.log('pawn.move_piece')
		# ******* EN PASSANT ******* #
		# check to see if this pawn is performing en passant, and if so, remove the en passant victim from the board.
		if board.en_passant and self.index in board.en_passant_pieces and pieces[board.en_passant_victim].x == x:
			pieces[board.en_passant_victim].leave_square(True)

		BlackPiece.move_piece(self, x, y)

		# Queen promotion
		if y == 0:
			self.promote_to_queen(x, y)

		# Reset the halfmove clock
		board.halfmove_clock = 0

	def calculate_moves(self):
		self.moves = board.black_pawn_moves[self.x][self.y] & ~board.all_piece_positions

		# The precalculated "sixth_rank_shifted_to_fifth" is used to prevent a pawn from hopping over a piece on its first move.
		if self.y == 6:
			self.moves = self.moves & ~board.sixth_rank_shifted_to_fifth

		# Deal with pawn attacks
		self.moves = self.moves + (board.black_pawn_attacks[self.x][self.y] & board.all_white_positions)
		board.all_defended_black_pieces = board.all_defended_black_pieces | (board.black_pawn_attacks[self.x][self.y] & board.all_black_positions)
		board.unrealized_black_pawn_attacks = board.unrealized_black_pawn_attacks | (board.black_pawn_attacks[self.x][self.y] & ~board.all_piece_positions)

		board.all_black_moves = board.all_black_moves | self.moves

	def promote_to_queen(self, x, y):

		# Leave the square
		self.leave_square(True)

		# Find the highest index for the pieces dict
		highest_key = 0
		for key in pieces:

			if int(math.log(key, 2)) > 30 and int(math.log(key, 2)) > highest_key:
				highest_key = int(math.log(key, 2))

		# Add a new black queen to the pieces array
		pieces[1<<(highest_key + 1)] = BlackQueen(x, y, False, 1<<(highest_key + 1), 1)

		# Add the queen to the active black pieces
		board.active_black_pieces += 1<<(highest_key + 1)

		# Add the queen to the set of black pinners
		board.black_pinners.add(1<<(highest_key + 1))