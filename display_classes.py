from tkinter import *

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

	def render_position(self, board, square_display):
		# compare current position to new position and draw the appropriate pieces
		for i in range(64):
			x = i // 8
			y = i % 8
			if self.current_position[i] != board[i]:

				# If the square has been highlighted, return it to its original color before recoloring it.
				if square_display[x][y].color == "#987":
					square_display[x][y].color = "#789"
				elif square_display[x][y].color == "#765":
					square_display[x][y].color = "#567"

				# Display the piece move
				square_display[x][y].color_square()

				if board[i] != 0:
					square_display[x][y].draw_piece(x, y, board[i])

		# Update the display's board position
		self.current_position = board

class SquareDisplay():
	def __init__(self, x, y, board_display):
		self.x_start = board_display.x_start + board_display.square_size * x
		self.y_start = board_display.y_start + board_display.square_size * (7 - y)
		self.x_end = board_display.x_start + board_display.square_size * (x + 1)
		self.y_end = board_display.y_start + board_display.square_size * (8 - y)
		self.x = x
		self.y = y
		self.board_display = board_display

		if x % 2 == y % 2:
			self.color = "#567"
		else:
			self.color = "#789"

		self.color_square()

	def color_square(self):
		self.board_display.create_rectangle(self.x_start, self.y_start, self.x_end, self.y_end, outline = "#666", fill = self.color)

	# object_definition: 2D list that contains a scale and 1 or more shapes that make an object, [[scale], [x1, y1, x2, y2, ... xn, yn], [x1, y1, x2, y2, ... nx, yn]]
	# This function will rotate any received object 180 degrees around an implied origin
	def rotate_object_180(self, object_definition):
		
		length = len(object_definition)
		new_object_definition = [[] for i in range(length)]
		new_object_definition[0] = object_definition[0]

		counter = 1
		for shape in object_definition[1:]:
			new_shape_definition = []
			for coordinate in shape:
				new_shape_definition.append(new_object_definition[0][0] - coordinate)
			new_object_definition[counter] = new_shape_definition
			counter += 1

		return new_object_definition

	#this changes proportional coordinates to actual coordinates
	def get_actual_coords(self, x, y, denom, nums, points): 
		coords = [[] for i in range(points * 2)]
		i = 1

		while i <= points:
			coords[2 * i - 2] = self.x_start + (nums[2 * i - 2] / denom) * self.board_display.square_size
			coords[2 * i - 1] = self.y_start + (nums[2 * i - 1] / denom) * self.board_display.square_size
			i += 1

		return coords

	def draw_piece(self, x, y, character):
		if character == 'p':
			self.draw_pawn(x, y, False)
		elif character == 'P':
			self.draw_pawn(x, y, True)
		elif character == 'n':
			self.draw_knight(x, y, False)
		elif character == 'N':
			self.draw_knight(x, y, True)
		elif character == 'b':
			self.draw_bishop(x, y, False)
		elif character == 'B':
			self.draw_bishop(x, y, True)
		elif character == 'r':
			self.draw_rook(x, y, False)
		elif character == 'R':
			self.draw_rook(x, y, True)
		elif character == 'q':
			self.draw_queen(x, y, False)
		elif character == 'Q':
			self.draw_queen(x, y, True)
		elif character == 'k':
			self.draw_king(x, y, False)
		elif character == 'K':
			self.draw_king(x, y, True)

	def draw_pawn(self, x, y, white):
		# Set the background color, and the piece color
		bg_color = self.color

		if white:
			piece_color = '#bbb'
		else:
			piece_color = '#444'

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]
		shields = [[4000.0], [500.0, 1125.0, 3500.0, 1125.0, 3500.0, 1375.0, 500.0, 1375.0]]
		pikes = [[4000.0]
		, [250, 250, 2500, 2750, 3000, 3500, 3000, 3125, 3500, 3500, 3125, 3000, 3500, 3000, 2750, 2500]
		, [3750, 250, 1250, 2500, 500, 3000, 875, 3000, 500, 3500, 1000, 3125, 1000, 3500, 1500, 2750]
		]
		
		pommels = [[4000.0]
		, [500, 2500, 1500, 2500, 1500, 3500, 1250, 2750]
		, [2500, 2500, 3500, 2500, 2750, 2750, 2500, 3500]
		]

		# rotate if the piece is black
		if not white:
			shields = self.rotate_object_180(shields)
			pikes = self.rotate_object_180(pikes)
			pommels = self.rotate_object_180(pommels)

		# convert proportions to coordinates
		shield = self.get_actual_coords(x, y, shields[0][0], shields[1], 4)
		pike1 = self.get_actual_coords(x, y, pikes[0][0], pikes[1], 8)
		pike2 = self.get_actual_coords(x, y, pikes[0][0], pikes[2], 8)
		pommel1 = self.get_actual_coords(x, y, pommels[0][0], pommels[1], 4)
		pommel2 = self.get_actual_coords(x, y, pommels[0][0], pommels[2], 4)		

		#draw the actual shapes
		self.board_display.create_polygon(shield[0], shield[1], shield[2], shield[3], shield[4], shield[5], shield[6], shield[7], outline = piece_color, fill = bg_color)
		self.board_display.create_polygon(pike1[0], pike1[1], pike1[2], pike1[3], pike1[4], pike1[5], pike1[6], pike1[7], pike1[8], pike1[9], pike1[10], pike1[11], pike1[12], pike1[13], pike1[14], pike1[15], outline = piece_color, fill = piece_color)
		self.board_display.create_polygon(pike2[0], pike2[1], pike2[2], pike2[3], pike2[4], pike2[5], pike2[6], pike2[7], pike2[8], pike2[9], pike2[10], pike2[11], pike2[12], pike2[13], pike2[14], pike2[15], outline = piece_color, fill = piece_color)
		self.board_display.create_polygon(pommel1[0], pommel1[1], pommel1[2], pommel1[3], pommel1[4], pommel1[5], pommel1[6], pommel1[7], outline = piece_color, fill = bg_color)
		self.board_display.create_polygon(pommel2[0], pommel2[1], pommel2[2], pommel2[3], pommel2[4], pommel2[5], pommel2[6], pommel2[7], outline = piece_color, fill = bg_color)

	def draw_knight(self, x, y, white):
		bg_color = self.color

		if white:
			piece_color = '#ccc'
		else:
			piece_color = '#333'

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]
		polygons = [[4000.0]
		, [500.0, 1200.0, 2500.0, 3200.0, 3500.0, 2200.0, 2500.0, 2950.0]
		, [500.0, 2200.0, 1500.0, 1200.0, 3500.0, 3200.0, 1500.0, 1450.0]
		, [500.0, 2200.0, 1500.0, 3200.0, 3500.0, 1200.0, 1500.0, 2950.0]
		, [500.0, 3200.0, 2500.0, 1200.0, 3500.0, 2200.0, 2500.0, 1450.0]
		, [2000.0, 200.0, 1000.0, 1200.0, 3000.0, 3200.0, 1250.0, 1200.0]
		, [2000.0, 200.0, 3000.0, 1200.0, 1000.0, 3200.0, 2750.0, 1200.0]
		, [500.0, 2700.0, 1000.0, 3700.0, 2000.0, 3200.0, 1000.0, 3575.0]
		, [2000.0, 3200.0, 3000.0, 3700.0, 3500.0, 2700.0, 3000.0, 3575.0]
		] 

		if not white:
			polygons = self.rotate_object_180(polygons)

		# convert proportions to coordinates
		counter = 1
		for polygon in polygons[1:]:
			polygons[counter] = self.get_actual_coords(x, y, polygons[0][0], polygon, 4)
			counter += 1

		#draw the actual shapes
		counter = 1
		for polygon in polygons[1:]:
			if counter > 4:
				fill_color = bg_color
			else: 
				fill_color = piece_color

			self.board_display.create_polygon(polygon[0], polygon[1], polygon[2], polygon[3], polygon[4], polygon[5], polygon[6], polygon[7], outline = piece_color, fill = fill_color)

			counter += 1

	def draw_rook(self, x, y, white):

		if white:
			piece_color = '#ddd'
		else:
			piece_color = '#222'

		bg_color = self.color

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]

		colored_squares = [
			[360.0]
			#top
			, [161.0, 9.0, 199.0, 47.0]
			, [123.0, 47.0, 161.0, 85.0]
			, [199.0, 47.0, 237.0, 85.0]
			, [161.0, 85.0, 199.0, 123.0]

			# left
			, [9.0, 161.0, 47.0, 199.0]
			, [47.0, 123.0, 85.0, 161.0]
			, [47.0, 199.0, 85.0, 237.0]
			, [85.0, 161.0, 123.0, 199.0]
			
			#bottom
			, [161.0, 351.0, 199.0, 313.0]
			, [123.0, 313.0, 161.0, 275.0]
			, [199.0, 313.0, 237.0, 275.0]
			, [161.0, 275., 199.0, 237.0]
			
			#right
			, [351.0, 161.0, 313.0, 199.0]
			, [313.0, 123.0, 275.0, 161.0]
			, [313.0, 199.0, 275.0, 237.0]
			, [275.0, 161.0, 237.0, 199.0]
			
			#center
			, [123.0, 123.0, 161.0, 161.0]
			, [123.0, 199.0, 161.0, 237.0]
			, [199.0, 123.0, 237.0, 161.0]
			, [199.0, 199.0, 237.0, 237.0]
			, [161.0, 161.0, 199.0, 199.0]
			]

		colored_square = [[] for i in range(len(colored_squares) - 1)]
		counter = 0

		# Convert proportions to coordinates
		for square in colored_squares[1:]:
			colored_square[counter] = self.get_actual_coords(x, y, colored_squares[0][0], square, 2)
			counter += 1


		#draw the actual shapes
		for square in colored_square:
			self.board_display.create_rectangle(square[0], square[1], square[2], square[3], outline = bg_color, fill = piece_color)

	def draw_bishop(self, x, y, white):
		if white:
			piece_color = '#ccc'
		else:
			piece_color = '#333'

		bg_color = self.color

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]
		triangles = [[1000], [50.0, 50.0, 500.0, 500.0, 414.0, 586.0], [950.0, 50.0, 500.0, 500.0, 414.0, 414.0]
		, [50.0, 950.0, 500.0, 500.0, 586.0, 586.0], [950.0, 950.0, 500.0, 500.0, 586.0, 414.0]
		, [50.0, 50.0, 500.0, 500.0, 586.0, 414.0], [950.0, 50.0, 500.0, 500.0, 586.0, 586.0]
		, [50.0, 950.0, 500.0, 500.0, 414.0, 414.0], [950.0, 950.0, 500.0, 500.0, 414.0, 586.0]]

		# convert proportions to coordinates
		length = len(triangles) - 1
		triangle = [[] for i in range(length)]
		i = 0

		while i < length:
			triangle[i] = self.get_actual_coords(x, y, triangles[0][0], triangles[i + 1], 3)
			i += 1

		#draw the actual shapes
		self.board_display.create_polygon(triangle[0][0], triangle[0][1], triangle[0][2], triangle[0][3], triangle[0][4], triangle[0][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[1][0], triangle[1][1], triangle[1][2], triangle[1][3], triangle[1][4], triangle[1][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[2][0], triangle[2][1], triangle[2][2], triangle[2][3], triangle[2][4], triangle[2][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[3][0], triangle[3][1], triangle[3][2], triangle[3][3], triangle[3][4], triangle[3][5], outline = bg_color, fill = piece_color)

		self.board_display.create_polygon(triangle[4][0], triangle[4][1], triangle[4][2], triangle[4][3], triangle[4][4], triangle[4][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[5][0], triangle[5][1], triangle[5][2], triangle[5][3], triangle[5][4], triangle[5][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[6][0], triangle[6][1], triangle[6][2], triangle[6][3], triangle[6][4], triangle[6][5], outline = bg_color, fill = piece_color)
		self.board_display.create_polygon(triangle[7][0], triangle[7][1], triangle[7][2], triangle[7][3], triangle[7][4], triangle[7][5], outline = bg_color, fill = piece_color)

	def draw_queen(self, x, y, white):

		if white:
			piece_color = '#eee'
		else:
			piece_color = '#111'

		bg_color = self.color

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]
		polygons = [
		[2000.0]
		, [250.0, 250.0, 500.0, 625.0, 1000.0, 1000.0, 500.0, 563.0]
		, [250.0, 250.0, 563.0, 500.0, 1000.0, 1000.0, 625.0, 500.0]
		, [1000.0, 0.0, 750.0, 500.0, 1000.0, 1000.0, 825.0, 500.0]
		, [1000.0, 0.0, 932.0, 500.0, 1000.0, 1000.0, 1068.0, 500.0]
		, [1000.0, 0.0, 1175.0, 500.0, 1000.0, 1000.0, 1250.0, 500.0]
		, [1750.0, 250.0, 1375.0, 500.0, 1000.0, 1000.0, 1437.0, 500.0]
		, [1750.0, 250.0, 1500.0, 625.0, 1000.0, 1000.0, 1500.0, 563.0]
		, [2000.0, 1000.0, 1500.0, 750.0, 1000.0, 1000.0, 1500.0, 825.0]
		, [2000.0, 1000.0, 1500.0, 932.0, 1000.0, 1000.0, 1500.0, 1068.0]
		, [2000.0, 1000.0, 1500.0, 1175.0, 1000.0, 1000.0, 1500.0, 1250.0]
		, [1750.0, 1750.0, 1500.0, 1375.0, 1000.0, 1000.0, 1500.0, 1437.0]
		, [1750.0, 1750.0, 1437.0, 1500.0, 1000.0, 1000.0, 1375.0, 1500.0]
		, [1000.0, 2000.0, 1250.0, 1500.0, 1000.0, 1000.0, 1175.0, 1500.0]
		, [1000.0, 2000.0, 1068.0, 1500.0, 1000.0, 1000.0, 932.0, 1500.0]
		, [1000.0, 2000.0, 825.0, 1500.0, 1000.0, 1000.0, 750.0, 1500.0]
		, [250.0, 1750.0, 625.0, 1500.0, 1000.0, 1000.0, 563.0, 1500.0]
		, [259.0, 1750.0, 500.0, 1375.0, 1000.0, 1000.0, 500.0, 1437.0]
		, [0.0, 1000.0, 500.0, 1250.0, 1000.0, 1000.0, 500.0, 1175.0]
		, [0.0, 1000.0, 500.0, 1068.0, 1000.0, 1000.0, 500.0, 932.0]
		, [0.0, 1000.0, 500.0, 825.0, 1000.0, 1000.0, 500.0, 750.0]
		]

		# convert proportions to coordinates
		counter = 1
		for polygon in polygons[1:]:
			polygons[counter] = self.get_actual_coords(x, y, polygons[0][0], polygon, 4)
			counter += 1

		#draw the actual shapes
		for polygon in polygons[1:]:
			self.board_display.create_polygon(polygon[0], polygon[1], polygon[2], polygon[3], polygon[4], polygon[5], polygon[6], polygon[7], outline = piece_color, fill = piece_color)

	def draw_king (self, x, y, white):
		bg_color = self.color

		if white:
			piece_color = '#fff'
		else:
			piece_color = '#000'

		# define shapes as proportions [[denominator], [xnum1, ynum1, ... , xnumn, ynumn], [shape2], ..., [shapen]]
		ups_or_downs = [
		[4000.0]
		, [1000.0, 30.0, 937.0, 500.0, 1000.0, 1000.0, 1063.0, 500.0]
		, [2000.0, 30.0, 1937.0, 500.0, 2000.0, 1000.0, 2063.0, 500.0]
		, [3000.0, 30.0, 2937.0, 500.0, 3000.0, 1000.0, 3063.0, 500.0]

		, [30.0, 1000.0, 500.0, 937.0, 1000.0, 1000.0, 500.0, 1063.0]
		, [1000.0, 1000.0, 1500.0, 937.0, 2000.0, 1000.0, 1500.0, 1063.0]
		, [2000.0, 1000.0, 2500.0, 937.0, 3000.0, 1000.0, 2500.0, 1063.0]
		, [3000.0, 1000.0, 3500.0, 937.0, 3970.0, 1000.0, 3500.0, 1063.0]

		, [1000.0, 1000.0, 937.0, 1500.0, 1000.0, 2000.0, 1063.0, 1500.0]
		, [2000.0, 1000.0, 1937.0, 1500.0, 2000.0, 2000.0, 2063.0, 1500.0]
		, [3000.0, 1000.0, 2937.0, 1500.0, 3000.0, 2000.0, 3063.0, 1500.0]

		, [30.0, 2000.0, 500.0, 1937.0, 1000.0, 2000.0, 500.0, 2063.0]
		, [1000.0, 2000.0, 1500.0, 1937.0, 2000.0, 2000.0, 1500.0, 2063.0]
		, [2000.0, 2000.0, 2500.0, 1937.0, 3000.0, 2000.0, 2500.0, 2063.0]
		, [3000.0, 2000.0, 3500.0, 1937.0, 3970.0, 2000.0, 3500.0, 2063.0]

		, [1000.0, 2000.0, 937.0, 2500.0, 1000.0, 3000.0, 1063.0, 2500.0]
		, [2000.0, 2000.0, 1937.0, 2500.0, 2000.0, 3000.0, 2063.0, 2500.0]
		, [3000.0, 2000.0, 2937.0, 2500.0, 3000.0, 3000.0, 3063.0, 2500.0]

		, [30.0, 3000.0, 500.0, 2937.0, 1000.0, 3000.0, 500.0, 3063.0]
		, [1000.0, 3000.0, 1500.0, 2937.0, 2000.0, 3000.0, 1500.0, 3063.0]
		, [2000.0, 3000.0, 2500.0, 2937.0, 3000.0, 3000.0, 2500.0, 3063.0]
		, [3000.0, 3000.0, 3500.0, 2937.0, 3970.0, 3000.0, 3500.0, 3063.0]

		, [1000.0, 3000.0, 937.0, 3500.0, 1000.0, 3970.0, 1063.0, 3500.0]
		, [2000.0, 3000.0, 1937.0, 3500.0, 2000.0, 3970.0, 2063.0, 3500.0]
		, [3000.0, 3000.0, 2937.0, 3500.0, 3000.0, 3970.0, 3063.0, 3500.0]
		]

		diagonals = [
		[4000.0]
		, [30.0, 30.0, 400.0, 500.0, 30.0, 1000.0, 500.0, 600.0, 1000.0, 1000.0, 600.0, 500.0, 1000.0, 30.0, 500.0, 400.0]
		, [1000.0, 30.0, 1400.0, 500.0, 1000.0, 1000.0, 1500.0, 600.0, 2000.0, 1000.0, 1600.0, 500.0, 2000.0, 30.0, 1500.0, 400.0]
		, [2000.0, 30.0, 2400.0, 500.0, 2000.0, 1000.0, 2500.0, 600.0, 3000.0, 1000.0, 2600.0, 500.0, 3000.0, 30.0, 2500.0, 400.0]
		, [3000.0, 30.0, 3400.0, 500.0, 3000.0, 1000.0, 3500.0, 600.0, 3970.0, 1000.0, 3600.0, 500.0, 3970.0, 30.0, 3500.0, 400.0]

		, [30.0, 1000.0, 400.0, 1500.0, 30.0, 2000.0, 500.0, 1600.0, 1000.0, 2000.0, 600.0, 1500.0, 1000.0, 1000.0, 500.0, 1400.0]
		, [1000.0, 1000.0, 1400.0, 1500.0, 1000.0, 2000.0, 1500.0, 1600.0, 2000.0, 2000.0, 1600.0, 1500.0, 2000.0, 1000.0, 1500.0, 1400.0]
		, [2000.0, 1000.0, 2400.0, 1500.0, 2000.0, 2000.0, 2500.0, 1600.0, 3000.0, 2000.0, 2600.0, 1500.0, 3000.0, 1000.0, 2500.0, 1400.0]
		, [3000.0, 1000.0, 3400.0, 1500.0, 3000.0, 2000.0, 3500.0, 1600.0, 3970.0, 2000.0, 3600.0, 1500.0, 3970.0, 1000.0, 3500.0, 1400.0]

		, [30.0, 2000.0, 400.0, 2500.0, 30.0, 3000.0, 500.0, 2600.0, 1000.0, 3000.0, 600.0, 2500.0, 1000.0, 2000.0, 500.0, 2400.0]
		, [1000.0, 2000.0, 1400.0, 2500.0, 1000.0, 3000.0, 1500.0, 2600.0, 2000.0, 3000.0, 1600.0, 2500.0, 2000.0, 2000.0, 1500.0, 2400.0]
		, [2000.0, 2000.0, 2400.0, 2500.0, 2000.0, 3000.0, 2500.0, 2600.0, 3000.0, 3000.0, 2600.0, 2500.0, 3000.0, 2000.0, 2500.0, 2400.0]
		, [3000.0, 2000.0, 3400.0, 2500.0, 3000.0, 3000.0, 3500.0, 2600.0, 3970.0, 3000.0, 3600.0, 2500.0, 3970.0, 2000.0, 3500.0, 2400.0]

		, [30.0, 3000.0, 400.0, 3500.0, 30.0, 3970.0, 500.0, 3600.0, 1000.0, 3970.0, 600.0, 3500.0, 1000.0, 3000.0, 500.0, 3400.0]
		, [1000.0, 3000.0, 1400.0, 3500.0, 1000.0, 3970.0, 1500.0, 3600.0, 2000.0, 3970.0, 1600.0, 3500.0, 2000.0, 3000.0, 1500.0, 3400.0]
		, [2000.0, 3000.0, 2400.0, 3500.0, 2000.0, 3970.0, 2500.0, 3600.0, 3000.0, 3970.0, 2600.0, 3500.0, 3000.0, 3000.0, 2500.0, 3400.0]
		, [3000.0, 3000.0, 3400.0, 3500.0, 3000.0, 3970.0, 3500.0, 3600.0, 3970.0, 3970.0, 3600.0, 3500.0, 3970.0, 3000.0, 3500.0, 3400.0]
		]

		# convert proportions to coordinates
		counter = 1
		for up_or_down in ups_or_downs[1:]:
			ups_or_downs[counter] = self.get_actual_coords(x, y, ups_or_downs[0][0], up_or_down, 4)
			counter += 1

		counter = 1
		for diagonal in diagonals[1:]:
			diagonals[counter] = self.get_actual_coords(x, y, diagonals[0][0], diagonal, 8)
			counter += 1

		#draw the actual shapes
		counter = 1
		for up_or_down in ups_or_downs[1:]:
			if counter == 1 or counter == 3 or counter == 4 or counter == 7 or counter == 9 or counter == 12 or counter == 13 or counter == 16 or counter == 18 or counter == 21 or counter == 22 or counter == 24:
				fill_color = bg_color
			else:
				fill_color = piece_color

			self.board_display.create_polygon(up_or_down[0], up_or_down[1], up_or_down[2], up_or_down[3], up_or_down[4], up_or_down[5], up_or_down[6], up_or_down[7], outline = piece_color, fill = fill_color)
			counter += 1

		counter = 1
		for diagonal in diagonals[1:]:
			if counter == 1 or counter == 4 or counter == 6 or counter == 7 or counter == 10 or counter == 11 or counter == 13 or counter == 16:
				fill_color = piece_color
			else:
				fill_color = bg_color

			self.board_display.create_polygon(
				diagonal[0], diagonal[1], diagonal[2], diagonal[3], diagonal[4], diagonal[5]
				, diagonal[6], diagonal[7], diagonal[8], diagonal[9], diagonal[10], diagonal[11]
				, diagonal[12], diagonal[13], diagonal[14], diagonal[15], outline = piece_color, fill = fill_color)

			counter += 1
