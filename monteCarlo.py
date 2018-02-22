import sys
import random
import time
import hashlib
import copy

SZ = 4

config = {
	'P1': 		'x',
	'P2': 		'o',
	'EM': 		'-',
	'TIME_LIM': 	16*1000,
	'TIME_DELTA': 500
}

class MonteCarlo:


	def __init__(self):
		self.clone = copy.deepcopy
		self.currentBlockStatus = None
		self.currentBoardStatus = None
		return

	def diamondCheck(self, boardState, blockCoord, flag, coord):
		flag = ((boardState[blockCoord[0] * SZ + coord[0] - 1][blockCoord[0] * SZ + coord[1]] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0]][blockCoord[0] * SZ + coord[1] - 1] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0] + 1][blockCoord[0] * SZ + coord[1]] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0]][blockCoord[0] * SZ + coord[1] + 1] == flag))

		return flag

	# boardState is the 2D list
	# blockCoord is a tuple
	def checkWinBlock(self, boardState, blockCoord, flag):
		# Horizontal Line Check
		flag = False
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (boardState[blockCoord[0] * SZ + i][blockCoord[0] * SZ + j] == flag)
			flag = flag or bFlag

		# Vertical Line Check
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (boardState[blockCoord[0] * SZ + j][blockCoord[0] * SZ + i] == flag)
			flag = flag or bFlag

		# Diamond Check
		flag = flag or self.diamondCheck(boardState, blockCoord, flag, (1, 1))
		flag = flag or self.diamondCheck(boardState, blockCoord, flag, (1, 2))
		flag = flag or self.diamondCheck(boardState, blockCoord, flag, (2, 1))
		flag = flag or self.diamondCheck(boardState, blockCoord, flag, (2, 2))

		return flag

	def getValidMoves(self, board, oldMove):
		pass
		return

	# Move the piece
	def move(self, board, oldMove, flag):
		# Deep copy the Current Board State
		self.currentBoardStatus = self.clone(board.board_status)
		self.currentBlockStatus = self.clone(board.block_status)
		self.validMoveCells = self.getValidMoves(board, oldMove)
		startTime = int(time.time() * 1000)	# Get time in ms
		while startTime + config.TIME_LIM + config.TIME_DELTA < time.time() * 1000:
			pass
		pass
