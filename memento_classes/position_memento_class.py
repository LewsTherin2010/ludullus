from globals_file import *

class PositionMemento():
	def store_current_position(self, position, board, pieces):
		self.store_last_move_variables(board)
		self.store_castle_variables(pieces)
		self.store_piece_positions(pieces, board)
		self.store_active_pieces(board)

		self.position = position

	def restore_current_position(self, board, pieces):
		self.restore_last_move_variables(board)
		self.restore_castle_variables(pieces)
		self.restore_piece_positions(pieces, board)
		self.restore_active_pieces(board)

		return self.position

	def store_last_move_variables(self, board):
		self.white_to_move = board.white_to_move
		self.last_move_piece_type = board.last_move_piece_type
		self.last_move_origin_x = board.last_move_origin_x
		self.last_move_origin_y = board.last_move_origin_y
		self.last_move_destination_x = board.last_move_destination_x
		self.last_move_destination_y = board.last_move_destination_y

	def store_castle_variables(self, pieces):
		self.white_castle_a = pieces[1<<30].castle_a
		self.white_castle_h = pieces[1<<30].castle_h
		self.black_castle_a = pieces[1<<31].castle_a
		self.black_castle_h = pieces[1<<31].castle_h

	def store_active_pieces(self, board):
		self.active_white_pieces = board.active_white_pieces
		self.active_black_pieces = board.active_black_pieces
		self.pieces = pieces

	def store_piece_positions(self, pieces, board):
		self.all_white_positions = board.all_white_positions
		self.all_black_positions = board.all_black_positions

		self.piece_positions = {}
		for piece in board.piece_indexes:
			self.piece_positions[piece] = [pieces[piece].x, pieces[piece].y]

	def restore_last_move_variables(self, board):
		board.white_to_move = self.white_to_move
		board.last_move_piece_type = self.last_move_piece_type
		board.last_move_origin_x = self.last_move_origin_x
		board.last_move_origin_y = self.last_move_origin_y
		board.last_move_destination_x = self.last_move_destination_x
		board.last_move_destination_y = self.last_move_destination_y

	def restore_castle_variables(self, pieces):
		pieces[1<<30].castle_a = self.white_castle_a
		pieces[1<<30].castle_h = self.white_castle_h
		pieces[1<<31].castle_a = self.black_castle_a
		pieces[1<<31].castle_h = self.black_castle_h

	def restore_piece_positions(self, pieces, board):
		board.all_white_positions = self.all_white_positions
		board.all_black_positions = self.all_black_positions

		for piece in board.piece_indexes:
			pieces[piece].x = self.piece_positions[piece][0]
			pieces[piece].y = self.piece_positions[piece][1]
			
	def restore_active_pieces(self, board):
		board.active_white_pieces = self.active_white_pieces
		board.active_black_pieces = self.active_black_pieces

		pieces = self.pieces
