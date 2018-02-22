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


	def diamondCheckBlock(self, blockState, flag, coord):
		flag = ((blockState[coord[0] - 1][coord[1]] == flag)
						and (blockState[coord[0]][coord[1] - 1] == flag)
						and (blockState[coord[0] + 1][coord[1]] == flag)
						and (blockState[coord[0]][coord[1] + 1] == flag))

		return flag

	# boardState is the 2D list
	# blockCoord is a tuple
	def checkWinInBlock(self, boardState, blockCoord, flag):
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

	# Check Board as a whole
	def checkWinOnBoard(self, blockState, flag):
		# Horizontal Line Check
		flag = False
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (boardState[i][j] == flag)
			flag = flag or bFlag

		# Vertical Line Check
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (boardState[j][i] == flag)
			flag = flag or bFlag

		# Diamond Check
		flag = flag or self.diamondCheckBlock(blockState, flag, (1, 1))
		flag = flag or self.diamondCheckBlock(blockState, flag, (1, 2))
		flag = flag or self.diamondCheckBlock(blockState, flag, (2, 1))
		flag = flag or self.diamondCheckBlock(blockState, flag, (2, 2))

		return flag


	def getValidMoves(self, board, oldMove):
		validCells = []
		blockMove = (oldMove[0] / SZ, blockMove[1] / SZ)
		boardState = board.board_status or self.currentBoardStatus
		blockState = board.block_status or self.currentBlockStatus

		# Check if the Block to move into is valid
		if oldMove != (-1, -1) and blockState[blockMove[0]][blockMove[1]] == config["EM"]:
			for i in xrange(4):
				for j in xrange(4):
					if boardState[blockMove[0] * SZ + i][blockMove[1] * SZ + j] == config["EM"]:
						validCells.append((blockMove[0] * SZ + i, blockMove[1] * SZ + j))
		else:
			for i in xrange(16):
				for j in xrange(16):
					if blockState[int(i / 4)][int(j / 4)] == config["EM"] and boardState[i][j] == config["EM"]:
						validCells.append((i, j))

		return validCells

	# Move the piece
	def move(self, board, oldMove, flag):
		# Deep copy the Current Board State
		self.currentBoardStatus = self.clone(board.board_status)
		self.currentBlockStatus = self.clone(board.block_status)
		self.validMoveCells 	= self.getValidMoves(board, oldMove)
		startTime = int(time.time() * 1000)	# Get time in ms
		currentBestProb = -0.1
		currentBestCell = None
		
		while startTime + config.TIME_LIM + config.TIME_DELTA < time.time() * 1000:
			pass
		pass
