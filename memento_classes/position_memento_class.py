from globals_file import *

class PositionMemento():
	def store_current_position(self, position):
		# Store last-move variables
		self.white_to_move = board.white_to_move
		self.last_move_piece_type = board.last_move_piece_type
		self.last_move_origin_eightx_y = board.last_move_origin_eightx_y
		self.last_move_destination_eightx_y = board.last_move_destination_eightx_y
		self.halfmove_clock = board.halfmove_clock

		# Store castle variables
		self.castles = board.castles

		# Store piece positions
		self.all_white_positions = board.all_white_positions
		self.all_black_positions = board.all_black_positions

		self.piece_positions = {}
		for piece in board.piece_indexes:
			self.piece_positions[piece] = pieces[piece].eightx_y

		# Store active pieces
		self.active_white_pieces = board.active_white_pieces
		self.active_black_pieces = board.active_black_pieces

		# Store position
		self.position = position

	def restore_current_position(self):
		# Restore last-move variables
		board.white_to_move = self.white_to_move
		board.last_move_piece_type = self.last_move_piece_type
		board.last_move_origin_eightx_y = self.last_move_origin_eightx_y
		board.last_move_destination_eightx_y = self.last_move_destination_eightx_y
		board.halfmove_clock = self.halfmove_clock

		# Restore castle variables
		board.castles = self.castles

		# Restore piece positions
		board.all_white_positions = self.all_white_positions
		board.all_black_positions = self.all_black_positions

		for piece in board.piece_indexes:
			pieces[piece].eightx_y = self.piece_positions[piece]

		# Restore active pieces
		board.active_white_pieces = self.active_white_pieces
		board.active_black_pieces = self.active_black_pieces

		# Return the position
		return self.position
