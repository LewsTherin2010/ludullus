from tkinter import *
from logger_class import *

class BoardDisplay(Canvas):
	def __init__(self, parent):
		# Display variables
		self.x_start = 10
		self.y_start = 10
		self.square_size = 100
		
		self.current_position = [0 for i in range(64)]

		# Interaction variables
		self.selected = 0
		self.highlighted_square = []

		# Move validation variables
		self.white_to_move = True

		Canvas.__init__(self, parent, height = 820, width = 820, bg = '#222')

	def render_position(self, new_position, square_display):
		#logger.log('board_display.render_position')

		# compare current position to new position and draw the appropriate pieces
		for i in range(64):
			x = i // 8
			y = i % 8
			if self.current_position[i] != new_position[i]:

				# If the square has been highlighted, return it to its original color before recoloring it.
				if square_display[x][y].color == "#987":
					square_display[x][y].color = "#789"
				elif square_display[x][y].color == "#765":
					square_display[x][y].color = "#567"

				# Display the piece move
				square_display[x][y].color_square()

				if new_position[i] != 0:
					square_display[x][y].draw_piece(x, y, new_position[i])


		# Update the display's board position
		self.current_position = new_position