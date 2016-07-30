		###### BITMASKS ######
		self.a1_h8_bitwise_mask = [7,6,15,5,14,23,4,13,22,31,3,12,21,30,39,2,11,20,29,38,47,1,10,19,28,37,46,55,0,9,18,27,36,45,54,63,8,17,26,35,44,53,62,16,25,34,43,52,61,24,33,42,51,60,32,41,50,59,40,49,58,48,57,56]
		self.a1_h8_bitwise_unmask = [28,21,15,10,6,3,1,0,36,29,22,16,11,7,4,2,43,37,30,23,17,12,8,5,49,44,38,31,24,18,13,9,54,50,45,39,32,25,19,14,58,55,51,46,40,33,26,20,61,59,56,52,47,41,34,27,63,62,60,57,53,48,42,35]

		self.a8_h1_bitwise_mask = [0,1,8,2,9,16,3,10,17,24,4,11,18,25,32,5,12,19,26,33,40,6,13,20,27,34,41,48,7,14,21,28,35,42,49,56,15,22,29,36,43,50,57,23,30,37,44,51,58,31,38,45,52,59,39,46,53,60,47,54,61,55,62,63]
		self.a8_h1_bitwise_unmask = [0,1,3,6,10,15,21,28,2,4,7,11,16,22,29,36,5,8,12,17,23,30,37,43,9,13,18,24,31,38,44,49,14,19,25,32,39,45,50,54,20,26,33,40,46,51,55,58,27,34,41,47,52,56,59,61,35,42,48,53,57,60,62,63]

		# 7 - - 0 - - 1 -
		# - 7 - 0 - 1 - -
		# - - 7 0 1 - - -
		# 6 6 6 X 2 2 2 2 
		# - - 5 4 3 - - -
		# - 5 - 4 - 3 - -
		# 5 - - 4 - - 3 -
		# - - - 4 - - - 3
		self.rays_from_square_bitboards = [[0 for y in range(8)] for x in range(64)]

		self.initialize_rays_from_square_bitboards()

	# Converting these hex values to bits and looking at the bit strings should clarify.
	# Basically, this algorithm exchanges diagonals of equal length.
	def rotate_bitboard_around_a8_h1(self, original_bitboard):
		flipped_bitboard = original_bitboard & 0x102040810204080L
		flipped_bitboard += (original_bitboard >> 9) & 0x1020408102040L
		flipped_bitboard += (original_bitboard << 9) & 0x204081020408000L
		flipped_bitboard += (original_bitboard >> 18) & 0x10204081020L
		flipped_bitboard += (original_bitboard << 18) & 0x408102040800000L
		flipped_bitboard += (original_bitboard >> 27) & 0x102040810L
		flipped_bitboard += (original_bitboard << 27) & 0x810204080000000L
		flipped_bitboard += (original_bitboard >> 36) & 0x1020408
		flipped_bitboard += (original_bitboard << 36) & 0x1020408000000000L
		flipped_bitboard += (original_bitboard >> 45) & 0x10204
		flipped_bitboard += (original_bitboard << 45) & 0x2040800000000000L
		flipped_bitboard += (original_bitboard >> 54) & 0x102
		flipped_bitboard += (original_bitboard << 54) & 0x4080000000000000L
		flipped_bitboard += (original_bitboard >> 63) & 0x1
		flipped_bitboard += (original_bitboard << 63) & 0x8000000000000000L

		return flipped_bitboard

	def reorder_bitboard_by_a1_h8_diagonals(self, original_bitboard):
		reordered_bitboard = 0
		for i in range(64):
			reordered_bitboard += ((original_bitboard >> self.a1_h8_bitwise_mask[i]) & 1) << i
		return reordered_bitboard

	def reorder_bitboard_from_a1_h8_diagonals(self, original_bitboard):
		reordered_bitboard = 0
		for i in range(64):
			reordered_bitboard += ((original_bitboard >> self.a1_h8_bitwise_unmask[i]) & 1) << i
		return reordered_bitboard

	def reorder_bitboard_by_a8_h1_diagonals(self, original_bitboard):
		reordered_bitboard = 0
		for i in range(64):
			reordered_bitboard += ((original_bitboard >> self.a8_h1_bitwise_mask[i]) & 1) << i
		return reordered_bitboard

	def reorder_bitboard_from_a8_h1_diagonals(self, original_bitboard):
		reordered_bitboard = 0
		for i in range(64):
			reordered_bitboard += ((original_bitboard >> self.a8_h1_bitwise_unmask[i]) & 1) << i
		return reordered_bitboard


	# 7 - - 0 - - 1 -
	# - 7 - 0 - 1 - -
	# - - 7 0 1 - - -
	# 6 6 6 X 2 2 2 2 
	# - - 5 4 3 - - -
	# - 5 - 4 - 3 - -
	# 5 - - 4 - - 3 -
	# - - - 4 - - - 3
	def initialize_rays_from_square_bitboards(self):
		for square in range(64):
			for ray in range(8):
				if ray == 0:
					location = square + 1
					while location % 8 > 0:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location += 1
				elif ray == 1:
					location = square + 9
					while location % 8 > 0 and location < 64:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location += 9
				elif ray == 2:
					location = square + 8
					while location < 64:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location += 8
				elif ray == 3:
					location = square + 7
					while location % 8 < 7 and location < 64:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location += 7
				elif ray == 4:
					location = square - 1
					while location % 8 < 7:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location -= 1
				elif ray == 5:
					location = square - 9
					while location % 8 < 7 and location > -1:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location -= 9
				elif ray == 6:
					location = square - 8
					while location > -1:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location -= 8
				elif ray == 7:
					location = square - 7
					while location % 8 > 0 and location > -1:
						self.rays_from_square_bitboards[square][ray] += 1 << location
						location -= 7

	# Converting these hex values to bits and looking at the bit strings should clarify.
	# Basically, this algorithm exchanges diagonals of equal length.
	def rotate_bitboard_around_a1_h8(self, original_bitboard):
		flipped_bitboard = original_bitboard & 0x8040201008040201L
		flipped_bitboard += (original_bitboard << 7) & 0x4020100804020100L
		flipped_bitboard += (original_bitboard >> 7) & 0x80402010080402L
		flipped_bitboard += (original_bitboard << 14) & 0x2010080402010000L
		flipped_bitboard += (original_bitboard >> 14) & 0x804020100804L
		flipped_bitboard += (original_bitboard << 21) & 0x1008040201000000L
		flipped_bitboard += (original_bitboard >> 21) & 0x8040201008L
		flipped_bitboard += (original_bitboard << 28) & 0x804020100000000L
		flipped_bitboard += (original_bitboard >> 28) & 0x1080000010L
		flipped_bitboard += (original_bitboard << 35) & 0x402010000000000L
		flipped_bitboard += (original_bitboard >> 35) & 0x804020
		flipped_bitboard += (original_bitboard << 42) & 0x201000000000000L
		flipped_bitboard += (original_bitboard >> 42) & 0x8040
		flipped_bitboard += (original_bitboard << 49) & 0x100000000000000L
		flipped_bitboard += (original_bitboard >> 49) & 0x80

		return flipped_bitboard






	def calculate_a1_h8_diagonal_moves_old(self):
		# Retrieve precalculated diagonal variables from the square the piece is in.
		bitshift_amount = squares[self.x][self.y].a1_h8_bitshift_amount

		ray = squares[self.x][self.y].a1_h8_ray

		position = squares[self.x][self.y].a1_h8_position

		# Shift the board to the right the appropriate amount, in order to access the 
		shifted_board = board.all_piece_positions_reordered_by_a1_h8 >> bitshift_amount

		# Calculate the occupancy
		occupancy = shifted_board & ray

		# Potential moves
		potential_moves = board.file_bitboards[position][occupancy] & ray

		# Unshift the bits, and reorder the moves to the standard square order
		unshifted_board = potential_moves << bitshift_amount

		potential_moves = board.reorder_bitboard_from_a1_h8_diagonals(unshifted_board)

		# Calculate moves and defended pieces
		if self.white:
			self.moves += potential_moves & ~board.all_white_positions
			board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)
		else:
			self.moves += potential_moves & ~board.all_black_positions
			board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)

	def calculate_a8_h1_diagonal_moves_old(self):
		# Retrieve precalculated diagonal variables from the square the piece is in.
		bitshift_amount = squares[self.x][self.y].a8_h1_bitshift_amount
		ray = squares[self.x][self.y].a8_h1_ray
		position = squares[self.x][self.y].a8_h1_position

		# Shift the board to the right the appropriate amount, in order to access the 
		shifted_board = board.all_piece_positions_reordered_by_a8_h1 >> bitshift_amount

		# Calculate the occupancy
		occupancy = shifted_board & ray

		# Potential moves
		potential_moves = board.file_bitboards[position][occupancy] & ray

		# Unshift the bits, and reorder the moves to the standard square order
		unshifted_board = potential_moves << bitshift_amount
		potential_moves = board.reorder_bitboard_from_a8_h1_diagonals(unshifted_board)

		# Calculate moves and defended pieces
		if self.white:
			self.moves += potential_moves & ~board.all_white_positions
			board.all_defended_white_pieces = board.all_defended_white_pieces | (potential_moves & board.all_white_positions)
		else:
			self.moves += potential_moves & ~board.all_black_positions
			board.all_defended_black_pieces = board.all_defended_black_pieces | (potential_moves & board.all_black_positions)