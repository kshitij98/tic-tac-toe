import pandas as pd
import time as time
import os as os

config = {
	TIME_LIM: 15
}

'''
	Node will contain information regarding a state of Board.
	Other information like evaluation function, etc.
	We need to figure out way to distinguish between a small
	and a big board.
	This will contain the information just reagarding the Board
	state. 'x' denotes First player and 'o' denotes second player
'''

class Team29:

	'''
	This will return the move to be played
	@board: OBJECT
		board_status: String containing X, - or O for whole Board
		block_status: String containing X, - or O for the Block
	@old_move: (X, Y); initially (-1, -1)
	@flag: Marker X or O
	'''
	def move(self, board, old_move, flag):
		pass
