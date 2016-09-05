# ************************* INCLUDES ***********************
import sys
from tkinter import *
from logger_class import *
from constant_bitboards import *
from display_classes import *

# **********************************************************
# ***************** MEMENTO (stores a board state) ************************
# **********************************************************
class PositionMemento():
	def __init__(self):
		# Store last-move variables
		self.former_white_to_move = white_to_move
		self.former_halfmove_clock = halfmove_clock

		# Store en passant square
		self.former_en_passant_square = en_passant_square

		# Store castle variables
		self.former_castles = castles

		# Store piece positions
		self.former_all_white_positions = all_white_positions
		self.former_all_black_positions = all_black_positions

		# Store pinners (this can change, because of queen promotion)
		self.former_white_pinners = white_pinners[:]
		self.former_black_pinners = black_pinners[:]

		# Store position
		self.board = board

	def restore_current_position(self):
		global white_to_move
		global castles
		global halfmove_clock
		global all_white_positions
		global all_black_positions
		global board
		global white_pinners
		global black_pinners
		global en_passant_square

		# Restore last-move variables
		white_to_move = self.former_white_to_move
		halfmove_clock = self.former_halfmove_clock

		# Restore en passant square
		en_passant_square = self.former_en_passant_square

		# Restore castle variables
		castles = self.former_castles

		# Restore piece positions
		all_white_positions = self.former_all_white_positions
		all_black_positions = self.former_all_black_positions

		# Restore pinners
		white_pinners = self.former_white_pinners[:]
		black_pinners = self.former_black_pinners[:]

		board = self.board

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
	if board_display.selected == -1:
		if board[eightx_y] != '-' and (white_to_move and board[eightx_y] in ['P', 'N', 'B', 'R', 'Q', 'K']) or (not white_to_move and board[eightx_y] in ['p', 'n', 'b', 'r', 'q', 'k']):
			select_piece(x, y, eightx_y)

	# If a piece is selected and the user has made a legal move
	elif (board_display.selected, eightx_y) in (white_move_list | black_move_list):
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
			logger.log("seconds: " + str(((computer_end - computer_start)/1000.0)))
			logger.log("************************************")
			nodes = 0

			generate_moves()

	# If a piece is selected and the user has made a non-move click
	else:
		deselect_piece()

def select_piece(x, y, eightx_y):
	# Color the selected square and redraw the piece
	if square_display[x][y].color == "#789":
		square_display[x][y].color = "#987"
	elif square_display[x][y].color == "#567":
		square_display[x][y].color = "#765"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, board[eightx_y])

	# Store which piece is selected, and which square has been highlighted
	board_display.selected = eightx_y
	board_display.highlighted_square = [x, y]

def deselect_piece():
	x = board_display.highlighted_square[0]
	y = board_display.highlighted_square[1]

	if square_display[x][y].color == "#987":
		square_display[x][y].color = "#789"
	elif square_display[x][y].color == "#765":
		square_display[x][y].color = "#567"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, board[8*x+y])
	board_display.selected = -1
	board_display.highlighted_square = []

def move_selected_piece(eightx_y):
	global white_to_move
	global fullmove_number

	# Move the piece
	if white_to_move:
		make_white_move(board_display.selected, eightx_y)
	else:
		make_black_move(board_display.selected, eightx_y)

	# Deselect the piece
	board_display.selected = -1

	# Increment the fullmove counter
	if not white_to_move:
		fullmove_number += 1

	# Change whose turn it is to move
	white_to_move = not white_to_move

	# Recolor the origin square
	board_display.render_position(board, square_display)

# ****************************************************************************
# ******************************** MOVING ************************************
# ****************************************************************************
def make_white_move(origin, destination):
	global halfmove_clock
	global all_white_positions
	global white_pinners
	global board
	global castles
	global en_passant_square

	piece = board[origin]
	all_white_positions += 1 << destination

	# Leave the current square
	white_leave_square(origin)

	# Kill the opposing piece, if any
	if board[destination] != '-':
		black_leave_square(destination, True)

	board = board[:destination] + piece + board[destination + 1:]

	# Only pawns have to deal with en passant attacks, queen promotion, and setting the halfmove clock to 0
	if piece == 'P':
		# En passant
		if destination == en_passant_square:
			black_leave_square(en_passant_square - 1, True)
		# Queen promotion
		if destination % 8 == 7:
			board = board[:destination] + 'Q' + board[destination + 1:]
			white_pinners.append(destination)

		# Reset the half-move clock
		halfmove_clock = 0
	else:
		halfmove_clock += 1

	# Kings and their castles.....
	if piece == 'K':
		# If he's not castling, remove castles
		if castles & 0b1100 > 0:
			castles &= 0b0011

		if origin - destination == 16:
			make_white_move(0, 24) # Queen's side
		elif origin - destination == -16:
			make_white_move(56, 40)

	# En passant detection
	if piece == 'P' and destination - origin == 2:
		en_passant_square = origin + 1
	else:
		en_passant_square = -1

	# Update pinner location
	if piece in ['B', 'R', 'Q']:
		white_pinners.remove(origin)
		white_pinners.append(destination)

def white_leave_square(square_to_leave, captured = False):
	global halfmove_clock
	global all_white_positions
	global board
	global castles

	# Deal with castling
	if board[square_to_leave] == 'R':
		if square_to_leave == 56:
			castles &= 0b0111
		elif square_to_leave == 0:
			castles &= 0b1011

	# Deal with captures
	if captured:
		halfmove_clock = 0
		if board[square_to_leave] in ['B', 'R', 'Q']:
			white_pinners.remove(square_to_leave)

	# Remove from boards and bitboards.
	all_white_positions -= 1 << square_to_leave
	board = board[:square_to_leave] + '-' + board[square_to_leave + 1:]

def make_black_move(origin, destination):
	global halfmove_clock
	global all_black_positions
	global black_pinners
	global board
	global castles
	global en_passant_square

	piece = board[origin]
	all_black_positions += 1 << destination

	# Leave the current square
	black_leave_square(origin)

	# Kill the opposing piece, if any
	if board[destination] != '-':
		white_leave_square(destination, True)

	board = board[:destination] + piece + board[destination + 1:]

	# Only pawns have to deal with en passant attacks, queen promotion, and setting the halfmove clock to 0
	if piece == 'p':
		# En passant
		if destination == en_passant_square:
			white_leave_square(en_passant_square + 1, True)
		# Queen promotion
		if destination % 8 == 0:
			board = board[:destination] + 'q' + board[destination + 1:]
			black_pinners.append(destination)

		# Reset the half-move clock
		halfmove_clock = 0
	else:
		halfmove_clock += 1

	# Kings and their castles.....
	if piece == 'k':
		# If he's not castling, remove castles
		if castles & 0b0011 > 0:
			castles &= 0b1100

		if origin - destination == 16:
			make_black_move(7, 31) # Queen's side
		elif origin - destination == -16:
			make_white_move(63, 47)

	# En passant detection
	if piece == 'p' and destination - origin == -2:
		en_passant_square = origin - 1
	else:
		en_passant_square = -1

	# Update pinner location
	if piece in ['b', 'r', 'q']:
		black_pinners.remove(origin)
		black_pinners.append(destination)

def black_leave_square(square_to_leave, captured = False):
	global halfmove_clock
	global all_black_positions
	global board
	global castles

	# Deal with castling
	if board[square_to_leave] == 'r':
		if square_to_leave == 63:
			castles &= 0b1101
		elif square_to_leave == 7:
			castles &= 0b1110

	# Deal with captures
	if captured:
		halfmove_clock = 0
		if board[square_to_leave] in ['b', 'r', 'q']:
			black_pinners.remove(square_to_leave)

	# Remove from boards and bitboards.
	all_black_positions -= 1 << square_to_leave
	board = board[:square_to_leave] + '-' + board[square_to_leave + 1:]

# ****************************************************************************
# ************************** MOVE GENERATION *********************************
# ****************************************************************************

def calculate_white_pawn_move(eightx_y):
	global all_white_moves
	global white_move_list

	moves = white_pawn_moves[eightx_y] & ~all_piece_positions

	# The precalculated "third_rank_shifted_to_fourth" is used to prevent a pawn from hopping over a piece on its first move.
	if eightx_y % 8 == 1:
		moves &= ~third_rank_shifted_to_fourth

	# Deal with pawn attacks
	moves += white_pawn_attacks[eightx_y] & all_black_positions

	# Because "all_white_moves"  is really just a list of squares the black king can't move onto, add all potential pawn attacks to it, but not the regular pawn moves.
	all_white_moves |= white_pawn_attacks[eightx_y]

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_white_knight_move(eightx_y):
	global all_white_moves
	global white_move_list

	moves = knight_move_bitboards[eightx_y] & ~all_white_positions
	all_white_moves = all_white_moves | knight_move_bitboards[eightx_y]

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_white_bishop_move(eightx_y):
	# This is based on the same bitboard methodology as the rank and file stuff. But the diagonals are all different lengths, whereas the ranks and files are all of equal length.
	global all_white_moves
	global white_move_list

	# Calculate the a1_h8 diagonal moves
	bitshift_amount = a1_h8_bitshift_amounts[eightx_y]
	occupancy = (all_piece_positions >> bitshift_amount) & 0b1000000001000000001000000001000000001000000001000000001000000001
	potential_moves = (a1_h8_diagonal_bitboards[occupancy][a1_h8_positions[eightx_y]] & a1_h8_lengths[eightx_y]) << bitshift_amount

	# Calculate the a8_h1 diagonal moves
	bitshift_amount = a8_h1_bitshift_amounts[eightx_y]
	if bitshift_amount < 0:
		occupancy = (all_piece_positions << abs(bitshift_amount)) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= ((a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) >> abs(bitshift_amount))
	else:
		occupancy = (all_piece_positions >> bitshift_amount) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= ((a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) << bitshift_amount)

	moves = potential_moves & ~all_white_positions
	all_white_moves |= potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_white_rook_move(eightx_y):
	global all_white_moves
	global white_move_list

 	# File moves
	occupancy = (all_piece_positions >> (eightx_y - (eightx_y % 8))) & 0b11111111
	potential_moves = file_bitboards[eightx_y % 8][occupancy] << (eightx_y - (eightx_y % 8))

	# Rank moves
	occupancy = (all_piece_positions >> (eightx_y % 8)) & 0b100000001000000010000000100000001000000010000000100000001
	potential_moves |= (rank_bitboards[occupancy][eightx_y // 8] << (eightx_y % 8))

	moves = potential_moves & ~all_white_positions
	all_white_moves = all_white_moves | potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_white_queen_move(eightx_y):
	global all_white_moves
	global white_move_list

	# Calculate the a1_h8 diagonal moves
	bitshift_amount = a1_h8_bitshift_amounts[eightx_y]
	occupancy = (all_piece_positions >> bitshift_amount) & 0b1000000001000000001000000001000000001000000001000000001000000001
	potential_moves = (a1_h8_diagonal_bitboards[occupancy][a1_h8_positions[eightx_y]] & a1_h8_lengths[eightx_y]) << bitshift_amount
	
	# Calculate the a8_h1 diagonal moves
	bitshift_amount = a8_h1_bitshift_amounts[eightx_y]
	if bitshift_amount < 0:
		occupancy = (all_piece_positions << abs(bitshift_amount)) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= ((a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) >> abs(bitshift_amount))
	else:
		occupancy = (all_piece_positions >> bitshift_amount) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= ((a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) << bitshift_amount)

 	# Calculate file moves
	occupancy = (all_piece_positions >> (eightx_y - (eightx_y % 8))) & 0b11111111
	potential_moves |= (file_bitboards[eightx_y % 8][occupancy] << (eightx_y - (eightx_y % 8)))

	# Calculate rank moves
	occupancy = (all_piece_positions >> (eightx_y % 8)) & 0b100000001000000010000000100000001000000010000000100000001
	potential_moves |= (rank_bitboards[occupancy][eightx_y // 8] << (eightx_y % 8))

	moves = potential_moves & ~all_white_positions
	
	# Update the all_white_moves bitboard
	all_white_moves = all_white_moves | potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_white_king_move():
	global white_move_list

	# Make sure not to move onto a square the opposing king can move onto
	# Make sure not to move onto a square that an enemy piece may move onto
	# Remove friendly pieces from potential moves
	moves = king_move_bitboards[white_king_eightx_y] & ~(king_move_bitboards[black_king_eightx_y] | all_black_moves | all_white_positions)

	# Column A castle
	# If neither the king nor the rook has moved and relevant squares are empty
	if castles & 0b0100 > 0 and all_piece_positions & 0b1000000010000000100000000 == 0:
		# If the king is not in check and would not have to move through check
		if all_black_moves & 0b100000001000000010000000000000000 == 0:
			moves += 1<<16

	# Column H castle
	# If neither the king nor the rook has moved and relevant squares are empty
	if castles & 0b1000 > 0 and all_piece_positions & 0b1000000010000000000000000000000000000000000000000 == 0:
		# If the king is not in check and would not have to move through check
		if all_black_moves & 0b1000000010000000000000000000000000000000000000000 == 0:
			moves += 1<<48

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		white_move_list.add((white_king_eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_pawn_move(eightx_y):
	global all_black_moves
	global black_move_list

	moves = black_pawn_moves[eightx_y] & ~all_piece_positions

	# The precalculated "sixth_rank_shifted_to_fifth" is used to prevent a pawn from hopping over a piece on its first move.
	if eightx_y % 8 == 6:
		moves &= ~sixth_rank_shifted_to_fifth

	# Deal with pawn attacks
	moves += (black_pawn_attacks[eightx_y] & all_white_positions)

	# Because "all_black_moves"  is really just a list of squares the white king can't move onto, add all potential pawn attacks to it, but not the regular pawn moves.
	all_black_moves |= black_pawn_attacks[eightx_y]

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_knight_move(eightx_y):
	global all_black_moves
	global black_move_list

	moves = knight_move_bitboards[eightx_y] & ~all_black_positions
	all_black_moves |= knight_move_bitboards[eightx_y]

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_bishop_move(eightx_y):
	# This is based on the same bitboard methodology as the rank and file stuff. But the diagonals are all different lengths, whereas the ranks and files are all of equal length.
	global all_black_moves
	global black_move_list

	# Calculate the a1_h8 diagonal moves
	bitshift_amount = a1_h8_bitshift_amounts[eightx_y]
	occupancy = (all_piece_positions >> bitshift_amount) & 0b1000000001000000001000000001000000001000000001000000001000000001
	potential_moves = (a1_h8_diagonal_bitboards[occupancy][a1_h8_positions[eightx_y]] & a1_h8_lengths[eightx_y]) << bitshift_amount

	# Calculate the a8_h1 diagonal moves
	bitshift_amount = a8_h1_bitshift_amounts[eightx_y]
	if bitshift_amount < 0:
		occupancy = ((all_piece_positions << abs(bitshift_amount)) & 0b100000010000001000000100000010000001000000100000010000000)
		potential_moves |= (a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) >> abs(bitshift_amount)
	else:
		occupancy = (all_piece_positions >> bitshift_amount) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= (a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) << bitshift_amount

	moves = potential_moves & ~all_black_positions
	all_black_moves |= potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_rook_move(eightx_y):
	global all_black_moves
	global black_move_list

	# File moves
	occupancy = (all_piece_positions >> (eightx_y - (eightx_y % 8))) & 0b11111111
	potential_moves = file_bitboards[eightx_y % 8][occupancy] << (eightx_y - (eightx_y % 8))

	# Rank moves
	occupancy = (all_piece_positions >> (eightx_y % 8)) & 0b100000001000000010000000100000001000000010000000100000001
	potential_moves |= (rank_bitboards[occupancy][eightx_y // 8] << (eightx_y % 8))

	moves = potential_moves & ~all_black_positions
	all_black_moves |= potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_queen_move(eightx_y):
	global all_black_moves
	global black_move_list

	# a1_h8 diagonal moves
	bitshift_amount = a1_h8_bitshift_amounts[eightx_y]
	occupancy = (all_piece_positions >> bitshift_amount) & 0b1000000001000000001000000001000000001000000001000000001000000001
	potential_moves = (a1_h8_diagonal_bitboards[occupancy][a1_h8_positions[eightx_y]] & a1_h8_lengths[eightx_y]) << bitshift_amount

	# a8_h1 diagonal moves
	bitshift_amount = a8_h1_bitshift_amounts[eightx_y]
	if bitshift_amount < 0:
		occupancy = ((all_piece_positions << abs(bitshift_amount)) & 0b100000010000001000000100000010000001000000100000010000000)
		potential_moves |= (a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) >> abs(bitshift_amount)
	else:
		occupancy = (all_piece_positions >> bitshift_amount) & 0b100000010000001000000100000010000001000000100000010000000
		potential_moves |= (a8_h1_diagonal_bitboards[occupancy][a8_h1_positions[eightx_y]] & a8_h1_lengths[eightx_y]) << bitshift_amount

	# File moves
	occupancy = (all_piece_positions >> (eightx_y - (eightx_y % 8))) & 0b11111111
	potential_moves |= file_bitboards[eightx_y % 8][occupancy] << (eightx_y - (eightx_y % 8))

	# Rank moves
	occupancy = (all_piece_positions >> (eightx_y % 8)) & 0b100000001000000010000000100000001000000010000000100000001
	potential_moves |= (rank_bitboards[occupancy][eightx_y // 8] << (eightx_y % 8))

	moves = potential_moves & ~all_black_positions
	all_black_moves |= potential_moves

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((eightx_y, bit_significance_mapping[move]))
		moves -= move

def calculate_black_king_move():
	global black_move_list

	# Don't move onto a square the opposing king can move onto
	# Don't move onto a square that an enemy piece may move onto
	# Remove friendly pieces from potential moves
	moves = king_move_bitboards[black_king_eightx_y] & ~(king_move_bitboards[white_king_eightx_y] | all_white_moves | all_black_positions)

	# Column A castle
	# If neither the king nor the rook has moved and relevant squares are empty
	if castles & 0b0001 > 0 and all_piece_positions & 0b10000000100000001000000000000000 == 0:
		# If the king is not in check and would not have to move through check
		if all_white_moves & 0b1000000010000000100000000000000000000000 == 0:
			moves += 1<<23

	# Column H castle
	# If neither the king nor the rook has moved and relevant squares are empty
	if castles & 0b0010 > 0 and all_piece_positions & 0b10000000100000000000000000000000000000000000000000000000 == 0:
		# If the king is not in check and would not have to move through check
		if all_white_moves & 0b10000000100000000000000000000000000000000000000000000000 == 0:
			moves += 1<<55

	# Add this piece's moves to the move list
	while moves > 0:
		move = moves & -moves
		black_move_list.add((black_king_eightx_y, bit_significance_mapping[move]))
		moves -= move

# These two functions will return lists of tuples:
# [(pinned piece location, pinning piece location), (pinned piece location, pinning piece location)].
def find_pinned_white_pieces():
	global pinned_white_pieces

	for pinning_piece_position in black_pinners:
		# Check to see if the the king and the pinning piece are on an array
		if board[pinning_piece_position] in ['r', 'q'] and ((1 << white_king_eightx_y) + (1 << pinning_piece_position)) in intervening_squares_rank_and_file_bb:
			intervening_squares = intervening_squares_rank_and_file_bb[(1 << white_king_eightx_y) + (1 << pinning_piece_position)]

		elif board[pinning_piece_position] in ['b', 'q'] and ((1 << white_king_eightx_y) + (1 << pinning_piece_position)) in intervening_squares_diagonal_bb:
			intervening_squares = intervening_squares_diagonal_bb[(1 << white_king_eightx_y) + (1 << pinning_piece_position)]
		else:
			continue

		if all_black_positions & intervening_squares == 0:
			# Otherwise, there can only be friendly pieces between.
			# If there is more than one friendly piece in the intervening squares, there is no pin.
			if all_white_positions & intervening_squares in bit_significance_mapping:
				pinned_white_pieces.append((bit_significance_mapping[all_white_positions & intervening_squares], pinning_piece_position))

def find_pinned_black_pieces():
	global pinned_black_pieces

	for pinning_piece_position in white_pinners:
		# Check to see if the the king and the pinning piece are on an array
		if board[pinning_piece_position] in ['R', 'Q'] and ((1 << black_king_eightx_y) + (1 << pinning_piece_position)) in intervening_squares_rank_and_file_bb:
			intervening_squares = intervening_squares_rank_and_file_bb[(1 << black_king_eightx_y) + (1 << pinning_piece_position)]

		elif board[pinning_piece_position] in ['B', 'Q'] and ((1 << black_king_eightx_y) + (1 << pinning_piece_position)) in intervening_squares_diagonal_bb:
			intervening_squares = intervening_squares_diagonal_bb[(1 << black_king_eightx_y) + (1 << pinning_piece_position)]
		else:
			continue

		if all_white_positions & intervening_squares == 0:
			# Otherwise, there can only be friendly pieces between.
			# If there is more than one friendly piece in the intervening squares, there is no pin.
			if all_black_positions & intervening_squares in bit_significance_mapping:
				pinned_black_pieces.append((bit_significance_mapping[all_black_positions & intervening_squares], pinning_piece_position))

def generate_moves():
	global checkers
	global pinned_white_pieces
	global pinned_black_pieces
	global all_white_moves
	global all_black_moves
	global all_piece_positions
	global third_rank_shifted_to_fourth
	global sixth_rank_shifted_to_fifth
	global white_king_eightx_y
	global black_king_eightx_y
	global white_move_list
	global black_move_list

	# Reset board variables
	# (the king locations will be reset with correct numbers when the board is scanned, anyway, so they don't need to be re-initialized)
	checkers = []
	pinned_white_pieces = []
	pinned_black_pieces = []
	white_move_list = set([])
	black_move_list = set([])

	# Erase the bitboards that are maintained by the *.calculate_moves functions
	all_white_moves = 0
	all_black_moves = 0

	# Populate the piece position bitboards
	all_piece_positions = all_white_positions | all_black_positions
	third_rank_shifted_to_fourth = (all_piece_positions & 0b10000000100000001000000010000000100000001000000010000000100) << 1
	sixth_rank_shifted_to_fifth = (all_piece_positions & 0b10000000100000001000000010000000100000001000000010000000100000) >> 1 

	# Recalculate all necessary information
	i = 0
	for character in board:
		if character != '-':
			if character.isupper():
				if character == 'P':
					calculate_white_pawn_move(i)
				elif character == 'N':
					calculate_white_knight_move(i)
				elif character == 'B':
					calculate_white_bishop_move(i)
				elif character == 'R':
					calculate_white_rook_move(i)
				elif character == 'Q':
					calculate_white_queen_move(i)
				elif character == 'K':
					white_king_eightx_y = i
			else:
				if character == 'p':
					calculate_black_pawn_move(i)
				elif character == 'n':
					calculate_black_knight_move(i)
				elif character == 'b':
					calculate_black_bishop_move(i)
				elif character == 'r':
					calculate_black_rook_move(i)
				elif character == 'q':
					calculate_black_queen_move(i)
				elif character == 'k':
					black_king_eightx_y = i
		i += 1

	# Check for en passant
	if en_passant_square != -1:
		if en_passant_square % 8 == 2: # Black's attack.
			if en_passant_square > 2:
				if board[en_passant_square - 7] == 'p':
					black_move_list.add((en_passant_square - 7, en_passant_square))
			if en_passant_square < 58:
				if board[en_passant_square + 9] == 'p':
					black_move_list.add((en_passant_square + 9, en_passant_square))
		else: # White's attack 
			if en_passant_square > 5:
				if board[en_passant_square - 9] == 'P':
					white_move_list.add((en_passant_square - 9, en_passant_square))
			if en_passant_square < 61:
				if board[en_passant_square + 7] == 'P':
					white_move_list.add((en_passant_square + 7, en_passant_square))

	# DETECT WHITE PINS ON WHITE PIECES
	find_pinned_white_pieces()

	# A pinned piece may only move on the ray between the king and the pinning piece.
	# Thus, pawns may advance toward a pinning piece, or a bishop may take a queen that pins on the diagonal.
	for pin in pinned_white_pieces:
		pinned_piece_position = 1 << pin[0]
		pinning_piece_position = 1 << pin[1]

		king_position = 1 << white_king_eightx_y

		# A pinned piece can only move on the ray between the king and the pinning piece. 
		potential_moves = intervening_squares_bitboards[king_position + pinning_piece_position] - pinned_piece_position + pinning_piece_position

		potential_move_list = []
		while potential_moves > 0:
			potential_move = potential_moves & -potential_moves
			potential_move_list.append((pin[0], bit_significance_mapping[potential_move]))
			potential_moves -= potential_move

		# Before removing moves, see if this piece is checking the opposing king, and if so, add it to the checkers array
		if (pin[0], black_king_eightx_y) in white_move_list:
			checkers.append(pin[0])

		# Remove moves
		moves_to_remove = set([])
		for move in white_move_list:
			if move[0] == pin[0] and move not in potential_move_list:
				moves_to_remove.add(move)

		white_move_list = white_move_list - moves_to_remove

	# DETECT BLACK PINS ON BLACK PIECES
	find_pinned_black_pieces()

	for pin in pinned_black_pieces:
		pinned_piece_position = 1 << pin[0]
		pinning_piece_position = 1 << pin[1]

		king_position = 1 << black_king_eightx_y

		# A pinned piece can only move on the ray between the king and the pinning piece. 
		potential_moves = intervening_squares_bitboards[king_position + pinning_piece_position] - pinned_piece_position + pinning_piece_position

		potential_move_list = []
		while potential_moves > 0:
			potential_move = potential_moves & -potential_moves
			potential_move_list.append((pin[0], bit_significance_mapping[potential_move]))
			potential_moves -= potential_move

		# Before removing moves, see if this piece is checking the opposing king, and if so, add it to the checkers array
		if (pin[0], white_king_eightx_y) in black_move_list:
			checkers.append(pin[0])

		# Remove moves
		moves_to_remove = set([])
		for move in black_move_list:
			if move[0] == pin[0] and move not in potential_move_list:
				moves_to_remove.add(move)

		black_move_list = black_move_list - moves_to_remove

	# CALCULATE KING MOVES
	calculate_white_king_move()
	calculate_black_king_move()

	# DETECT CHECKS
	if white_to_move:
		if all_black_moves & 1 << white_king_eightx_y > 0:
			# If the king is in check, discover the type and location of the checking pieces
			for move in black_move_list:
				if move[1] == white_king_eightx_y:
					checkers.append(move[0])

			# Calculate the moves that friendly pieces can perform to save the king
			calculate_white_check_moves()
	else:
		if all_white_moves & 1 << black_king_eightx_y > 0:

			# If the king is in check, discover the type and location of the checking pieces
			for move in white_move_list:
				if move[1] == black_king_eightx_y:
					checkers.append(move[0])

			# Calculate the moves that friendly pieces can perform to save the king
			calculate_black_check_moves()

def calculate_white_check_moves():
	global white_move_list

	defence_moves = 0
	number_of_checkers = len(checkers)

	# If there is one piece checking the king, then friendly pieces can save the king
	# If there is more than one piece checking the king, then only the king can save himself.
	if number_of_checkers == 1:
		# If there's only one checker, capturing it is always an option
		defence_moves += 1 << checkers[0]

		# If the single checking piece is not a pawn or a knight, then the checked side can defend also defend by interposing a piece
		if board[checkers[0]] in ['b', 'r', 'q']:
			if ((1 << white_king_eightx_y) + (1 << checkers[0])) in intervening_squares_bitboards:
				defence_moves += intervening_squares_bitboards[(1 << white_king_eightx_y) + (1 << checkers[0])]

	# Unpack the defense moves bitboard.
	defence_move_list = []
	while defence_moves > 0:
		defence_move_list.append(bit_significance_mapping[defence_moves & -defence_moves])
		defence_moves -= (defence_moves & -defence_moves)

	# Get a list of moves to remove
	moves_to_remove = set([])
	for move in white_move_list:
		if move[0] != white_king_eightx_y and move[1] not in defence_move_list:
			moves_to_remove.add(move)

	# If the king is being checked by a ray piece, He may not move away from a checking ray piece on the ray that he is being checked with.
	for checker in checkers:
		if board[checker] in ['b', 'r', 'q']:
			moves_to_remove.add((white_king_eightx_y, white_king_eightx_y + get_vector(checker, white_king_eightx_y)))

	white_move_list = white_move_list - moves_to_remove

def calculate_black_check_moves():
	global black_move_list

	defence_moves = 0
	number_of_checkers = len(checkers)

	# If there is one piece checking the king, then friendly pieces can save the king
	# If there is more than one piece checking the king, then only the king can save himself.
	if number_of_checkers == 1:
		# If there's only one checker, capturing it is always an option
		defence_moves += 1 << checkers[0]

		# If the single checking piece is not a pawn or a knight, then the checked side can defend also defend by interposing a piece
		if board[checkers[0]] in ['B', 'R', 'Q']:
			if ((1 << black_king_eightx_y) + (1 << checkers[0])) in intervening_squares_bitboards:
				defence_moves += intervening_squares_bitboards[(1 << black_king_eightx_y) + (1 << checkers[0])]

	# Unpack the defense moves bitboard.
	defence_move_list = []
	while defence_moves > 0:
		defence_move_list.append(bit_significance_mapping[defence_moves & -defence_moves])
		defence_moves -= (defence_moves & -defence_moves)

	# Get a list of moves to remove
	moves_to_remove = set([])
	for move in black_move_list:
		if move[0] != black_king_eightx_y and move[1] not in defence_move_list:
			moves_to_remove.add(move)

	# If the king is being checked by a ray piece, He may not move away from a checking ray piece on the ray that he is being checked with.
	for checker in checkers:
		if board[checker] in ['B', 'R', 'Q']:
			moves_to_remove.add((black_king_eightx_y, black_king_eightx_y + get_vector(checker, black_king_eightx_y)))

	black_move_list = black_move_list - moves_to_remove

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

# ****************************************************************************
# ***************************** EVALUATION ***********************************
# ****************************************************************************
def evaluate_position():
	global nodes
	position_value = 0

	for i in range(64):
		position_value += piece_values[board[i]]

	nodes += 1
	return position_value

# ****************************************************************************
# ******************************* SEARCH *************************************
# ****************************************************************************
def computer_move(computer_plays):
	if computer_plays == 'white':
		calculation_result = calculate_white_move(4, 4, -20000, 20000)

		# Calculate_white_move will return either -1 or a dictionary containing instructions for moving. =1 means checkmate.
		if calculation_result == -1: # Checkmate
			print("Checkmate has occurred. Black wins.")
			return

		# Unpack the return dictionary	
		best_move_origin = calculation_result.get("best_move_origin")
		best_move_destination = calculation_result.get("best_move_destination")

		# Move the piece, with graphics.
		board_display.selected = best_move_origin
		move_selected_piece(best_move_destination)


	elif computer_plays == 'black':
		calculation_result = calculate_black_move(4, 4, -20000, 20000)

		# Calculate_black_move will return either -1 or a dictionary containing instructions for moving. -1 means checkmate.
		if calculation_result == -1: # Checkmate
			print("Checkmate has occurred. White wins.")
			return

		# Unpack the return dictionary	
		best_move_origin = calculation_result.get("best_move_origin")
		best_move_destination = calculation_result.get("best_move_destination")

		# Move the piece, with graphics.
		board_display.selected = best_move_origin
		move_selected_piece(best_move_destination)
	
def calculate_white_move(depth, current_depth, alpha, beta):
	global white_to_move

	# store the current position, as well as the last move variables (for en passant detection)
	position_memento = PositionMemento()
	generate_moves()

	# Initialize the best_move_origin as an impossible value, to allow detection of checkmate
	best_move_origin = -1
	best_position_value = -20000

	# Find all moves for this node.
	move_list = list(white_move_list)[:]

	for move in move_list:
		# Make move and return value of board (without graphics)
		make_white_move(move[0], move[1])

		# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
		# Otherwise, call the move function of the opposing side. 
		if current_depth == 0:
			position_value = evaluate_position()
		else:
			white_to_move = not white_to_move
			position_value = calculate_black_move(depth, current_depth - 1, alpha, beta)

		position_memento.restore_current_position()

		# compare value of move with previous high move value
		if position_value > best_position_value:
			best_position_value = position_value
			best_move_origin = move[0]
			best_move_destination = move[1]

		# Alpha beta logic
		if position_value > alpha:
			alpha = position_value

		if beta <= alpha:
			if depth != current_depth: # Not root node
				if best_move_origin == -1: # Checkmate has occurred.
					return -20000
				else:
					return best_position_value
			else: # root node
				if best_move_origin == -1: # Checkmate has occurred.
					return -1
				else: 
					return {"best_move_origin": best_move_origin, "best_move_destination": best_move_destination}

	# For any node but the root of the tree, the function should return the calculate value of the position.
	# For the root node of the tree, the function should return a piece index, and the x, y values of the best move.
	# If checkmate has occurred in a branch, return an arbitrarily large number as the value of the position.
	# If checkmate has occurred in the root node, return -1 as the piece index.
	if depth != current_depth: # Not root node
		if best_move_origin == -1: # Checkmate has occurred.
			return -20000
		else:
			return best_position_value
	else: # root node
		if best_move_origin == -1: # Checkmate has occurred.
			return -1
		else: 
			return {"best_move_origin": best_move_origin, "best_move_destination": best_move_destination}

def calculate_black_move(depth, current_depth, alpha, beta):
	global white_to_move

	# store the current position, as well as the last move variables (for en passant detection)
	position_memento = PositionMemento()
	generate_moves()
	
	# Initialize the best_move_origin as an impossible value, to allow detection of checkmate
	best_move_origin = -1
	best_position_value = 20000

	# Find all moves for this node.
	move_list = list(black_move_list)[:]
	for move in move_list:			
		# Make move and return value of board (without graphics)
		make_black_move(move[0], move[1])

		# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
		# Otherwise, call the move function of the opposing side. 
		if current_depth == 0:
			position_value = evaluate_position()
		else:
			white_to_move = not white_to_move
			position_value = calculate_white_move(depth, current_depth - 1, alpha, beta)

		position_memento.restore_current_position()

		# compare value of move with previous high move value
		if position_value < best_position_value:
			best_position_value = position_value
			best_move_origin = move[0]
			best_move_destination = move[1]

		# Alpha beta logic
		if position_value < beta:
			beta = position_value

		if beta <= alpha:
			if depth != current_depth: # Not root node
				if best_move_origin == -1: # Checkmate has occurred.
					return -20000
				else:
					return best_position_value
			else: # root node
				if best_move_origin == -1: # Checkmate has occurred.
					return -1
				else: 
					return {"best_move_origin": best_move_origin, "best_move_destination": best_move_destination}

	# For any node but the root of the tree, the function should return the calculate value of the position.
	# For the root node of the tree, the function should return a piece index, and the x, y values of the best move.
	# If checkmate has occurred in a branch, return an arbitrarily large number as the value of the position.
	# If checkmate has occurred in the root node, return -1 as the piece index.

	if depth != current_depth: # Not root node
		if best_move_origin == -1: # Checkmate has occurred.
			return 20000
		else:
			return best_position_value
	else: # root node
		if best_move_origin == -1: # Checkmate has occurred.
			return -1
		else: 
			return {"best_move_origin": best_move_origin, "best_move_destination": best_move_destination}

def calculate_white_perft(depth, current_depth):
	global nodes
	global white_to_move

	if current_depth == 1:
		generate_moves()
		nodes += len(white_move_list)
	else:
		position_memento = PositionMemento()
		generate_moves()

		move_list = list(white_move_list)[:]
		for move in move_list:
			make_white_move(move[0], move[1])
			white_to_move = not white_to_move
			calculate_black_perft(depth, current_depth - 1)
			position_memento.restore_current_position()

def calculate_black_perft(depth, current_depth):
	global nodes
	global white_to_move

	if current_depth == 1:
		generate_moves()
		nodes += len(black_move_list)
	else:
		position_memento = PositionMemento()
		generate_moves()

		move_list = list(black_move_list)[:]
		for move in move_list:
			make_black_move(move[0], move[1])
			white_to_move = not white_to_move
			calculate_white_perft(depth, current_depth - 1)
			position_memento.restore_current_position()

# ****************************************************************************
# *********************** INITIALIZATION FUNCTIONS ***************************
# ****************************************************************************

# Bind an event handler to the left click event
def initialize_board_display():
	board_display.bind("<Button-1>", handle_click)
	board_display.pack()

# Sets up the board in the initial position, and displays it.
def initialize_with_start_position():
	global all_white_positions
	global all_black_positions

	# Manually set up a couple bitboards
	all_white_positions = 0b0000001100000011000000110000001100000011000000110000001100000011
	all_black_positions = 0b1100000011000000110000001100000011000000110000001100000011000000

	# Generate the moves
	generate_moves()

	# Display the board
	board_display.render_position(board, square_display)

def initialize_with_fen_position(fen_string):
	global white_to_move
	global castles
	global en_passant_square
	global halfmove_clock
	global fullmove_number
	global all_white_positions
	global all_black_positions
	global board

	# Split it into separate parts
	fen_array = fen_string.split(' ')

	# Set up a blank board.
	board = '----------------------------------------------------------------'

	# 1) PIECE PLACEMENT DATA
	# Split the position string into an array, and reverse it so that we deal with rank 1 first
	position_array = list(reversed(fen_array[0].split('/')))

	# Loop through the array, parse each string, and initialize each piece
	rank_counter = 0
	for rank in position_array:
		file_counter = 0
		for character in rank:
			if character.isdigit():
				file_counter += int(character)
			else: 
				eightx_y = file_counter * 8 + rank_counter
				board = board[:eightx_y] + character + board[eightx_y + 1:]
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

		en_passant_square = 8 * target_square_file + target_square_rank
	else:
		en_passant_square = -1

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
	i = 0
	for character in board:
		if character in ['P', 'B', 'N', 'R', 'Q', 'K']:
			all_white_positions += 1 << i
		elif character in ['p', 'b', 'n', 'r', 'q', 'k']:
			all_black_positions += 1 << i
		i += 1

	# Generate the moves
	generate_moves()

	# Display the board
	board_display.render_position(board, square_display)

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
board = 'RP----prNP----pnBP----pbQP----pqKP----pkBP----pbNP----pnRP----pr'

# Default is that the computer is not playing.
computer_plays = ''

# Variables for the locations of the kings
white_king_eightx_y = -1
black_king_eightx_y = -1

# This is a list of tuples of the form [(start_square, end_square), (start_square, end_square)]
white_move_list = set([])
black_move_list = set([])

# Pin variables
white_pinners = [0, 16, 24, 40, 56] # Queen, rooks, and bishops
black_pinners = [7, 23, 31, 47, 63] # Queen, rooks, and bishops

# Active pieces
# These lists do not include the king's index. The kings will be active for the entire game.
active_white_pieces = [1, 1<<1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7, 1<<16, 1<<17, 1<<20, 1<<21, 1<<24, 1<<25, 1<<28]
active_black_pieces = [1<<8, 1<<9, 1<<10, 1<<11, 1<<12, 1<<13, 1<<14, 1<<15, 1<<18, 1<<19, 1<<22, 1<<23, 1<<26, 1<<27, 1<<29]

# En passant variables
en_passant_square = -1

# Move variables
white_to_move = True

# Castles
# The bits here are as follow:
# 1000 : White castle kingside
# 0100 : White castle queenside
# 0010 : Black castle kingside
# 0001 : Black castle queenside
castles = 0b1111

# Check variables
checkers = []

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
# "all_white_moves" and "all_black_moves" are misnamed. They only exist to prevent a king from moving onto a square that the opposing side can move onto. 
# They are not updated after pins are found. 
# They are not updated by the kings' move calculations. 
# They are not updated after check moves are calculated.
# They include unrealized pawn attacks
# They include defended pieces
all_white_moves = 0 
all_black_moves = 0

all_white_positions = 0
all_black_positions = 0

all_piece_positions = 0

third_rank_shifted_to_fourth = 0 # For use in calculating white pawns' first moves
sixth_rank_shifted_to_fifth = 0 # For use in calculating black pawns' first moves

# NOTE: This includes extra indexes for queeen promotions. All extra white queens are greater than 31, and they are even. All extra black queens are greater than 32, and they ard odd.
piece_values = {'-':0, 'P':1, 'p':-1, 'N':3, 'n':-3, 'B':3, 'b':-3, 'R':5, 'r':-5, 'Q':9, 'q':-9, 'K':10000, 'k':-10000}

nodes = 0

# ****************************************************************************
# ************************ COMMAND LINE OPTIONS *****************************
# ****************************************************************************

# Just start the game, no special options
if len(sys.argv) == 1:
	computer_plays = ''
	initialize_board_display()
	initialize_with_start_position()
	root.mainloop()

# Other options
elif len(sys.argv) > 1:
	if sys.argv[1] == 'white': # Computer plays white
		initialize_board_display()
		initialize_with_start_position()

		computer_plays = 'white'

		# Play the move
		computer_start = logger.return_timestamp()
		computer_move(computer_plays)
		computer_end = logger.return_timestamp()

		# Record statistics
		if computer_end - computer_start > 0:
			nps = nodes / ((computer_end - computer_start)/1000.0)
		else:
			nps = nodes

		logger.log("nodes: " + str(nodes))
		logger.log("nps: " + str(nps))
		logger.log("seconds: " + str(((computer_end - computer_start)/1000.0)))
		logger.log("************************************")
		nodes = 0

		root.mainloop()

	elif sys.argv[1] == 'black': # Computer plays black
		initialize_board_display()
		initialize_with_start_position()
		computer_plays = 'black'
		root.mainloop()

	elif sys.argv[1] == 'fen': # Load the board with a FEN string
		computer_plays = ''
		initialize_board_display()
		initialize_with_fen_position(sys.argv[2])

		if len(sys.argv) == 4: 
			if sys.argv[3] == 'white': # Have the computer play white in the position specified by the FEN string
				computer_plays = 'white'
				if white_to_move:

					# Play the move
					computer_start = logger.return_timestamp()
					computer_move(computer_plays)
					computer_end = logger.return_timestamp()

					# Record statistics
					if computer_end - computer_start > 0:
						nps = nodes / ((computer_end - computer_start)/1000.0)
					else:
						nps = nodes

					logger.log("nodes: " + str(nodes))
					logger.log("nps: " + str(nps))
					logger.log("seconds: " + str(((computer_end - computer_start)/1000.0)))
					logger.log("************************************")
					nodes = 0

			elif sys.argv[3] == 'black': # Have the computer play black in the position specified by the FEN string
				computer_plays = 'black'
				if not white_to_move:
					# Play the move
					computer_start = logger.return_timestamp()
					computer_move(computer_plays)
					computer_end = logger.return_timestamp()

					# Record statistics
					nps = nodes / ((computer_end - computer_start)/1000.0)
					logger.log("nodes: " + str(nodes))
					logger.log("nps: " + str(nps))
					logger.log("seconds: " + str(((computer_end - computer_start)/1000.0)))
					logger.log("************************************")
					nodes = 0

		root.mainloop()

	# Calculate perft to a specific depth from a position specified in FEN
	elif sys.argv[1] == 'perft': # Count the number of leaf nodes at particular depths of minimax search
		if not sys.argv[3].isdigit():
			print ('The depth parameter must be a digit.')
		else:
			depth = int(sys.argv[3])

		initialize_with_fen_position(sys.argv[2])

		if white_to_move:
			start = logger.return_timestamp()
			calculate_white_perft(depth, depth)
			end = logger.return_timestamp()
		else:
			start = logger.return_timestamp()
			calculate_black_perft(depth, depth)
			end = logger.return_timestamp()

		if end-start == 0:
			print('Nodes:', nodes, ', NPS:', nodes, 'Seconds:', '0')
		else:
			nps = nodes / ((end - start)/1000.0)
			print('Nodes:', nodes, ', NPS:', int(nps), 'Seconds:', round(((end - start)/1000),2))

else: 
	print('Please initialize the program with one of the following options:')
	print('1: python chessboard.py {white/black}')
	print('2: python chessboard.py fen [FEN] {white/black}')
	print('3: python chessboard.py perft [FEN] [DEPTH]')
