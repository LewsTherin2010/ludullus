from tkinter import *
from logger_class import *

class BoardDisplay(Canvas):
	def __init__(self, parent):
		# Display variables
		self.x_start = 10
		self.y_start = 10
		self.square_size = 100
		
		self.current_position = [[9999 for x in range (0, 8)] for y in range (0, 8)]

		# Interaction variables
		self.selected = 9999
		self.highlighted_square = []

		# Move validation variables
		self.white_to_move = True

		Canvas.__init__(self, parent, height = 820, width = 820, bg = '#222')

	def render_position(self, new_position, square_display):
		#logger.log('board_display.render_position')

		# compare current position to new position and draw the appropriate pieces
		for x in range (0, 8):
			for y in range (0, 8):
				if self.current_position[x][y] != new_position[x][y]:

					# If the square has been highlighted, return it to its original color before recoloring it.
					if square_display[x][y].color == "#987":
						square_display[x][y].color = "#789"
					elif square_display[x][y].color == "#765":
						square_display[x][y].color = "#567"

					# Display the piece move
					square_display[x][y].color_square()

					if new_position[x][y] != 9999:
						square_display[x][y].draw_piece(x, y, new_position[x][y])


		# Update the display's board position
		self.current_position = new_position