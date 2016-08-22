from white_piece_class import *
from globals_file import *
import math

class WhiteKing(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	# The king has a special move, castling, so he overloads piece.move_function to check for it, but then just calls it.
	def move_piece(self, eightx_y):
		#logger.log('king.move_piece')
		# the king may only castle if he has not moved.
		# we only need to update these once, so add a condition. that will hopefully save a little bit of processing time
		if board.castles & 0b1100 > 0:
				board.castles = board.castles & 0b0011

		# Make sure that the proper rook moves to the proper place
		if self.eightx_y - eightx_y == 16:
			pieces[1<<16].move_piece(24) # Queen's side
		elif self.eightx_y - eightx_y == -16:
			pieces[1<<17].move_piece(40) # King's side

		# move the king
		WhitePiece.move_piece(self, eightx_y)

	def calculate_moves(self):
		potential_moves = board.king_move_bitboards[self.eightx_y]

		# Make sure not to move onto a square the opposing king can move onto
		potential_moves = potential_moves & ~board.king_move_bitboards[pieces[1<<31].eightx_y]

		# Make sure not to move onto a square that an opposing pawn can attack
		potential_moves = potential_moves & ~board.unrealized_black_pawn_attacks

		# Make sure not to move onto a square that a pinned piece can attack
		potential_moves = potential_moves & ~board.black_removed_pin_moves

		# Make sure not to move onto a square that an enemy piece may move onto
		potential_moves = potential_moves & ~board.all_black_moves

		# Make sure not to move onto a square that an enemy piece is defending
		potential_moves = potential_moves & ~board.all_defended_black_pieces

		# Defend friendly pieces, and remove friendly pieces from potential moves
		board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)

		self.moves = potential_moves & ~board.all_white_positions

		# Column A castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if board.castles & 0b0100 > 0 and board.all_piece_positions & 0x1010100 == 0:
			# If the king is not in check and would not have to move through check
			if (board.all_black_moves | board.unrealized_black_pawn_attacks | board.black_removed_pin_moves) & 0x101010000 == 0:
				self.moves += 0x10000

		# Column H castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if board.castles & 0b1000 > 0 and board.all_piece_positions & 0x1010000000000 == 0:
			# If the king is not in check and would not have to move through check
			if (board.all_black_moves | board.unrealized_black_pawn_attacks | board.black_removed_pin_moves) & 0x1010000000000 == 0:
				self.moves += 1<<48

		board.all_white_moves = board.all_white_moves | self.moves

	# This function finds any pins on a king
	# It will return a list of dictionaries in the following form:
	# dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}),
	# where the dictionary values are piece indexes
	# The function simply checks each piece that may pin the king. This is perhaps not the most elegant method,
	# but it should be rather efficient, given the precalculated bitboards.
	def find_pins(self):
		pinned_pieces = []

		for pinner_piece in board.black_pinners:
			if pinner_piece & board.active_black_pieces > 0:
				pinned_pieces.append(self.find_pin_by_piece(pinner_piece, board.all_white_positions, board.all_black_positions))

		# Remove potential empty elements from the list
		for i in range(5):
			if None in pinned_pieces:
				pinned_pieces.remove(None)

		return pinned_pieces

	# A dictionary of bitboards has been precalculated (intervening_squares_bitboards), that uses bitboards representing pairs of squares 
	# that lie on a ray as its keys. The value of these keys is a bitboard that represents the intervening squares.
	# This function creates a bitboard from the positions of the king and the pinning piece, then checks the dictionary to see if that 
	# bitboard is a key.
	def find_pin_by_piece(self, pinning_piece, friendly_pieces, enemy_pieces):
		# Get a bitboared representation of the potential pinning piece's position
		pinning_piece_position = (pieces[pinning_piece].eightx_y)

		# Check to see if the the king and the pinning piece are on an array
		if (1 << self.eightx_y) + (1 << pinning_piece_position) in board.intervening_squares_bitboards:

			# Make sure that the correct piece type is being used with the correct ray type (queen & bishops => diagonals, queens & rooks => ranks & files)
			# This is a rook on a diagonal
			if pieces[pinning_piece].type == 2 and (self.eightx_y - pinning_piece_position) // 8 != 0 and (self.eightx_y - pinning_piece_position) % 8 != 0:
				return None

			# This is a bishop on a rank or file (It is sufficient to rule out ranks and files for the bishop, because we already know that the bishop is on a ray [see above])
			if pieces[pinning_piece].type == 3 and ((self.eightx_y - pinning_piece_position) // 8 == 0 or (self.eightx_y - pinning_piece_position) % 8 == 0):
				return None

			# If so, get the squares between them
			intervening_squares = board.intervening_squares_bitboards[(1 << self.eightx_y) + (1 << pinning_piece_position)]

			# If there are any enemy pieces between the (friendly) king and the potential pinning piece,
			# then there is no pin.
			if enemy_pieces & intervening_squares == 0:

				# Otherwise, there can only be friendly pieces between.
				# If there is more than one friendly piece in the intervening squares, there is no pin.
				potential_pinned = friendly_pieces & intervening_squares
				if potential_pinned != 0 and math.log(potential_pinned, 2) % 1 == 0:

					pinned_piece = squares[int(math.log(potential_pinned, 2))].occupied_by
					return dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece})
