# ************************* INCLUDES ***********************
import sys
import math
import time
from tkinter import *
from logger_class import *
from constant_bitboards import *
from display_classes import *

# **********************************************************
# ************************* CLASSES ************************
# **********************************************************

class WhitePiece():
	def __init__(self, x, y, white, index, piece_type):
		global squares

		self.eightx_y = 8*x+y
		self.white = white
		self.moves = 0
		self.index = index
		self.type = piece_type

		squares[self.eightx_y] = self.index

	def move_piece(self, eightx_y):
		global en_passant_pieces
		global en_passant_victim
		global last_move_piece_type
		global last_move_origin_eightx_y
		global last_move_destination_eightx_y
		global halfmove_clock
		global all_white_positions
		global squares

		# If it's not a pawn, increment the halfmove clock
		if self.type != 5:
			halfmove_clock += 1

		all_white_positions += 1 << eightx_y

		# Leave the current square
		self.leave_square()

		# Kill the opposing piece, if any
		if squares[eightx_y] != 0:
			pieces[squares[eightx_y]].leave_square(True)

		# Reset en passant variables
		en_passant_pieces = []
		en_passant_victim = 0

		# Reset last move variables
		last_move_piece_type = self.type
		last_move_origin_eightx_y = self.eightx_y
		last_move_destination_eightx_y = eightx_y

		#update current piece coordinates
		self.eightx_y = eightx_y

		#update occupied status of target square
		squares[eightx_y] = self.index

	# This method is overwritten by the white rook class, to deal with castling.
	def leave_square(self, captured = False):
		global active_white_pieces
		global halfmove_clock
		global all_white_positions
		global squares

		squares[self.eightx_y] = 0

		all_white_positions -= 1 << self.eightx_y
		if captured:
			active_white_pieces -= self.index
			halfmove_clock = 0

	# This is an interface method that is overwritten by every type of piece
	def calculate_moves(self):
		dummy = 1

	def add_moves_to_all_move_bitboard(self):
		global all_white_moves

		all_white_moves = all_white_moves | self.moves

	def calculate_file_moves(self):
		global all_defended_white_pieces

		occupancy = (all_piece_positions >> (self.eightx_y - (self.eightx_y % 8))) & 255
		potential_moves = file_bitboards[self.eightx_y % 8][occupancy] << (self.eightx_y - (self.eightx_y % 8))

		self.moves += potential_moves & ~all_white_positions
		all_defended_white_pieces = all_defended_white_pieces | (potential_moves & all_white_positions)

	def calculate_rank_moves(self):
		global all_defended_white_pieces

		occupancy = (all_piece_positions >> (self.eightx_y % 8)) & 0x101010101010101
		potential_moves = rank_bitboards[occupancy][self.eightx_y // 8] << (self.eightx_y % 8)

		self.moves += potential_moves & ~all_white_positions
		all_defended_white_pieces = all_defended_white_pieces | (potential_moves & all_white_positions)

	def calculate_a1_h8_diagonal_moves(self):
		global all_defended_white_pieces

		bitshift_amount = a1_h8_bitshift_amounts[self.eightx_y]
		position = a1_h8_positions[self.eightx_y]
		length = a1_h8_lengths[self.eightx_y]

		occupancy = (all_piece_positions >> bitshift_amount) & 0x8040201008040201
		potential_moves = (a1_h8_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~all_white_positions
		all_defended_white_pieces = all_defended_white_pieces | (potential_moves & all_white_positions)

	def calculate_a8_h1_diagonal_moves(self):
		global all_defended_white_pieces

		bitshift_amount = a8_h1_bitshift_amounts[self.eightx_y]
		position = a8_h1_positions[self.eightx_y]
		length = a8_h1_lengths[self.eightx_y]

		if bitshift_amount < 0:
			occupancy = (all_piece_positions << abs(bitshift_amount)) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) >> abs(bitshift_amount)
		else:
			occupancy = (all_piece_positions >> bitshift_amount) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~all_white_positions
		all_defended_white_pieces = all_defended_white_pieces | (potential_moves & all_white_positions)

class BlackPiece():
	def __init__(self, x, y, white, index, piece_type):
		global squares
		self.eightx_y = 8*x+y
		self.white = white
		self.moves = 0
		self.index = index
		self.type = piece_type

		squares[self.eightx_y] = self.index

	def move_piece(self, eightx_y):
		global en_passant_pieces
		global en_passant_victim
		global last_move_piece_type
		global last_move_origin_eightx_y
		global last_move_destination_eightx_y
		global halfmove_clock
		global all_black_positions
		global squares

		# If it's not a pawn, increment the halfmove clock
		if self.type != 5:
			halfmove_clock += 1

		all_black_positions += 1 << eightx_y

		# Leave the current square
		self.leave_square()

		# Kill the opposing piece, if any
		if squares[eightx_y] != 0:
			pieces[squares[eightx_y]].leave_square(True)

		# Reset en passant variables
		en_passant_pieces = []
		en_passant_victim = 0

		# Reset last move variables
		last_move_piece_type = self.type
		last_move_origin_eightx_y = self.eightx_y
		last_move_destination_eightx_y = eightx_y

		#update current piece coordinates
		self.eightx_y = eightx_y

		#update occupied status of target square
		squares[eightx_y] = self.index

	# This method is overwritten by the black rook class, to deal with castling.
	def leave_square(self, captured = False):
		global active_black_pieces
		global halfmove_clock
		global all_black_positions
		global squares
		
		squares[self.eightx_y] = 0

		all_black_positions -= 1 << self.eightx_y
		if captured:
			active_black_pieces -= self.index
			halfmove_clock = 0

	# This is an interface method that is overwritten by every type of piece
	def calculate_moves(self):
		dummy = 1

	def add_moves_to_all_move_bitboard(self):
		global all_black_moves

		all_black_moves = all_black_moves | self.moves

	def calculate_file_moves(self):
		global all_defended_black_pieces

		occupancy = (all_piece_positions >> (self.eightx_y - (self.eightx_y % 8))) & 255
		potential_moves = file_bitboards[self.eightx_y % 8][occupancy] << (self.eightx_y - (self.eightx_y % 8))

		self.moves += potential_moves & ~all_black_positions
		all_defended_black_pieces = all_defended_black_pieces | (potential_moves & all_black_positions)

	def calculate_rank_moves(self):
		global all_defended_black_pieces

		occupancy = (all_piece_positions >> (self.eightx_y % 8)) & 0x101010101010101
		potential_moves = rank_bitboards[occupancy][self.eightx_y // 8] << (self.eightx_y % 8)

		self.moves += potential_moves & ~all_black_positions
		all_defended_black_pieces = all_defended_black_pieces | (potential_moves & all_black_positions)

	def calculate_a1_h8_diagonal_moves(self):
		global all_defended_black_pieces

		bitshift_amount = a1_h8_bitshift_amounts[self.eightx_y]
		position = a1_h8_positions[self.eightx_y]
		length = a1_h8_lengths[self.eightx_y]

		occupancy = (all_piece_positions >> bitshift_amount) & 0x8040201008040201
		potential_moves = (a1_h8_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~all_black_positions
		all_defended_black_pieces = all_defended_black_pieces | (potential_moves & all_black_positions)

	def calculate_a8_h1_diagonal_moves(self):
		global all_defended_black_pieces

		bitshift_amount = a8_h1_bitshift_amounts[self.eightx_y]
		position = a8_h1_positions[self.eightx_y]
		length = a8_h1_lengths[self.eightx_y]

		if bitshift_amount < 0:
			occupancy = (all_piece_positions << abs(bitshift_amount)) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) >> abs(bitshift_amount)
		else:
			occupancy = (all_piece_positions >> bitshift_amount) & 0x102040810204080
			potential_moves = (a8_h1_diagonal_bitboards[occupancy][position] & length) << bitshift_amount

		self.moves += potential_moves & ~all_black_positions
		all_defended_black_pieces = all_defended_black_pieces | (potential_moves & all_black_positions)

class WhiteKing(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	# The king has a special move, castling, so he overloads piece.move_function to check for it, but then just calls it.
	def move_piece(self, eightx_y):
		global castles

		# the king may only castle if he has not moved.
		# we only need to update these once, so add a condition. that will hopefully save a little bit of processing time
		if castles & 0b1100 > 0:
				castles = castles & 0b0011

		# Make sure that the proper rook moves to the proper place
		if self.eightx_y - eightx_y == 16:
			pieces[1<<16].move_piece(24) # Queen's side
		elif self.eightx_y - eightx_y == -16:
			pieces[1<<17].move_piece(40) # King's side

		# move the king
		WhitePiece.move_piece(self, eightx_y)

	def calculate_moves(self):
		global all_white_moves
		global all_defended_white_pieces

		potential_moves = king_move_bitboards[self.eightx_y]

		# Make sure not to move onto a square the opposing king can move onto
		potential_moves = potential_moves & ~king_move_bitboards[pieces[1<<31].eightx_y]

		# Make sure not to move onto a square that an opposing pawn can attack
		potential_moves = potential_moves & ~unrealized_black_pawn_attacks

		# Make sure not to move onto a square that a pinned piece can attack
		potential_moves = potential_moves & ~black_removed_pin_moves

		# Make sure not to move onto a square that an enemy piece may move onto
		potential_moves = potential_moves & ~all_black_moves

		# Make sure not to move onto a square that an enemy piece is defending
		potential_moves = potential_moves & ~all_defended_black_pieces

		# Defend friendly pieces, and remove friendly pieces from potential moves
		all_defended_white_pieces = all_defended_white_pieces | (potential_moves & all_white_positions)

		self.moves = potential_moves & ~all_white_positions

		# Column A castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if castles & 0b0100 > 0 and all_piece_positions & 0x1010100 == 0:
			# If the king is not in check and would not have to move through check
			if (all_black_moves | unrealized_black_pawn_attacks | black_removed_pin_moves) & 0x101010000 == 0:
				self.moves += 0x10000

		# Column H castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if castles & 0b1000 > 0 and all_piece_positions & 0x1010000000000 == 0:
			# If the king is not in check and would not have to move through check
			if (all_black_moves | unrealized_black_pawn_attacks | black_removed_pin_moves) & 0x1010000000000 == 0:
				self.moves += 1<<48

		all_white_moves = all_white_moves | self.moves

	# This function finds any pins on a king
	# It will return a list of dictionaries in the following form:
	# dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}),
	# where the dictionary values are piece indexes
	# The function simply checks each piece that may pin the king. This is perhaps not the most elegant method,
	# but it should be rather efficient, given the precalculated bitboards.
	def find_pins(self):
		global pinned_white_pieces

		active_black_pinners = black_pinners & active_black_pieces
		while active_black_pinners > 0:
			pinning_piece = active_black_pinners & -active_black_pinners
			
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
						if all_black_positions & intervening_squares == 0:

							# Otherwise, there can only be friendly pieces between.
							# If there is more than one friendly piece in the intervening squares, there is no pin.
							potential_pinned = all_white_positions & intervening_squares
							
							if potential_pinned != 0 and potential_pinned in bit_significance_mapping:

								pinned_piece = squares[bit_significance_mapping[potential_pinned]]
								pinned_white_pieces.append(dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}))
			
			# Move to the next active pinner
			active_black_pinners = active_black_pinners - pinning_piece

class BlackKing(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	# The king has a special move, castling, so he overloads piece.move_function to check for it, but then just calls it.
	def move_piece(self, eightx_y):
		global castles 

		# the king may only castle if he has not moved.
		# we only need to update these once, so add a condition. that will hopefully save a little bit of processing time
		if castles & 0b0011 > 0:
			castles = castles & 0b1100

		# Make sure that the proper rook moves to the proper place
		if self.eightx_y - eightx_y == 16:
			pieces[1<<18].move_piece(31) # queen's side
		elif self.eightx_y - eightx_y == -16:
			pieces[1<<19].move_piece(47) # king's side

		# move the king
		BlackPiece.move_piece(self, eightx_y)

	def calculate_moves(self):
		global all_black_moves
		global all_defended_black_pieces

		potential_moves = king_move_bitboards[self.eightx_y]

		# Make sure not to move onto a square the opposing king can move onto
		potential_moves = potential_moves & ~king_move_bitboards[pieces[1<<30].eightx_y]

		# Make sure not to move onto a square that an opposing pawn can attack
		potential_moves = potential_moves & ~unrealized_white_pawn_attacks

		# Make sure not to move onto a square that a pinned piece can attack
		potential_moves = potential_moves & ~white_removed_pin_moves

		# Make sure not to move onto a square that an enemy piece may move onto
		potential_moves = potential_moves & ~all_white_moves

		# Make sure not to move onto a square that an enemy piece is defending
		potential_moves = potential_moves & ~all_defended_white_pieces

		# Defend friendly pieces, and remove friendly pieces from potential moves
		all_defended_black_pieces = all_defended_black_pieces | (potential_moves & all_black_positions)
		
		self.moves = potential_moves & ~all_black_positions

		# Column A castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if castles & 0b0001 > 0 and all_piece_positions & 0x80808000 == 0:
			# If the king is not in check and would not have to move through check
			if (all_white_moves | unrealized_white_pawn_attacks | white_removed_pin_moves) & 0x8080800000 == 0:
				self.moves += 0x800000

		# Column H castle
		# If neither the king nor the rook has moved and relevant squares are empty
		if castles & 0b0010 > 0 and all_piece_positions & 0x80800000000000 == 0:
			# If the king is not in check and would not have to move through check
			if (all_white_moves | unrealized_white_pawn_attacks | white_removed_pin_moves) & 0x80800000000000 == 0:
				self.moves += 0x80000000000000

		all_black_moves = all_black_moves | self.moves

	# This function finds any pins on a king
	# It will return a list of dictionaries in the following form:
	# dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}),
	# where the dictionary values are piece indexes
	# The function simply checks each piece that may pin the king. This is perhaps not the most elegant method,
	# but it should be rather efficient, given the precalculated bitboards.
	def find_pins(self):
		global pinned_black_pieces

		active_white_pinners = white_pinners & active_white_pieces
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
						if all_white_positions & intervening_squares == 0:

							# Otherwise, there can only be friendly pieces between.
							# If there is more than one friendly piece in the intervening squares, there is no pin.
							potential_pinned = all_black_positions & intervening_squares
							
							if potential_pinned != 0 and potential_pinned in bit_significance_mapping:

								pinned_piece = squares[bit_significance_mapping[potential_pinned]]
								pinned_black_pieces.append(dict({"pinned_piece": pinned_piece, "pinning_piece": pinning_piece}))

			# Move to the next active white pinner
			active_white_pinners = active_white_pinners - pinning_piece

class WhiteQueen(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_white_moves

		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()
		
		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()

		all_white_moves = all_white_moves | self.moves

class BlackQueen(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_black_moves

		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()
		
		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()
		
		all_black_moves = all_black_moves | self.moves

class WhiteRook(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_white_moves

		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		all_white_moves = all_white_moves | self.moves

	# Whenever a rook leaves a square (captured or not), shut off the castle.
	def leave_square(self, captured = False):
		global castles

		if self.eightx_y == 56:
			castles = castles & 0b0111
		elif self.eightx_y == 0:
			castles = castles & 0b1011

		WhitePiece.leave_square(self, captured)

class BlackRook(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_black_moves

		self.moves = 0

		self.calculate_rank_moves()
		self.calculate_file_moves()

		all_black_moves = all_black_moves | self.moves

	# Whenever a rook leaves a square (captured or not), shut off the castle.
	def leave_square(self, captured = False):
		global castles

		if self.eightx_y == 63:
			castles = castles & 0b1101
		elif self.eightx_y == 7:
			castles = castles & 0b1110

		BlackPiece.leave_square(self, captured)

class WhiteBishop(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_white_moves

		self.moves = 0

		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()

		all_white_moves = all_white_moves | self.moves

class BlackBishop(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def calculate_moves(self):
		global all_black_moves

		self.moves = 0

		self.calculate_a1_h8_diagonal_moves()
		self.calculate_a8_h1_diagonal_moves()

		all_black_moves = all_black_moves | self.moves

class WhiteKnight(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	# The board stores 64 bitboards for knight moves, 1 for the set of moves a knight can make from each square.
	# I store them in the board, rather than in the piece, because if they were stored in the piece, then there would
	# be a copy of all the bitboards for each knight.
	def calculate_moves(self):
		global all_white_moves
		global all_defended_white_pieces

		self.moves = knight_move_bitboards[self.eightx_y] & ~all_white_positions
		all_defended_white_pieces = all_defended_white_pieces | (knight_move_bitboards[self.eightx_y] & all_white_positions)

		all_white_moves = all_white_moves | self.moves

class BlackKnight(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	# The board stores 64 bitboards for knight moves, 1 for the set of moves a knight can make from each square.
	# I store them in the board, rather than in the piece, because if they were stored in the piece, then there would
	# be a copy of all the bitboards for each knight.
	def calculate_moves(self):
		global all_black_moves
		global all_defended_black_pieces

		self.moves = knight_move_bitboards[self.eightx_y] & ~all_black_positions
		all_defended_black_pieces = all_defended_black_pieces | (knight_move_bitboards[self.eightx_y] & all_black_positions)

		all_black_moves = all_black_moves | self.moves

class WhitePawn(WhitePiece):
	def __init__(self, x, y, white, index, piece_type):
		WhitePiece.__init__(self, x, y, white, index, piece_type)

	def move_piece(self, eightx_y):
		global halfmove_clock

		# ******* EN PASSANT ******* #
		# check to see if this pawn is performing en passant, and if so, remove the en passant victim from the board.
		if self.index in en_passant_pieces and pieces[en_passant_victim].eightx_y // 8 == eightx_y // 8:
			pieces[en_passant_victim].leave_square(True)

		WhitePiece.move_piece(self, eightx_y)

		# Queen promotion
		if eightx_y % 8 == 7:
			self.promote_to_queen(x, y)

		# Reset the halfmove clock
		halfmove_clock = 0

	def calculate_moves(self):
		global all_white_moves
		global all_defended_white_pieces
		global unrealized_white_pawn_attacks

		self.moves = white_pawn_moves[self.eightx_y] & ~all_piece_positions

		# The precalculated "third_rank_shifted_to_fourth" is used to prevent a pawn from hopping over a piece on its first move.
		if self.eightx_y % 8 == 1:
			self.moves = self.moves & ~third_rank_shifted_to_fourth

		# Deal with pawn attacks
		self.moves += (white_pawn_attacks[self.eightx_y] & all_black_positions)
		all_defended_white_pieces = all_defended_white_pieces | (white_pawn_attacks[self.eightx_y] & all_white_positions)
		unrealized_white_pawn_attacks = unrealized_white_pawn_attacks | (white_pawn_attacks[self.eightx_y] & ~all_piece_positions)

		all_white_moves = all_white_moves | self.moves

	def promote_to_queen(self, x, y):
		global white_pinners
		global active_white_pieces

		# Leave the square
		self.leave_square(True)

		# Find the highest index for the pieces dict
		highest_key = 0
		for key in pieces:

			if bit_significance_mapping[key] > 30 and bit_significance_mapping[key] > highest_key:
				highest_key = bit_significance_mapping[key]

		# Add a new white queen to the pieces array
		pieces[1<<(highest_key + 1)] = WhiteQueen(x, y, True, 1<<(highest_key + 1), 1)

		# Add the queen to the active white pieces
		active_white_pieces += 1<<(highest_key + 1)

		# Add the queen to the set of white pinners
		white_pinners.add(1<<(highest_key + 1))

class BlackPawn(BlackPiece):
	def __init__(self, x, y, white, index, piece_type):
		BlackPiece.__init__(self, x, y, white, index, piece_type)

	def move_piece(self, eightx_y):
		global halfmove_clock

		# ******* EN PASSANT ******* #
		# check to see if this pawn is performing en passant, and if so, remove the en passant victim from the board.
		if self.index in en_passant_pieces and pieces[en_passant_victim].eightx_y // 8 == eightx_y // 8:
			pieces[en_passant_victim].leave_square(True)

		BlackPiece.move_piece(self, eightx_y)

		# Queen promotion
		if eightx_y % 8 == 0:
			self.promote_to_queen(x, y)

		# Reset the halfmove clock
		halfmove_clock = 0

	def calculate_moves(self):
		global all_black_moves
		global all_defended_black_pieces
		global unrealized_black_pawn_attacks

		self.moves = black_pawn_moves[self.eightx_y] & ~all_piece_positions

		# The precalculated "sixth_rank_shifted_to_fifth" is used to prevent a pawn from hopping over a piece on its first move.
		if self.eightx_y % 8 == 6:
			self.moves = self.moves & ~sixth_rank_shifted_to_fifth

		# Deal with pawn attacks
		self.moves += (black_pawn_attacks[self.eightx_y] & all_white_positions)
		all_defended_black_pieces = all_defended_black_pieces | (black_pawn_attacks[self.eightx_y] & all_black_positions)
		unrealized_black_pawn_attacks = unrealized_black_pawn_attacks | (black_pawn_attacks[self.eightx_y] & ~all_piece_positions)

		all_black_moves = all_black_moves | self.moves

	def promote_to_queen(self, x, y):
		global black_pinners
		global active_black_pieces

		# Leave the square
		self.leave_square(True)

		# Find the highest index for the pieces dict
		highest_key = 0
		for key in pieces:

			if bit_significance_mapping[key] > 30 and bit_significance_mapping[key] > highest_key:
				highest_key = bit_significance_mapping[key]

		# Add a new black queen to the pieces array
		pieces[1<<(highest_key + 1)] = BlackQueen(x, y, False, 1<<(highest_key + 1), 1)

		# Add the queen to the active black pieces
		active_black_pieces += 1<<(highest_key + 1)

		# Add the queen to the set of black pinners
		black_pinners.add(1<<(highest_key + 1))

class PositionMemento():
	def __init__(self):
		# Store last-move variables
		self.former_white_to_move = white_to_move
		self.former_last_move_piece_type = last_move_piece_type
		self.former_last_move_origin_eightx_y = last_move_origin_eightx_y
		self.former_last_move_destination_eightx_y = last_move_destination_eightx_y
		self.former_halfmove_clock = halfmove_clock

		# Store castle variables
		self.former_castles = castles

		# Store piece positions
		self.former_all_white_positions = all_white_positions
		self.former_all_black_positions = all_black_positions

		self.piece_positions = {}
		for piece in piece_indexes:
			self.piece_positions[piece] = pieces[piece].eightx_y

		# Store active pieces
		self.former_active_white_pieces = active_white_pieces
		self.former_active_black_pieces = active_black_pieces

		# Store position
		self.position = squares[:]

	def restore_current_position(self):
		global active_white_pieces
		global active_black_pieces
		global white_to_move
		global last_move_piece_type
		global last_move_origin_eightx_y
		global last_move_destination_eightx_y
		global castles
		global halfmove_clock
		global all_white_positions
		global all_black_positions
		global pieces
		global squares

		# Restore last-move variables
		white_to_move = self.former_white_to_move
		last_move_piece_type = self.former_last_move_piece_type
		last_move_origin_eightx_y = self.former_last_move_origin_eightx_y
		last_move_destination_eightx_y = self.former_last_move_destination_eightx_y
		halfmove_clock = self.former_halfmove_clock

		# Restore castle variables
		castles = self.former_castles

		# Restore piece positions
		all_white_positions = self.former_all_white_positions
		all_black_positions = self.former_all_black_positions

		for piece in piece_indexes:
			pieces[piece].eightx_y = self.piece_positions[piece]

		# Restore active pieces
		active_white_pieces = self.former_active_white_pieces
		active_black_pieces = self.former_active_black_pieces

		squares = self.position[:]

# **************************************************************************
# ********** GLOBAL VARIABLES (FORMER GLOBALS FILE.PY) *********************
# **************************************************************************

# Create a root window
root = Tk()
root.title("Chess Board")
root.geometry("820x820")

# Create a frame in the window to hold other widgets
app = Frame(root, height = 1000, width = 1000, bg = "#333")
app.grid()

# Create the board display and the square display
board_display = BoardDisplay(app)
square_display = [[SquareDisplay(x, y, board_display) for y in range(8)] for x in range(8)]

# Create the main data structures for the engine
squares = [0 for i in range(64)] # i = 8x+y

# Create the pieces dictionary
piece_indexes = [2**x for x in range(32)]
pieces = {}

for piece_index in piece_indexes:
	pieces[piece_index] = []

# Pin variables
white_pinners = 0b00010011000000110000000000000000 # Queen, rooks, and bishops
black_pinners = 0b00101100000011000000000000000000 # Queen, rooks, and bishops

# Active pieces
active_white_pieces = 0b01010011001100110000000011111111
active_black_pieces = 0b10101100110011001111111100000000

# En passant variables
en_passant_pieces = []
en_passant_victim = 0

# Move variables
white_to_move = True

last_move_piece_type = -1
last_move_origin_eightx_y = -1
last_move_destination_eightx_y = -1

#Castles
# The bits here are as follow:
# 1000 : White castle kingside
# 0100 : White castle queenside
# 0010 : Black castle kingside
# 0001 : Black castle queenside
castles = 0b1111

# Check variables
checker_types = []
checker_positions = []

# pin arrays
pinned_white_pieces = []
pinned_black_pieces = []

# FEN variables - These are to enable load from Forsyth-Edwards notation
halfmove_clock = 0
fullmove_number = 1

# This is a way to get the significance of numbers that are powers of 2. Useful for translating piece indexes
bit_significance_mapping = {}
for i in range(64):
	bit_significance_mapping[1<<i] = i

###### BOARD STATE BITBOARDS ######
all_white_moves = 0
all_black_moves = 0

all_defended_white_pieces = 0
all_defended_black_pieces = 0

all_white_positions = 0
all_black_positions = 0

all_piece_positions = 0

white_removed_pin_moves = 0
black_removed_pin_moves = 0

unrealized_white_pawn_attacks = 0
unrealized_black_pawn_attacks = 0

third_rank_shifted_to_fourth = 0 # For use in calculating white pawns' first moves
sixth_rank_shifted_to_fifth = 0 # For use in calculating black pawns' first moves

piece_values = {0:0,1<<0:1, 1<<1:1, 1<<2:1, 1<<3:1, 1<<4:1, 1<<5:1, 1<<6:1, 1<<7:1, 1<<8:-1, 1<<9:-1, 1<<10:-1, 1<<11:-1, 1<<12:-1, 1<<13:-1, 1<<14:-1, 1<<15:-1, 1<<16:5, 1<<17:5, 1<<18:-5, 1<<19:-5, 1<<20:3, 1<<21:3, 1<<22:-3, 1<<23:-3, 1<<24:3, 1<<25:3, 1<<26:-3, 1<<27:-3, 1<<28: 9, 1<<29:-9, 1<<30:10000, 1<<31:-10000}

nodes = 0

# **************************************************************************
# ************************** USER INTERFACE ********************************
# **************************************************************************

def handle_click (event):
	global nodes

	# find coordinates of click (gives x, y coords)
	x = (event.x - board_display.x_start) // board_display.square_size
	y = 7 - (event.y - board_display.y_start) // board_display.square_size
	eightx_y = 8*x+y

	# If nothing is selected
	if board_display.selected == 0:
		if squares[eightx_y] != 0 and pieces[squares[eightx_y]].white == white_to_move:
			select_piece(x, y, eightx_y)

	# If a piece is selected and the user has made a legal move
	elif pieces[board_display.selected].moves & (1 << eightx_y) > 0:
		move_selected_piece(eightx_y)

		generate_moves()

		# Let the computer play
		if computer_plays == 'white' or computer_plays == 'black':
			computer_start = logger.return_timestamp()
			computer_move(computer_plays)
			computer_end = logger.return_timestamp()

			nps = nodes / ((computer_end - computer_start)/1000.0)
			logger.log("nodes: " + str(nodes))
			logger.log("nps: " + str(nps))
			logger.log("************************************")
			nodes = 0

			generate_moves()

	# If a piece is selected and the user has made a non-move click
	else:
		deselect_piece()

def select_piece(x, y, eightx_y):
	#logger.log('select_piece')

	# Color the selected square and redraw the piece
	if square_display[x][y].color == "#789":
		square_display[x][y].color = "#987"
	elif square_display[x][y].color == "#567":
		square_display[x][y].color = "#765"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, squares[eightx_y], pieces)

	# Store which piece is selected, and which square has been highlighted
	board_display.selected = squares[eightx_y]
	board_display.highlighted_square = [x, y]

def deselect_piece():
	#logger.log('deselect_piece')

	x = board_display.highlighted_square[0]
	y = board_display.highlighted_square[1]

	if square_display[x][y].color == "#987":
		square_display[x][y].color = "#789"
	elif square_display[x][y].color == "#765":
		square_display[x][y].color = "#567"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, squares[8*x+y], pieces)
	board_display.selected = 0
	board_display.highlighted_square = []

def move_selected_piece(eightx_y):
	global white_to_move
	global fullmove_number

	# Move the piece
	pieces[board_display.selected].move_piece(eightx_y)

	# Deselect the piece
	board_display.selected = 0

	# Increment the fullmove counter
	if not white_to_move:
		fullmove_number += 1

	# Change whose turn it is to move
	white_to_move = not white_to_move

	# Recolor the origin square
	board_display.render_position(squares[:], square_display, pieces)

# ****************************************************************************
# ************************** MOVE GENERATION *********************************
# ****************************************************************************

def generate_moves():
	global checker_types
	global checker_positions
	global pinned_white_pieces
	global pinned_black_pieces
	global all_white_moves
	global all_black_moves
	global all_defended_white_pieces
	global all_defended_black_pieces
	global all_piece_positions
	global white_removed_pin_moves
	global black_removed_pin_moves
	global unrealized_white_pawn_attacks
	global unrealized_black_pawn_attacks
	global third_rank_shifted_to_fourth
	global sixth_rank_shifted_to_fifth

	# Reset board variables
	checker_types = []
	checker_positions = []
	pinned_white_pieces = []
	pinned_black_pieces = []

	# Erase the bitboards that are maintained by the *.calculate_moves functions
	all_white_moves = 0
	all_black_moves = 0
	all_defended_white_pieces = 0
	all_defended_black_pieces = 0
	unrealized_white_pawn_attacks = 0
	unrealized_black_pawn_attacks = 0
	white_removed_pin_moves = 0
	black_removed_pin_moves = 0

	# Populate the piece position bitboards
	all_piece_positions = all_white_positions | all_black_positions
	third_rank_shifted_to_fourth = (all_piece_positions & 0x404040404040404) << 1
	sixth_rank_shifted_to_fifth = (all_piece_positions & 0x2020202020202020) >> 1
	
	# Recalculate all necessary information
	calculate_all_moves_but_king_moves()
	manage_white_pins()
	manage_black_pins()

	calculate_king_moves()

	if white_to_move:	
		find_black_checks()
	else:
		find_white_checks()

def calculate_all_moves_but_king_moves():

	# Recalculate the moves for all active pieces except for kings
	white_pieces_for_loop = active_white_pieces - (1<<30)
	while white_pieces_for_loop > 0:
		active_piece = white_pieces_for_loop & -white_pieces_for_loop
		pieces[active_piece].calculate_moves()
		white_pieces_for_loop -= active_piece

	black_pieces_for_loop = active_black_pieces - (1<<31)
	while black_pieces_for_loop > 0:
		active_piece = black_pieces_for_loop & -black_pieces_for_loop
		pieces[active_piece].calculate_moves()
		black_pieces_for_loop -= active_piece

	# Do this here, rather than inside each pawn.
	check_for_en_passant()

# The kings' moves must be calculated after pins are set up (Although, wouldn't it make sense to just calculate the kings' moves before calculating pins?)
def calculate_king_moves():
	#logger.log('calculate_king_moves')

	pieces[1<<30].calculate_moves()
	pieces[1<<31].calculate_moves()

def manage_white_pins():
	global white_removed_pin_moves

	pieces[1<<30].find_pins()

	# A pinned piece may only move on the ray between the king and the pinning piece.
	# Thus, pawns may advance toward a pinning piece, or a bishop may take a queen that pins on the diagonal.
	for pin in pinned_white_pieces:
		pinned_piece = pin['pinned_piece']
		pinning_piece = pin['pinning_piece']

		pinning_piece_position = 1 << (pieces[pinning_piece].eightx_y)
		pinned_piece_position = 1 << (pieces[pinned_piece].eightx_y)

		king_position = 1 << (pieces[1<<30].eightx_y)

		# A pinned piece can only move on the ray between the king and the pinning piece.
		potential_moves = intervening_squares_bitboards[king_position + pinning_piece_position] - pinned_piece_position + pinning_piece_position

		# Even if a white bishop is pinned, a black king still cannot move onto a square it could have moved onto.
		# So, store all the removed moves in the board, and reference that board in the king's move function.
		white_removed_pin_moves = white_removed_pin_moves | (pieces[pinned_piece].moves - (pieces[pinned_piece].moves & potential_moves))
		# Update the pinned piece
		pieces[pinned_piece].moves = pieces[pinned_piece].moves & potential_moves

def manage_black_pins():
	global black_removed_pin_moves

	pieces[1<<31].find_pins()

	# A pinned piece may only move on the ray between the king and the pinning piece.
	# Thus, pawns may advance toward a pinning piece, or a bishop may take a queen that pins on the diagonal.
	for pin in pinned_black_pieces:
		pinned_piece = pin['pinned_piece']
		pinning_piece = pin['pinning_piece']

		pinning_piece_position = 1 << (pieces[pinning_piece].eightx_y)
		pinned_piece_position = 1 << (pieces[pinned_piece].eightx_y)

		king_position = 1 << (pieces[1<<31].eightx_y)

		# A pinned piece can only move on the ray between the king and the pinning piece.
		potential_moves = intervening_squares_bitboards[king_position + pinning_piece_position] - pinned_piece_position + pinning_piece_position

		# Even if a white bishop is pinned, a black king still cannot move onto a square it could have moved onto.
		# So, store all the removed moves in the board, and reference that board in the king's move function.
		black_removed_pin_moves = black_removed_pin_moves | (pieces[pinned_piece].moves - (pieces[pinned_piece].moves & potential_moves))

		# Update the pinned piece
		pieces[pinned_piece].moves = pieces[pinned_piece].moves & potential_moves

def find_white_checks():
	global checker_types
	global checker_positions
	global all_white_moves

	king_position = 1 << (pieces[1<<30].eightx_y)

	if all_black_moves & king_position > 0:
		# If the king is in check, discover the type and location of the checking pieces
		black_pieces_for_loop = active_black_pieces
		while black_pieces_for_loop > 0:
			active_piece = black_pieces_for_loop & -black_pieces_for_loop
			if pieces[active_piece].moves & king_position > 1:
				checker_positions.append(pieces[active_piece].eightx_y)
				checker_types.append(pieces[active_piece].type)

			black_pieces_for_loop -= active_piece

		# Calculate the moves that friendly pieces can perform to save the king
		calculate_check_moves(1<<30)

		all_white_moves = 0

		white_pieces_for_loop = active_white_pieces
		while white_pieces_for_loop > 0:
			active_piece = white_pieces_for_loop & -white_pieces_for_loop
			pieces[active_piece].add_moves_to_all_move_bitboard()
			white_pieces_for_loop -= active_piece

def find_black_checks():
	global checker_types
	global checker_positions
	global all_black_moves

	king_position = 1 << (pieces[1<<31].eightx_y)

	if all_white_moves & king_position > 0:
		# If the king is in check, discover the type and location of the checking pieces
		white_pieces_for_loop = active_white_pieces
		while white_pieces_for_loop > 0:
			active_piece = white_pieces_for_loop & -white_pieces_for_loop
			if pieces[active_piece].moves & king_position > 1:
				checker_positions.append(pieces[active_piece].eightx_y)
				checker_types.append(pieces[active_piece].type)

			white_pieces_for_loop -= active_piece

		# Calculate the moves that friendly pieces can perform to save the king
		calculate_check_moves(1<<31)

		all_black_moves = 0

		black_pieces_for_loop = active_black_pieces
		while black_pieces_for_loop > 0:
			active_piece = black_pieces_for_loop & -black_pieces_for_loop
			pieces[active_piece].add_moves_to_all_move_bitboard()
			black_pieces_for_loop -= active_piece

# Create a bitboard of moves that can be used to defend the king.
# Then, pass the list to the defend_move() function, which will bitwise AND that bitboard with the piece's own bitboard.
def calculate_check_moves(king):

	defence_moves = 0
	number_of_checkers = len(checker_positions)

	# If there is one piece checking the king, then friendly pieces may save the king
	# If there is more than one piece checking the king, then only the king may save himself.
	if number_of_checkers == 1:
		# If there's only one chcker, capturing it is always an option
		defence_moves += 1 << checker_positions[0]

		# If the single checking piece is not a pawn or a knight, then the checked side can defend also defend my interposing a piece
		if checker_types[0] in [1, 2, 3]:
			if ((1 << pieces[king].eightx_y) + (1 << checker_positions[0])) in intervening_squares_bitboards:
				defence_moves += intervening_squares_bitboards[(1 << pieces[king].eightx_y) + (1 << checker_positions[0])]

	# Use the defense moves array to decide how to defend the king
	if pieces[king].white:
		defenders = active_white_pieces - (1<<30)
	else:
		defenders = active_black_pieces - (1<<31)

	while defenders > 0:
		defender = defenders & -defenders
		pieces[defender].moves = pieces[defender].moves & defence_moves
		defenders -= defender

	# If the king is being checked by a ray piece, there is an additional condition added to his moves:
	# He may not move away from a checking ray piece on the ray that he is being checked with.
	moves_to_remove = 0
	king_eightx_y = pieces[king].eightx_y

	# Loop, for there may be more than 1 checker.
	for i in range(number_of_checkers):
		# The checker_types array doesn't tie the position to the checker type.
		checker_eightx_y = checker_positions[i]
		checker_index = squares[checker_positions[i]]
		checker_type = pieces[checker_index].type

		if checker_type in [1, 2, 3]:
			vector = get_vector(checker_positions[i], pieces[king].eightx_y)

			if pieces[king].eightx_y + vector >= 0 and pieces[king].eightx_y + vector <= 64:
				potential_move_to_remove = 1 << (pieces[king].eightx_y + vector)
			else:
				potential_move_too_remove = 0

			if king_move_bitboards[king_eightx_y] & potential_move_to_remove > 0:
				moves_to_remove += potential_move_to_remove

	pieces[king].moves = pieces[king].moves - (pieces[king].moves & moves_to_remove)

def get_vector(origin, destination):
	if origin // 8 == destination // 8:	# Same file
		if origin > destination:
			return -1
		else: 
			return 1
	elif origin % 8 == destination % 8: # Same rank
		if origin > destination:
			return -8
		else:
			return 8
	elif (origin - destination) % 9 == 0: # A1H8 diagonals
		if origin > destination:
			return -9
		else:
			return 9
	elif (origin - destination) % 7 == 0: #A8H1 diagonals
		if origin > destination:
			return -7
		else:
			return 7

def check_for_en_passant():
	global en_passant_pieces
	global en_passant_victim

	if last_move_piece_type == 5:
		if last_move_origin_eightx_y - last_move_destination_eightx_y == 2:
			if last_move_origin_eightx_y > 7 and squares[last_move_destination_eightx_y - 8] & 0b11111111 > 0:
				en_passant_attacker = squares[last_move_destination_eightx_y - 8]
				pieces[en_passant_attacker].moves += 1 << (last_move_destination_eightx_y + 1)
				en_passant_pieces.append(en_passant_attacker)
				en_passant_victim = squares[last_move_destination_eightx_y]

			if last_move_origin_eightx_y < 56 and squares[last_move_destination_eightx_y + 8] & 0b11111111 > 0:
				en_passant_attacker = squares[last_move_destination_eightx_y + 8]
				pieces[en_passant_attacker].moves += 1 << (last_move_destination_eightx_y + 1)
				en_passant_pieces.append(en_passant_attacker)
				en_passant_victim = squares[last_move_destination_eightx_y]

		elif last_move_origin_eightx_y - last_move_destination_eightx_y == -2:
			if last_move_origin_eightx_y > 7 and squares[last_move_destination_eightx_y - 8] & 0b1111111100000000 > 0:
				en_passant_attacker = squares[last_move_destination_eightx_y - 8]
				pieces[en_passant_attacker].moves += 1 << (last_move_destination_eightx_y - 1)
				en_passant_pieces.append(en_passant_attacker)
				en_passant_victim = squares[last_move_destination_eightx_y]

			if last_move_origin_eightx_y < 56 and squares[last_move_destination_eightx_y + 8] & 0b1111111100000000 > 0:
				en_passant_attacker = squares[last_move_destination_eightx_y + 8]
				pieces[en_passant_attacker].moves += 1 << (last_move_destination_eightx_y - 1)
				en_passant_pieces.append(en_passant_attacker)
				en_passant_victim = squares[last_move_destination_eightx_y]

# ****************************************************************************
# ***************************** EVALUATION ***********************************
# ****************************************************************************
def evaluate_position():
	global nodes

	position_value = 0

	for i in range(64):
		position_value += piece_values[squares[i]]

	nodes += 1

	return position_value

# ****************************************************************************
# ******************************* SEARCH *************************************
# ****************************************************************************
def computer_move(computer_plays):
	#logger.log('computer_move')

	if computer_plays == 'white':
		calculation_result = calculate_white_move(3, 3)

		# Calculate_white_move will return either -1 or a dictionary containing instructions for moving. =1 means checkmate.
		if calculation_result == -1: # Checkmate
			print("Checkmate has occurred. Black wins.")

	elif computer_plays == 'black':
		calculation_result = calculate_black_move(3, 3)

		# Calculate_black_move will return either -1 or a dictionary containing instructions for moving. -1 means checkmate.
		if calculation_result == -1: # Checkmate
			print("Checkmate has occurred. White wins.")

	# Unpack the return dictionary	
	best_move_piece = calculation_result.get("best_move_piece")
	best_move = calculation_result.get("best_move")

	# Move the piece, with graphics.
	board_display.selected = best_move_piece
	move_selected_piece(best_move)

def calculate_white_move(depth, current_depth):
	# store the current position, as well as the last move variables (for en passant detection)
	position_memento = PositionMemento()
	generate_moves()

	# Loop through all pieces' moves
	current_active_white_pieces = active_white_pieces

	# Initialize the best_move_piece as an impossible value, to allow detection of checkmate
	best_move_piece = -1
	best_position_value = -20000

	while current_active_white_pieces > 0:
		piece = current_active_white_pieces & -current_active_white_pieces

		piece_moves = pieces[piece].moves

		while piece_moves > 0:

			# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
			move = piece_moves & -piece_moves
			eightx_y = bit_significance_mapping[move]

			# Make move and return value of board (without graphics)
			pieces[piece].move_piece(eightx_y)

			# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
			# Otherwise, call the move function of the opposing side. 
			if current_depth == 0:
				# Calculate the position of the board
				position_value = evaluate_position()
			else:
				position_value = calculate_black_move(depth, current_depth - 1)

			# compare value of move with previous high move value
			if position_value > best_position_value:
				best_position_value = position_value
				best_move_piece = piece
				best_move_eightx_y = eightx_y
		
			# restore game state using Memento
			position_memento.restore_current_position()
			generate_moves()

			# Update the piece_moves bitboard
			piece_moves -= move

		current_active_white_pieces -= piece

	# For any node but the root of the tree, the function should return the calculate value of the position.
	# For the root node of the tree, the function should return a piece index, and the x, y values of the best move.
	# If checkmate has occurred in a branch, return an arbitrarily large number as the value of the position.
	# If checkmate has occurred in the root node, return -1 as the piece index.
	if depth != current_depth: # Not root node
		if best_move_piece == -1: # Checkmate has occurred.
			return -20000
		else:
			return best_position_value
	else: # root node
		if best_move_piece == -1: # Checkmate has occurred.
			return -1
		else: 
			return {"best_move_piece": best_move_piece, "best_move": best_move_eightx_y}

def calculate_black_move(depth, current_depth):
	# store the current position, as well as the last move variables (for en passant detection)
	position_memento = PositionMemento()
	generate_moves()

	# Loop through all pieces' moves
	# (I'll need to generalize this for white or black)
	current_active_black_pieces = active_black_pieces

	# Initialize the best_move_piece as an impossible value, to allow detection of checkmate
	best_move_piece = -1
	best_position_value = 20000

	while current_active_black_pieces > 0:
		piece = current_active_black_pieces & -current_active_black_pieces

		piece_moves = pieces[piece].moves

		while piece_moves > 0:

			# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
			move = piece_moves & -piece_moves
			eightx_y = bit_significance_mapping[move]

			# Make move and return value of board (without graphics)
			pieces[piece].move_piece(eightx_y)

			# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
			# Otherwise, call the move function of the opposing side. 
			if current_depth == 0:
				# Calculate the position of the board
				position_value = evaluate_position()
			else:
				position_value = calculate_white_move(depth, current_depth - 1)

			# compare value of move with previous high move value
			if position_value < best_position_value:
				best_position_value = position_value
				best_move_piece = piece
				best_move_eightx_y = eightx_y

			# restore game state using Memento
			position_memento.restore_current_position()
			generate_moves()

			# Update the piece_moves bitboard
			piece_moves -= move

		current_active_black_pieces -= piece

	# For any node but the root of the tree, the function should return the calculate value of the position.
	# For the root node of the tree, the function should return a piece index, and the x, y values of the best move.
	# If checkmate has occurred in a branch, return an arbitrarily large number as the value of the position.
	# If checkmate has occurred in the root node, return -1 as the piece index.

	if depth != current_depth: # Not root node
		if best_move_piece == -1: # Checkmate has occurred.
			return 20000
		else:
			return best_position_value
	else: # root node
		if best_move_piece == -1: # Checkmate has occurred.
			return -1
		else: 
			return {"best_move_piece": best_move_piece, "best_move": best_move_eightx_y}

# ****************************************************************************
# ************************ INITIALIZTION FUNCTIONS ***************************
# ****************************************************************************

# Bind an event handler to the left click event
def initialize_board_display():
	board_display.bind("<Button-1>", handle_click)
	board_display.pack()

# Sets up the board in the initial position, and displays it.
def initialize_with_start_position():
	global all_white_positions
	global all_black_positions

	# Set up the pieces

	# Piece(rank, file, white, index, piece_type)
	pieces[1] = WhitePawn(0, 1, True, 1, 5)
	pieces[1<<1] = WhitePawn(1, 1, True, 1<<1, 5)
	pieces[1<<2] = WhitePawn(2, 1, True, 1<<2, 5)
	pieces[1<<3] = WhitePawn(3, 1, True, 1<<3, 5)
	pieces[1<<4] = WhitePawn(4, 1, True, 1<<4, 5)
	pieces[1<<5] = WhitePawn(5, 1, True, 1<<5, 5)
	pieces[1<<6] = WhitePawn(6, 1, True, 1<<6, 5)
	pieces[1<<7] = WhitePawn(7, 1, True, 1<<7, 5)
	pieces[1<<8] = BlackPawn(0, 6, False, 1<<8, 5)
	pieces[1<<9] = BlackPawn(1, 6, False, 1<<9, 5)
	pieces[1<<10] = BlackPawn(2, 6, False, 1<<10, 5)
	pieces[1<<11] = BlackPawn(3, 6, False, 1<<11, 5)
	pieces[1<<12] = BlackPawn(4, 6, False, 1<<12, 5)
	pieces[1<<13] = BlackPawn(5, 6, False, 1<<13, 5)
	pieces[1<<14] = BlackPawn(6, 6, False, 1<<14, 5)
	pieces[1<<15] = BlackPawn(7, 6, False, 1<<15, 5)
	pieces[1<<16] = WhiteRook(0, 0, True, 1<<16, 2)
	pieces[1<<17] = WhiteRook(7, 0, True, 1<<17, 2)
	pieces[1<<18] = BlackRook(0, 7, False, 1<<18, 2)
	pieces[1<<19] = BlackRook(7, 7, False, 1<<19, 2)
	pieces[1<<20] = WhiteKnight(1, 0, True, 1<<20, 4)
	pieces[1<<21] = WhiteKnight(6, 0, True, 1<<21, 4)
	pieces[1<<22] = BlackKnight(1, 7, False, 1<<22, 4)
	pieces[1<<23] = BlackKnight(6, 7, False, 1<<23, 4)
	pieces[1<<24] = WhiteBishop(2, 0, True, 1<<24, 3)
	pieces[1<<25] = WhiteBishop(5, 0, True, 1<<25, 3)
	pieces[1<<26] = BlackBishop(2, 7, False, 1<<26, 3)
	pieces[1<<27] = BlackBishop(5, 7, False, 1<<27, 3)
	pieces[1<<28] = WhiteQueen(3, 0, True, 1<<28, 1)
	pieces[1<<29] = BlackQueen(3, 7, False, 1<<29, 1)
	pieces[1<<30] = WhiteKing(4, 0, True, 1<<30, 0)
	pieces[1<<31] = BlackKing(4, 7, False, 1<<31, 0)

	# Manually set up a couple bitboards
	all_white_positions = 0x303030303030303
	all_black_positions = 0xc0c0c0c0c0c0c0c0

	# Generate the moves
	generate_moves()

	# Display the board

	board_display.render_position(squares[:], square_display, pieces)

def initialize_with_fen_position(fen_string):
	global white_to_move
	global last_move_piece_type
	global last_move_origin_eightx_y
	global last_move_destination_eightx_y
	global castles
	global halfmove_clock
	global fullmove_number
	global all_white_positions
	global all_black_positions
	global all_piece_positions

	# Split it into separate parts
	fen_array = fen_string.split(' ')

	# 1) PIECE PLACEMENT DATA
	# Split the position string into an array, and reverse it so that we deal with rank A first
	position_array = list(reversed(fen_array[0].split('/')))

	# Specify which indexes a piece can have in the pieces array
	white_pawn_indexes = [1, 1<<1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7]
	black_pawn_indexes = [1<<8, 1<<9, 1<<10, 1<<11, 1<<12, 1<<13, 1<<14, 1<<15]
	white_rook_indexes = [1<<16, 1<<17]
	black_rook_indexes = [1<<18, 1<<19]
	white_knight_indexes = [1<<20, 1<<21]
	black_knight_indexes = [1<<22, 1<<23]
	white_bishop_indexes = [1<<24, 1<<25]
	black_bishop_indexes = [1<<26, 1<<27]
	white_queen_index = 1<<28
	black_queen_index = 1<<29
	white_king_index = 1<<30
	black_king_index = 1<<31

	# Loop through the array, parse each string, and initialize each piece
	rank_counter = 0
	for rank in position_array:
	
		file_counter = 0
		for file in rank:
			if file.isdigit():
				file_counter += int(file)
			else: 
				# Piece(rank, file, white, index, piece_type)
				if file == 'P':
					white_pawn_index = white_pawn_indexes[0]
					pieces[white_pawn_index] = WhitePawn(file_counter, rank_counter, True, white_pawn_index, 5)
					white_pawn_indexes.remove(white_pawn_index)
				elif file == 'p': # Black pawn
					black_pawn_index = black_pawn_indexes[0]
					pieces[black_pawn_index] = BlackPawn(file_counter, rank_counter, False, black_pawn_index, 5)
					black_pawn_indexes.remove(black_pawn_index)
				elif file == 'R': # White rook
					white_rook_index = white_rook_indexes[0]
					pieces[white_rook_index] = WhiteRook(file_counter, rank_counter, True, white_rook_index, 2)
					white_rook_indexes.remove(white_rook_index)
				elif file == 'r': # Black rook
					black_rook_index = black_rook_indexes[0]
					pieces[black_rook_index] = BlackRook(file_counter, rank_counter, False, black_rook_index, 2)
					black_rook_indexes.remove(black_rook_index)
				elif file == 'N': # White knight
					white_knight_index = white_knight_indexes[0]
					pieces[white_knight_index] = WhiteKnight(file_counter, rank_counter, True, white_knight_index, 4)
					white_knight_indexes.remove(white_knight_index)
				elif file == 'n': # Black knight
					black_knight_index = black_knight_indexes[0]
					pieces[black_knight_index] = BlackKnight(file_counter, rank_counter, False, black_knight_index, 4)
					black_knight_indexes.remove(black_knight_index)
				elif file == 'B': # White bishop
					white_bishop_index = white_bishop_indexes[0]
					pieces[white_bishop_index] = WhiteBishop(file_counter, rank_counter, True, white_bishop_index, 3)
					white_bishop_indexes.remove(white_bishop_index)
				elif file == 'b': # Black bishop
					black_bishop_index = black_bishop_indexes[0]
					pieces[black_bishop_index] = BlackBishop(file_counter, rank_counter, False, black_bishop_index, 3)
					black_bishop_indexes.remove(black_bishop_index)
				elif file == 'Q': # White queen
					pieces[white_queen_index] = WhiteQueen(file_counter, rank_counter, True, white_queen_index, 1)
				elif file == 'q': # Black queen
					pieces[black_queen_index] = BlackQueen(file_counter, rank_counter, False, black_queen_index, 1)
				elif file == 'K': # White king
					pieces[white_king_index] = WhiteKing(file_counter, rank_counter, True, white_king_index, 0)
				elif file == 'k': # Black king
					pieces[black_king_index] = BlackKing(file_counter, rank_counter, False, black_king_index, 0)

				file_counter += 1

		if file_counter != 8:
			print('Invalid piece placement data. rank ' + str(rank_counter + 1) + ' does not have the correct amount of squares in it.')
			exit()

		rank_counter += 1

	# 2) ACTIVE COLOR
	if fen_array[1] == 'w':
		white_to_move = True
	elif fen_array[1] == 'b':
		white_to_move = False
	else:
		print('The second field of the FEN string is invalid. It must be a "w" or a "b".')
		exit()
	
	# 3) CASTLING AVAILABILITY
	for character in fen_array[2]:
		if character not in ['-', 'K', 'Q', 'k', 'q']:
			print('The castling availability field is invalid. It must contain either a combination of the characters "K", "Q", "k", and "q", or the character "-".')
			exit()

	if 'K' in fen_array[2]:
		castles = castles | 0b1000
	else:
		castles = castles & 0b0111

	if 'Q' in fen_array[2]:
		castles = castles | 0b0100
	else:
		castles = castles & 0b1011

	if 'k' in fen_array[2]:
		castles = castles | 0b0010
	else:
		castles = castles & 0b1101

	if 'q' in fen_array[2]:
		castles = castles | 0b0001
	else:
		castles = castles & 0b1110

	# 4) EN PASSANT TARGET SQUARE
	# Ludullus stores 5 last-move variables in the board class, and infers from those whether or not en passant is possible. 
	# If it is possible, three en passant variables are stored in the board class, and the moves of the piece(s) that may perform the en passant are updated.
	# So, this function will only populate the initial five last-move variables, and allow downstream logic to do the rest.

	if fen_array[3] not in ['a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3', 'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6', '-']:
		print('The en passant target square field is invalid. It must be either a square on the 3rd or the 6th rank, or a hyphen.')
		exit()

	if fen_array[3] != '-':
		# Find the rank
		if '3' in fen_array[3]:
			target_square_rank = 2 # Subtracting 1, because the coordinates start at 0.
		elif '6' in fen_array[3]:
			target_square_rank = 5 # etc.

		# Find the file
		if 'a' in fen_array[3]:
			target_square_file = 0
		elif 'b' in fen_array[3]:
			target_square_file = 1
		elif 'c' in fen_array[3]:
			target_square_file = 2
		elif 'd' in fen_array[3]:
			target_square_file = 3
		elif 'e' in fen_array[3]:
			target_square_file = 4
		elif 'f' in fen_array[3]:
			target_square_file = 5
		elif 'g' in fen_array[3]:
			target_square_file = 6
		elif 'h' in fen_array[3]:
			target_square_file = 7

		last_move_piece_type = 5

		if target_square_rank == 2: # white
			last_move_origin_eightx_y = 8*target_square_file+1
			last_move_destination_eightx_y = 8*target_square_file+3
		else: # black
			last_move_origin_eightx_y = 8*target_square_file+6
			last_move_destination_eightx_y = 8*target_square_file+4

	# 5) HALFMOVE CLOCK
	if fen_array[4].isdigit():
		halfmove_clock = int(fen_array[4])
	else:
		print('The halfmove clock field must be an integer.')

	# 6) FULLMOVE NUMBER
	if fen_array[5].isdigit():
		fullmove_number = int(fen_array[5])
	else:
		print('The fullmove number field must be an integer.')

	# Manually set up a couple bitboards
	for piece in pieces:
		if pieces[piece].white:
			all_white_positions += 1 << pieces[piece].eightx_y
		else:
			all_black_positions += 1 << pieces[piece].eightx_y

	# Generate the moves
	generate_moves()

	# Display the board
	board_display.render_position(squares[:], square_display, pieces)

def calculate_white_perft(depth, current_depth):
	global nodes
	# store the current position, as well as the last move variables (for en passant detection)

	if current_depth == 0:
		nodes += 1	
	else:
		position_memento = PositionMemento()
		generate_moves()

		# Loop through all pieces' moves
		current_active_white_pieces = active_white_pieces

		while current_active_white_pieces > 0:
			piece = current_active_white_pieces & -current_active_white_pieces

			piece_moves = pieces[piece].moves

			while piece_moves > 0:

				# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
				move = piece_moves & -piece_moves
				eightx_y = bit_significance_mapping[move]

				# Make move and return value of board (without graphics)
				pieces[piece].move_piece(eightx_y)

				# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
				# Otherwise, call the move function of the opposing side. 
				position_value = calculate_black_perft(depth, current_depth - 1)
			
				# restore game state using Memento
				position_memento.restore_current_position()
				generate_moves()

				# Update the piece_moves bitboard
				piece_moves -= move

			current_active_white_pieces -= piece

	if depth == current_depth:
		return nodes

def calculate_black_perft(depth, current_depth):
	global nodes

	if current_depth == 0:
		nodes += 1

	else:
		# store the current position
		position_memento = PositionMemento()
		generate_moves()

		# Loop through all pieces' moves
		current_active_black_pieces = active_black_pieces

		while current_active_black_pieces > 0:
			piece = current_active_black_pieces & -current_active_black_pieces

			piece_moves = pieces[piece].moves

			while piece_moves > 0:

				# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
				move = piece_moves & -piece_moves
				eightx_y = bit_significance_mapping[move]

				# Make move and return value of board (without graphics)
				pieces[piece].move_piece(eightx_y)

				# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
				# Otherwise, call the move function of the opposing side. 
				position_value = calculate_white_perft(depth, current_depth - 1)

				# restore game state using Memento
				position_memento.restore_current_position()
				generate_moves()

				# Update the piece_moves bitboard
				piece_moves -= move

			current_active_black_pieces -= piece

	if depth == current_depth:
		return nodes

# ****************************************************************************
# ************************ COMMAND LINE OPTIONS *****************************
# ****************************************************************************

# No Computer Player
if len(sys.argv) == 1:
	computer_plays = ''
	initialize_board_display()
	initialize_with_start_position()
	root.mainloop()

# Computer plays black or white
elif len(sys.argv) == 2:
	initialize_board_display()
	initialize_with_start_position()

	# Computer plays white
	if sys.argv[1] == 'white':
		computer_plays = 'white'

		# Play the move
		computer_start = logger.return_timestamp()
		computer_move(computer_plays)
		computer_end = logger.return_timestamp()

		# Record statistics
		nps = nodes / ((computer_end - computer_start)/1000.0)
		logger.log("nodes: " + str(nodes))
		logger.log("nps: " + str(nps))
		logger.log("************************************")
		nodes = 0

		root.mainloop()
	
	# Computer plays black
	if sys.argv[1] == 'black':
		computer_plays = 'black'
		root.mainloop()

# Load from Forsyth-Edwards notation
# Specification found here: https://www.chessclub.com/user/help/PGN-spec (section 16.1)
elif len(sys.argv) == 3:
	if sys.argv[1] == 'fen':
		computer_plays = ''
		initialize_board_display()
		initialize_with_fen_position(sys.argv[2])
		root.mainloop()
# Calculate perft to a specific depth from a position specified in FEN
elif len(sys.argv) == 4:
	if sys.argv[1] == 'perft':
		
		if not sys.argv[3].isdigit():
			print ('The depth parameter must be a digit.')
		else:
			depth = int(sys.argv[3])

		computer_plays = ''
		initialize_with_fen_position(sys.argv[2])

		
		if white_to_move:
			start = logger.return_timestamp()
			nodes = calculate_white_perft(depth, depth)
			end = logger.return_timestamp()
		else:
			start = logger.return_timestamp()
			nodes = calculate_black_perft(depth, depth)
			end = logger.return_timestamp()
	nps = nodes / ((end - start)/1000.0)

	print('Nodes:', nodes, ', NPS:', int(nps), 'Seconds:', round(((end - start)/1000),2))

else: 
	print('Please initialize the program with one of the following options:')
	print('1: python chessboard.py')
	print('2: python chessboard.py white')
	print('3: python chessboard.py black')
	print('4: python chessboard.py fen [FEN]')
	print('5: python chessboard.py perft [FEN] [DEPTH]')