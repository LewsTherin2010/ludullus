from tkinter import *
from board_class import *
from square_class import *
from board_display_class import *
from square_display_class import *

#declare the global objects
global root
print("Initialized root")

global app
print("Initialized app")

global board_display
print("Initialized board_display")

global square_display
print("Initialized square_display")

global board
print("Initialized board")

global squares
print("Initialized squares")

global pieces 
print("Initialized pieces")

# ********************* ADD VALUES TO THE GLOBAL VARIABLES ************************
# Create a root window
root = Tk()
root.title("Chess Board")
root.geometry("820x820")

# Create a frame in the window to hold other widgets
app = Frame(root, height = 1000, width = 1000, bg = "#333")
app.grid()

# Create the board display and the square display
board_display = BoardDisplay(app)
square_display = [[SquareDisplay(x, y, board_display) for y in range(8)] for x in range(8)]

# Create the main data structures for the engine
board = Board()
squares = [[Square(x, y, board) for y in range(8)] for x in range(8)]

# Create the pieces dictionary
piece_indexes = [2**x for x in range(32)]
pieces = {}

for piece_index in piece_indexes:
	pieces[piece_index] = []
