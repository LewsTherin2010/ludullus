from logger_class import *

class Board():
	def __init__(self):
		self.nodes = 0

		# Piece variables
		self.piece_type_definitions = {0:'King', 1:'Queen', 2:'Rook', 3:'Bishop', 4:'Knight', 5:'Pawn'}
		self.piece_indexes = [1<<x for x in range(32)]
		self.piece_values = {1<<0:1, 1<<1:1, 1<<2:1, 1<<3:1, 1<<4:1, 1<<5:1, 1<<6:1, 1<<7:1, 1<<8:-1, 1<<9:-1, 1<<10:-1, 1<<11:-1, 1<<12:-1, 1<<13:-1, 1<<14:-1, 1<<15:-1, 1<<16:5, 1<<17:5, 1<<18:-5, 1<<19:-5, 1<<20:3, 1<<21:3, 1<<22:-3, 1<<23:-3, 1<<24:3, 1<<25:3, 1<<26:-3, 1<<27:-3, 1<<28: 9, 1<<29:-9, 1<<30:10000, 1<<31:-10000}
		
		self.all_white_pieces = 0b01010011001100110000000011111111
		self.all_black_pieces = 0b10101100110011001111111100000000

		self.white_pinners = 0b00010011000000110000000000000000 # Queen, rooks, and bishops
		self.black_pinners = 0b00101100000011000000000000000000 # Queen, rooks, and bishops

		self.active_white_pieces = 0b01010011001100110000000011111111
		self.active_black_pieces = 0b10101100110011001111111100000000
								   
		self.extra_white_indexes = [1<<32, 1<<33, 1<<34, 1<<35, 1<<36, 1<<37, 1<<38, 1<<39]
		self.extra_black_indexes = [1<<40, 1<<41, 1<<42, 1<<43, 1<<44, 1<<45, 1<<46, 1<<47]

		# En passant variables
		self.en_passant_pieces = []
		self.en_passant_victim = 0

		# Move variables
		self.white_to_move = True

		self.last_move_piece_type = -1
		self.last_move_origin_eightx_y = -1
		self.last_move_destination_eightx_y = -1

		#Castles
		# The bits here are as follow:
		# 1000 : White castle kingside
		# 0100 : White castle queenside
		# 0010 : Black castle kingside
		# 0001 : Black castle queenside
		self.castles = 0b1111

		# Check variables
		self.checker_types = []
		self.checker_positions = []

		# pin arrays
		self.pinned_white_pieces = []
		self.pinned_black_pieces = []

		# FEN variables - These are to enable load from Forsyth-Edwards notation
		self.en_passant_target_square = ''
		self.halfmove_clock = 0
		self.fullmove_number = 1

		###### BOARD STATE BITBOARDS ######
		self.all_white_moves = 0
		self.all_black_moves = 0

		self.all_defended_white_pieces = 0
		self.all_defended_black_pieces = 0

		self.all_white_positions = 0
		self.all_black_positions = 0

		self.all_piece_positions = 0

		self.white_removed_pin_moves = 0
		self.black_removed_pin_moves = 0

		self.unrealized_white_pawn_attacks = 0
		self.unrealized_black_pawn_attacks = 0

		self.third_rank_shifted_to_fourth = 0 # For use in calculating white pawns' first moves
		self.sixth_rank_shifted_to_fifth = 0 # For use in calculating black pawns' first moves


		# Run init functions


	def get_position(self, squares):
		#logger.log('board.get_position')

		position = [0 for i in range(64)]

		for i in range(64):
			position[i] = squares[i].occupied_by

		return position

	def evaluate_position(self, position):
		#logger.log('board.evaluate_position')

		position_value = 0

		for i in range(64):
			if position[i] != 0:
				position_value += self.piece_values[position[i]]

		self.nodes += 1

		return position_value

	def shift_third_rank_to_fourth(self, original_bitboard):
		return (original_bitboard & 0x404040404040404) << 1

	def shift_sixth_rank_to_fifth(self, original_bitboard):
		return (original_bitboard & 0x2020202020202020) >> 1

