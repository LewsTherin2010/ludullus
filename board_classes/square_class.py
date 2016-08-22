from globals_file import *
import board_class

class Square():
	def __init__(self, i, board):
		self.x = i // 8
		self.y = i % 8
		self.board = board
		self.bitwise_position = i
		self.occupied_by = 0

		#Diagonal bitshift variables
		self.a1_h8_bitshift_amount = 0
		self.a1_h8_length = 0
		self.a1_h8_position = 0

		self.a8_h1_bitshift_amount = 0
		self.a8_h1_length = 0
		self.a8_h1_position = 0

		#Initialize some variables.
		self.calculate_a1_h8_diagonal_bitboard_variables()
		self.calculate_a8_h1_diagonal_bitboard_variables()

	def calculate_a1_h8_diagonal_bitboard_variables(self):
		if self.x - self.y == -7:
			self.a1_h8_bitshift_amount = 7
			self.a1_h8_length = 0b1
			self.a1_h8_position = self.x
		elif self.x - self.y == -6:
			self.a1_h8_bitshift_amount = 6
			self.a1_h8_length = 0b1000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == -5:
			self.a1_h8_bitshift_amount = 5
			self.a1_h8_length = 0b1000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == -4:
			self.a1_h8_bitshift_amount = 4
			self.a1_h8_length = 0b1000000001000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == -3:
			self.a1_h8_bitshift_amount = 3
			self.a1_h8_length = 0b1000000001000000001000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == -2:
			self.a1_h8_bitshift_amount = 2
			self.a1_h8_length = 0b1000000001000000001000000001000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == -1:
			self.a1_h8_bitshift_amount = 1
			self.a1_h8_length = 0b1000000001000000001000000001000000001000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == 0:
			self.a1_h8_bitshift_amount = 0
			self.a1_h8_length = 0b1000000001000000001000000001000000001000000001000000001000000001
			self.a1_h8_position = self.x
		elif self.x - self.y == 1:
			self.a1_h8_bitshift_amount = 8
			self.a1_h8_length = 0b1000000001000000001000000001000000001000000001000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 2:
			self.a1_h8_bitshift_amount = 16
			self.a1_h8_length = 0b1000000001000000001000000001000000001000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 3:
			self.a1_h8_bitshift_amount = 24
			self.a1_h8_length = 0b1000000001000000001000000001000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 4:
			self.a1_h8_bitshift_amount = 32
			self.a1_h8_length = 0b1000000001000000001000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 5:
			self.a1_h8_bitshift_amount = 40
			self.a1_h8_length = 0b1000000001000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 6:
			self.a1_h8_bitshift_amount = 48
			self.a1_h8_length = 0b1000000001
			self.a1_h8_position = self.y
		elif self.x - self.y == 7:
			self.a1_h8_bitshift_amount = 56
			self.a1_h8_length = 0b1
			self.a1_h8_position = self.y

	def calculate_a8_h1_diagonal_bitboard_variables(self):
		if self.x + self.y == 0:
			self.a8_h1_bitshift_amount = -7
			self.a8_h1_length = 0b10000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 1:
			self.a8_h1_bitshift_amount = -6
			self.a8_h1_length = 0b100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 2:
			self.a8_h1_bitshift_amount = -5
			self.a8_h1_length = 0b1000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 3:
			self.a8_h1_bitshift_amount = -4
			self.a8_h1_length = 0b10000001000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 4:
			self.a8_h1_bitshift_amount = -3
			self.a8_h1_length = 0b100000010000001000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 5:
			self.a8_h1_bitshift_amount = -2
			self.a8_h1_length = 0b1000000100000010000001000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 6:
			self.a8_h1_bitshift_amount = -1
			self.a8_h1_length = 0b10000001000000100000010000001000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 7:
			self.a8_h1_bitshift_amount = 0
			self.a8_h1_length = 0b100000010000001000000100000010000001000000100000010000000
			self.a8_h1_position = self.x
		elif self.x + self.y == 8:
			self.a8_h1_bitshift_amount = 8
			self.a8_h1_length = 0b10000001000000100000010000001000000100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 9:
			self.a8_h1_bitshift_amount = 16
			self.a8_h1_length = 0b1000000100000010000001000000100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 10:
			self.a8_h1_bitshift_amount = 24
			self.a8_h1_length = 0b100000010000001000000100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 11:
			self.a8_h1_bitshift_amount = 32
			self.a8_h1_length = 0b10000001000000100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 12:
			self.a8_h1_bitshift_amount = 40
			self.a8_h1_length = 0b1000000100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 13:
			self.a8_h1_bitshift_amount = 48
			self.a8_h1_length = 0b100000010000000
			self.a8_h1_position = 7 - self.y
		elif self.x + self.y == 14:
			self.a8_h1_bitshift_amount = 56
			self.a8_h1_length = 0b10000000
			self.a8_h1_position = 7 - self.y