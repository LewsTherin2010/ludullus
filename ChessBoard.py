# ************************* INCLUDES ***********************
#from tkinter import *
import sys
import copy
import math

sys.path.append('C:\\NaiveChess\\board_classes')
sys.path.append('C:\\NaiveChess\\piece_classes')
sys.path.append('C:\\NaiveChess\\memento_classes')
sys.path.append('C:\\NaiveChess\\display_classes')

from globals_file import *
from logger_class import *
from board_class import *
from board_display_class import *
from square_class import *
from square_display_class import *
from white_piece_class import *
from black_piece_class import *

from white_king_class import *
from black_king_class import *

from white_queen_class import *
from black_queen_class import *

from white_rook_class import *
from black_rook_class import *

from white_bishop_class import *
from black_bishop_class import *

from white_knight_class import *
from black_knight_class import *

from white_pawn_class import *
from black_pawn_class import *

from position_memento_class import *

#******************** EVENT HANDLER *********************#
def handle_click (event):
	#logger.log('handle_click')

	# find coordinates of click (gives x, y coords)
	x = (event.x - board_display.x_start) // board_display.square_size
	y = 7 - (event.y - board_display.y_start) // board_display.square_size

	# If nothing is selected
	if board_display.selected == 9999:
		if squares[x][y].occupied_by != 9999 and pieces[squares[x][y].occupied_by].white == board.white_to_move:
			select_piece(x, y)

	# If a piece is selected and the user has made a legal move
	elif pieces[board_display.selected].moves & (1 << (x * 8 + y)) > 0:
		move_selected_piece(x, y)

		position = board.get_position(squares)

		generate_moves(position)

		# Let the computer play
		"""
		computer_start = logger.return_timestamp()
		computer_move()
		computer_end = logger.return_timestamp()

		nps = board.nodes / ((computer_end - computer_start)/1000.0)
		logger.log("nodes: " + str(board.nodes))
		logger.log("nps: " + str(nps))
		logger.log("************************************")
		board.nodes = 0

		position = board.get_position(squares)
		generate_moves(position)
		"""

	# If a piece is selected and the user has made a non-move click
	else:
		deselect_piece()

def select_piece(x, y):
	#logger.log('select_piece')

	# Color the selected square and redraw the piece
	if square_display[x][y].color == "#789":
		square_display[x][y].color = "#987"
	elif square_display[x][y].color == "#567":
		square_display[x][y].color = "#765"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, squares[x][y].occupied_by)

	# Store which piece is selected, and which square has been highlighted
	board_display.selected = squares[x][y].occupied_by
	board_display.highlighted_square = [x, y]

def move_selected_piece(x, y):
	#logger.log('move_selected_piece')

	# Move the piece
	pieces[board_display.selected].move_piece(x, y)

	# Deselect the piece
	board_display.selected = 9999

	# Change whose turn it is to move
	board.white_to_move = not board.white_to_move

	# Recolor the origin square
	new_position = board.get_position(squares)
	board_display.render_position(new_position, square_display)

def generate_moves(position):
	#logger.log('generate_moves')

	# Reset board variables
	board.reset_board_variables(position)

	# Erase the bitboards. These are maintained by the *.piece_move functions
	board.erase_all_bitboards()

	# Set the squares' occupied statuses to the current position
	reset_squares(position)

	# Populate the piece position bitboards
	reset_position_bitboards(position)
	
	# Recalculate all necessary information
	calculate_all_moves()
	manage_pins()
	find_white_checks()
	find_black_checks()

# If a square is occupied, get the bitwise position of the square [8x + y], and add it to the appropriate bitboard
def reset_position_bitboards(position):
	board.all_piece_positions = board.all_white_positions | board.all_black_positions
	board.third_rank_shifted_to_fourth = board.shift_third_rank_to_fourth(board.all_piece_positions) 
	board.sixth_rank_shifted_to_fifth = board.shift_sixth_rank_to_fifth(board.all_piece_positions)

def calculate_all_moves():
	#logger.log('calculate_all_moves')

	# Recalculate the moves for all active pieces except for kings
	active_white_pieces = board.active_white_pieces - (1<<30)

	while active_white_pieces > 0:
		active_piece = active_white_pieces & -active_white_pieces

		pieces[active_piece].calculate_moves()
		active_white_pieces -= active_piece

	active_black_pieces = board.active_black_pieces - (1<<31)

	while active_black_pieces > 0:
		active_piece = active_black_pieces & -active_black_pieces
		pieces[active_piece].calculate_moves()
		active_black_pieces -= active_piece

	# Do this here, rather than inside each pawn.
	check_for_en_passant()

	# Calculate moves for kings last. The black king's moves depend on the moves of the white pieces.
	pieces[1<<30].calculate_moves()
	pieces[1<<31].calculate_moves()

def deselect_piece():
	#logger.log('deselect_piece')

	x = board_display.highlighted_square[0]
	y = board_display.highlighted_square[1]

	if square_display[x][y].color == "#987":
		square_display[x][y].color = "#789"
	elif square_display[x][y].color == "#765":
		square_display[x][y].color = "#567"

	square_display[x][y].color_square()
	square_display[x][y].draw_piece(x, y, squares[x][y].occupied_by)
	board_display.selected = 9999
	board_display.highlighted_square = []

def computer_move():
	#logger.log('computer_move')

	calculation_result = calculate_black_move(2, 2)

	# Calculate_black_move will return either -1 or a dictionary containing instructions for moving. -1 means checkmate.
	if calculation_result == -1: # Checkmate
		print("Checkmate has occurred. White wins.")
	else:
		# Unpack the return dictionary	
		best_move_piece = calculation_result.get("best_move_piece")
		best_move_x = calculation_result.get("best_move_x")
		best_move_y = calculation_result.get("best_move_y")

		# Move the piece, with graphics.
		board_display.selected = best_move_piece
		move_selected_piece(best_move_x, best_move_y)

def calculate_white_move(depth, current_depth):
	#logger.log('calculate_white_move')

	# store the current position, as well as the last move variables (for en passant detection)
	position = board.get_position(squares)

	position_memento = PositionMemento()
	position_memento.store_current_position(position, board, pieces)

	generate_moves(position)

	# Loop through all pieces' moves
	current_active_white_pieces = board.active_white_pieces

	# Initialize the best_move_piece as an impossible value, to allow detection of checkmate
	best_move_piece = -1
	best_position_value = -20000

	while current_active_white_pieces > 0:
		piece = current_active_white_pieces & -current_active_white_pieces

		piece_moves = pieces[piece].moves

		while piece_moves > 0:

			# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
			move = piece_moves & -piece_moves
			x = int(round(math.log(move, 2) // 8, 0))
			y = int(round(math.log(move, 2) % 8, 0))

			# Make move and return value of board (without graphics)
			pieces[piece].move_piece(x, y)

			# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
			# Otherwise, call the move function of the opposing side. 
			if current_depth == 0:
				# Calculate the position of the board
				position_to_consider = board.get_position(squares)
				position_value = board.evaluate_position(position_to_consider)
			else:
				position_value = calculate_black_move(depth, current_depth - 1)

			# compare value of move with previous high move value
			if position_value > best_position_value:
				best_position_value = position_value
				best_move_piece = piece
				best_move_x = x
				best_move_y = y
		
			# restore game state using Memento
			restore_position = position_memento.restore_current_position(board, pieces)
			generate_moves(restore_position)

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
			return {"best_move_piece": best_move_piece, "best_move_x": best_move_x, "best_move_y": best_move_y}

def calculate_black_move(depth, current_depth):
	#logger.log('calculate_black_move')

	# store the current position, as well as the last move variables (for en passant detection)
	position = board.get_position(squares)

	position_memento = PositionMemento()
	position_memento.store_current_position(position, board, pieces)

	generate_moves(position)

	# Loop through all pieces' moves
	# (I'll need to generalize this for white or black)
	current_active_black_pieces = board.active_black_pieces

	# Initialize the best_move_piece as an impossible value, to allow detection of checkmate
	best_move_piece = -1
	best_position_value = 20000

	while current_active_black_pieces > 0:
		piece = current_active_black_pieces & -current_active_black_pieces

		piece_moves = pieces[piece].moves

		while piece_moves > 0:

			# Because of how negative numbers are stored, the bitwise and of a number and its negative will equal the smallest bit in the number.
			move = piece_moves & -piece_moves
			x = int(round(math.log(move, 2) // 8, 0))
			y = int(round(math.log(move, 2) % 8, 0))

			# Make move and return value of board (without graphics)
			pieces[piece].move_piece(x, y)

			# Recurse. If this calculation is the leaf of the search tree, find the position of the board.
			# Otherwise, call the move function of the opposing side. 
			if current_depth == 0:
				# Calculate the position of the board
				position_to_consider = board.get_position(squares)
				position_value = board.evaluate_position(position_to_consider)
			else:
				position_value = calculate_white_move(depth, current_depth - 1)

			# compare value of move with previous high move value
			if position_value < best_position_value:
				best_position_value = position_value
				best_move_piece = piece
				best_move_x = x
				best_move_y = y

			# restore game state using Memento

			restore_position = position_memento.restore_current_position(board, pieces)
			generate_moves(restore_position)

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
			return {"best_move_piece": best_move_piece, "best_move_x": best_move_x, "best_move_y": best_move_y}

def manage_pins():
	#logger.log('manage_pins')

	all_pins = []

	black_pins = pieces[1<<30].find_pins()
	white_pins = pieces[1<<31].find_pins()

	all_pins.extend(black_pins)
	all_pins.extend(white_pins)

	# A pinned piece may only move on the ray between the king and the pinning piece.
	# Thus, pawns may advance toward a pinning piece, or a bishop may take a queen that pins on the diagonal.
	for pin in all_pins:
		pinned_piece = pin['pinned_piece']
		pinning_piece = pin['pinning_piece']

		pinning_piece_position = 1 << (pieces[pinning_piece].x * 8 + pieces[pinning_piece].y)
		pinned_piece_position = 1 << (pieces[pinned_piece].x * 8 + pieces[pinned_piece].y)

		if pieces[pinned_piece].white:
			king_position = 1 << (pieces[1<<30].x * 8 + pieces[1<<30].y)
		else:
			king_position = 1 << (pieces[1<<31].x * 8 + pieces[1<<31].y)

		# Potential moves are the squares between the pinned piece and the king, if any,
		# plus the squares between the pinned piece and the pinning piece, if any,
		# plus the square that the pinning piece is on,
		# provided that the pinned piece may already move to these squares
		squares_between_king_and_pinned = 0
		squares_between_pinned_and_pinning = 0

		if king_position + pinned_piece_position in board.intervening_squares_bitboards:
			squares_between_king_and_pinned = board.intervening_squares_bitboards[king_position + pinned_piece_position]

		if pinned_piece_position + pinning_piece_position in board.intervening_squares_bitboards:
			squares_between_pinned_and_pinning = board.intervening_squares_bitboards[pinned_piece_position + pinning_piece_position]

		potential_moves = squares_between_king_and_pinned + squares_between_pinned_and_pinning + pinning_piece_position

		# Even if a white bishop is pinned, a black king still cannot move onto a square it could have moved onto.
		# So, store all the removed moves in the board, and reference that board in the king's move function.
		if pieces[pinned_piece].white:
			board.white_removed_pin_moves = board.white_removed_pin_moves | (pieces[pinned_piece].moves - (pieces[pinned_piece].moves & potential_moves))
		else:
			board.black_removed_pin_moves = board.black_removed_pin_moves | (pieces[pinned_piece].moves - (pieces[pinned_piece].moves & potential_moves))

		# Update the pinned piece
		pieces[pinned_piece].moves = pieces[pinned_piece].moves & potential_moves

def find_white_checks():
	#logger.log('find_white_checks')

	king_position = 1 << (pieces[1<<30].x * 8 + pieces[1<<30].y)

	if board.all_black_moves & king_position > 0:		
		# If the king is in check, discover the type and location of the checking pieces
		active_black_pieces = board.active_black_pieces
		while active_black_pieces > 0:
			active_pieces = active_black_pieces & -active_black_pieces
			if pieces[active_piece].moves & king_position > 1:
				board.checker_positions.append([pieces[active_piece].x, pieces[active_piece].y])
				board.checker_types.append(pieces[active_piece].type)

			active_black_pieces -= active_piece

		# Calculate the moves that friendly pieces can perform to save the king
		calculate_check_moves(board.active_white_pieces, 1<<30)

		board.all_white_moves = 0

		active_white_pieces = board.active_white_pieces
		while active_white_pieces > 0:
			active_piece = active_white_pieces & -active_white_pieces
			pieces[active_piece].add_moves_to_all_move_bitboard(board)
			active_white_pieces -= active_piece

def find_black_checks():
	#logger.log('find_black_checks')

	king_position = 1 << (pieces[1<<31].x * 8 + pieces[1<<31].y)

	if board.all_white_moves & king_position > 0:
		# If the king is in check, discover the type and location of the checking pieces
		active_white_pieces = board.active_white_pieces
		while active_white_pieces > 0:
			active_piece = active_white_pieces & -active_white_pieces
			if pieces[active_piece].moves & king_position > 1:
				board.checker_positions.append([pieces[active_piece].x, pieces[active_piece].y])
				board.checker_types.append(pieces[active_piece].type)

			active_white_pieces -= active_piece

		# Calculate the moves that friendly pieces can perform to save the king
		calculate_check_moves(board.active_black_pieces, 1<<31)

		board.all_black_moves = 0

		active_black_pieces = board.active_black_pieces
		while active_black_pieces > 0:
			active_piece = active_black_pieces & -active_black_pieces
			pieces[active_piece].add_moves_to_all_move_bitboard(board)
			active_black_pieces -= active_piece

# Create a bitboard of moves that can be used to defend the king.
# Then, pass the list to the defend_move() function, which will bitwise AND that bitboard with the piece's own bitboard.
def calculate_check_moves(active_pieces, king):
	#logger.log('calculate_check_moves')

	defence_moves = 0
	number_of_checkers = len(board.checker_positions)

	# If there is one piece checking the king, then friendly pieces may save the king
	# If there is more than one piece checking the king, then only the king may save himself.
	if number_of_checkers == 1:
		# If the single checking piece is a pawn or a king, then the checked side may capture the checking piece
		if board.checker_types[0] in [4, 5]:
			defence_moves += 1 << (board.checker_positions[0][0] * 8 + board.checker_positions[0][1])

		# If the single checking piece is a bishop, rook, or queen, then the checked side may either capture the checking piece
		# or interpose a piece between the checking piece and the king.
		else:
			checker_position = 1 << (board.checker_positions[0][0] * 8 + board.checker_positions[0][1])
			king_position = 1 << (pieces[king].x * 8 + pieces[king].y)
			intervening_squares = 0

			if king_position + checker_position in board.intervening_squares_bitboards:
				intervening_squares = board.intervening_squares_bitboards[king_position + checker_position]

			defence_moves += checker_position
			defence_moves += intervening_squares

	# Use the defense moves array to decide how to defend the king
	defend_king(defence_moves, king)

	# If the king is being checked by a ray piece, there is an additional condition added to his moves:
	# He may not move away from a checking ray piece on the ray that he is being checked with.
	moves_to_remove = 0
	king_x = pieces[king].x
	king_y = pieces[king].y

	# Loop, for there may be more than 1 checker.
	for i in range(number_of_checkers):
		# The checker_types array doesn't tie the position to the checker type.
		checker_x = board.checker_positions[i][0]
		checker_y = board.checker_positions[i][1]
		checker_index = squares[checker_x][checker_y].occupied_by
		checker_type = pieces[checker_index].type

		if checker_type in [1, 2, 3]:
			vector_x = get_vector(checker_x, king_x)
			vector_y = get_vector(checker_y, king_y)

			potential_move_to_remove = 1 << ((king_x + vector_x) * 8 + (king_y + vector_y))

			if board.king_move_bitboards[king_x][king_y] & potential_move_to_remove > 0:
				moves_to_remove += potential_move_to_remove

	pieces[king].moves = pieces[king].moves - (pieces[king].moves & moves_to_remove)

def get_vector(origin, destination):
	#logger.log('get_vector')

	if origin - destination > 0:
		return -1
	elif origin - destination == 0:
		return 0
	elif origin - destination < 0:
		return 1

def defend_king (defence_moves, king):
	#logger.log('defend_king')

	if pieces[king].white:
		defenders = board.active_white_pieces - 1<<30
	else:
		defenders = board.active_black_pieces - 1<<31

	while defenders > 0:
		defender = defenders & -defenders
		pieces[defender].moves = pieces[defender].moves & defence_moves
		defenders -= defender

def reset_squares(position):
	for x in range(8):
		for y in range(8):
			squares[x][y].occupied_by = position[x][y]

def check_for_en_passant():
	if board.last_move_piece_type == 5:
		if abs(board.last_move_origin_y - board.last_move_destination_y) == 2:
			if board.white_to_move:
				if board.last_move_origin_x > 0 and squares[board.last_move_origin_x - 1][board.last_move_destination_y].occupied_by in [1<<0,1<<1,1<<2,1<<3,1<<4,1<<5,1<<6,1<<7]:
					en_passant_attacker = squares[board.last_move_origin_x - 1][board.last_move_destination_y].occupied_by
					pieces[en_passant_attacker].moves += 1 << (board.last_move_origin_x * 8 + 5)
					board.en_passant = True
					board.en_passant_pieces.append(en_passant_attacker)
					board.en_passant_victim = squares[board.last_move_destination_x][board.last_move_destination_y].occupied_by

				if board.last_move_origin_x < 7 and squares[board.last_move_origin_x + 1][board.last_move_destination_y].occupied_by in [1<<0,1<<1,1<<2,1<<3,1<<4,1<<5,1<<6,1<<7]:
					en_passant_attacker = squares[board.last_move_origin_x + 1][board.last_move_destination_y].occupied_by
					pieces[en_passant_attacker].moves += 1 << (board.last_move_origin_x * 8 + 5)
					board.en_passant = True
					board.en_passant_pieces.append(en_passant_attacker)
					board.en_passant_victim = squares[board.last_move_destination_x][board.last_move_destination_y].occupied_by
			else:
				if board.last_move_origin_x > 0 and squares[board.last_move_origin_x - 1][board.last_move_destination_y].occupied_by in [1<<8,1<<9,1<<10,1<<11,1<<12,1<<13,1<<14,1<<15]:
					en_passant_attacker = squares[board.last_move_origin_x - 1][board.last_move_destination_y].occupied_by
					pieces[en_passant_attacker].moves += 1 << (board.last_move_origin_x * 8 + 2)
					board.en_passant = True
					board.en_passant_pieces.append(en_passant_attacker)
					board.en_passant_victim = squares[board.last_move_destination_x][board.last_move_destination_y].occupied_by

				if board.last_move_origin_x < 7 and squares[board.last_move_origin_x + 1][board.last_move_destination_y].occupied_by in [1<<8,1<<9,1<<10,1<<11,1<<12,1<<13,1<<14,1<<15]:
					en_passant_attacker = squares[board.last_move_origin_x + 1][board.last_move_destination_y].occupied_by
					pieces[en_passant_attacker].moves += 1 << (board.last_move_origin_x * 8 + 2) # KEY ERROR 9999
					board.en_passant = True
					board.en_passant_pieces.append(en_passant_attacker)
					board.en_passant_victim = squares[board.last_move_destination_x][board.last_move_destination_y].occupied_by

# ********************* MAIN PROGRAM *********************
# Bind an event handler to the left click event
board_display.bind("<Button-1>", handle_click)
board_display.pack()

#create the pieces
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

# ********************** INITIALIZE THE BOARD ***********************
start_position = board.get_position(squares)
generate_moves(start_position)
board_display.render_position(start_position, square_display)

# *********************** BEGIN *************************************

root.mainloop()