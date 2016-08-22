from globals_file import *

class PositionMemento():
	def store_current_position(self, position, board, pieces):
		# Store last-move variables
		self.white_to_move = board.white_to_move
		self.last_move_piece_type = board.last_move_piece_type
		self.last_move_origin_x = board.last_move_origin_x
		self.last_move_origin_y = board.last_move_origin_y
		self.last_move_destination_x = board.last_move_destination_x
		self.last_move_destination_y = board.last_move_destination_y
		self.halfmove_clock = board.halfmove_clock

		# Store castle variables
		self.white_castle_a = pieces[1<<30].castle_a
		self.white_castle_h = pieces[1<<30].castle_h
		self.black_castle_a = pieces[1<<31].castle_a
		self.black_castle_h = pieces[1<<31].castle_h

		# Store piece positions
		self.all_white_positions = board.all_white_positions
		self.all_black_positions = board.all_black_positions

		self.piece_positions = {}
		for piece in board.piece_indexes:
			self.piece_positions[piece] = [pieces[piece].x, pieces[piece].y, pieces[piece].eightx_y]

		# Store active pieces
		self.active_white_pieces = board.active_white_pieces
		self.active_black_pieces = board.active_black_pieces
		self.pieces = pieces

		# Store position
		self.position = position

	def restore_current_position(self, board, pieces):
		# Restore last-move variables
		board.white_to_move = self.white_to_move
		board.last_move_piece_type = self.last_move_piece_type
		board.last_move_origin_x = self.last_move_origin_x
		board.last_move_origin_y = self.last_move_origin_y
		board.last_move_destination_x = self.last_move_destination_x
		board.last_move_destination_y = self.last_move_destination_y
		board.halfmove_clock = self.halfmove_clock

		# Restore castle variables
		pieces[1<<30].castle_a = self.white_castle_a
		pieces[1<<30].castle_h = self.white_castle_h
		pieces[1<<31].castle_a = self.black_castle_a
		pieces[1<<31].castle_h = self.black_castle_h

		# Restore piece positions
		board.all_white_positions = self.all_white_positions
		board.all_black_positions = self.all_black_positions

		for piece in board.piece_indexes:
			pieces[piece].x = self.piece_positions[piece][0]
			pieces[piece].y = self.piece_positions[piece][1]
			pieces[piece].eightx_y = self.piece_positions[piece][2]

		# Restore active pieces
		board.active_white_pieces = self.active_white_pieces
		board.active_black_pieces = self.active_black_pieces

		pieces = self.pieces

		# Return the position
		return self.position
