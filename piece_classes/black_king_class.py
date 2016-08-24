from black_piece_class import *
from globals_file import *
from constant_bitboards import *
import math

class BlackKing(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	# The king has a special move, castling, so he overloads piece.move_function to check for it, but then just calls it.
	def move_piece(self, eightx_y):
		#logger.log('king.move_piece')
		# the king may only castle if he has not moved.
		# we only need to update these once, so add a condition. that will hopefully save a little bit of processing time
		if board.castles & 0b0011 > 0:
			board.castles = board.castles & 0b1100

		# Make sure that the proper rook moves to the proper place
		if self.eightx_y - eightx_y == 16:
			pieces[1<<18].move_piece(31) # queen's side
		elif self.eightx_y - eightx_y == -16:
			pieces[1<<19].move_piece(47) # king's side

		# move the king
		BlackPiece.move_piece(self, eightx_y)

	def calculate_moves(self):
		potential_moves = king_move_bitboards[self.eightx_y]

		# Make sure not to move onto a square the opposing king can move onto
		potential_moves = potential_moves & ~king_move_bitboards[pieces[1<<30].eightx_y]

		# Make sure not to move onto a square that an opposing pawn can attack
		potential_moves = potential_moves & ~board.unrealized_white_pawn_attacks

		# Make sure not to move onto a square that a pinned piece can attack
		potential_moves = potential_moves & ~board.white_removed_pin_moves

		# Make sure not to move onto a square that an enemy piece may move onto
		potential_moves = potential_moves & ~board.all_white_moves

		# Make sure not to move onto a square that an enemy piece is defending
		potential_moves = potential_moves & ~board.all_defended_white_pieces

		# Defend friendly pieces, and remove friendly pieces from potential moves
		board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)
		
		self.moves = potential_moves & ~board.all_black_positions

		# Column A castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if board.castles & 0b0001 > 0 and board.all_piece_positions & 0x80808000 == 0:
			# If the king is not in check and would not have to move through check
			if (board.all_white_moves | board.unrealized_white_pawn_attacks | board.white_removed_pin_moves) & 0x8080800000 == 0:
				self.moves += 0x800000

		# Column H castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if board.castles & 0b0010 > 0 and board.all_piece_positions & 0x80800000000000 == 0:
			# If the king is not in check and would not have to move through check
			if (board.all_white_moves | board.unrealized_white_pawn_attacks | board.white_removed_pin_moves) & 0x80800000000000 == 0:
				self.moves += 0x80000000000000

		board.all_black_moves = board.all_black_moves | self.moves

	# This function finds any pins on a king
	# It will return a list of dictionaries in the following form:
	# dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}),
	# where the dictionary values are piece indexes
	# The function simply checks each piece that may pin the king. This is perhaps not the most elegant method,
	# but it should be rather efficient, given the precalculated bitboards.
	def find_pins(self):
		active_white_pinners = board.white_pinners & board.active_white_pieces
		while active_white_pinners > 0:
			pinning_piece = active_white_pinners & -active_white_pinners

			# A dictionary of bitboards has been precalculated (intervening_squares_bitboards), that uses bitboards representing pairs of squares 
			# that lie on a ray as its keys. The value of these keys is a bitboard that represents the intervening squares.
			# This function creates a bitboard from the positions of the king and the pinning piece, then checks the dictionary to see if that 
			# bitboard is a key.
			
			# Get a bitboard representation of the potential pinning piece's position
			pinning_piece_position = (pieces[pinning_piece].eightx_y)

			# Check to see if the the king and the pinning piece are on an array
			if (1 << self.eightx_y) + (1 << pinning_piece_position) in intervening_squares_bitboards:

				# Make sure that the correct piece type is being used with the correct ray type (queen & bishops => diagonals, queens & rooks => ranks & files)
				# This is a rook on a diagonal
				if not (pieces[pinning_piece].type == 2 and (self.eightx_y - pinning_piece_position) // 8 != 0 and (self.eightx_y - pinning_piece_position) % 8 != 0):

					# This is a bishop on a rank or file (It is sufficient to rule out ranks and files for the bishop, because we already know that the bishop is on a ray [see above])
					if not (pieces[pinning_piece].type == 3 and ((self.eightx_y - pinning_piece_position) // 8 == 0 or (self.eightx_y - pinning_piece_position) % 8 == 0)):

						# If so, get the squares between them
						intervening_squares = intervening_squares_bitboards[(1 << self.eightx_y) + (1 << pinning_piece_position)]

						# If there are any enemy pieces between the (friendly) king and the potential pinning piece,
						# then there is no pin.
						if board.all_white_positions & intervening_squares == 0:

							# Otherwise, there can only be friendly pieces between.
							# If there is more than one friendly piece in the intervening squares, there is no pin.
							potential_pinned = board.all_black_positions & intervening_squares
							
							if potential_pinned != 0 and math.log(potential_pinned, 2) % 1 == 0:

								pinned_piece = squares[int(math.log(potential_pinned, 2))].occupied_by
								board.pinned_black_pieces.append(dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}))

			# Move to the next active white pinner
			active_white_pinners = active_white_pinners - pinning_piece