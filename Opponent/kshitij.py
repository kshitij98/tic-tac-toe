import sys
import random
import time
import hashlib
import copy
import os
import traceback

SZ = 4
TUNIT = 1000000
config = {
	'P1':	 		'x',
	'P2': 			'o',
	'EM': 			'-',
	'TIME_LIM': 	16 * TUNIT,
	'TIME_DELTA': 	TUNIT / 2,
	'POINTS':		[[6, 4, 4, 6],
					 [4, 3, 3, 4],
					 [4, 3, 3, 4],
					 [6, 4, 4, 6]]
}

class Kshitij:

	def __init__(self):
		# Set BONUS_MOVE = false
		self.player = 'P1'
		self.isBonusMove = False
		self.pivot = [None] * 2
		self.board = [[None for i in range(16)] for j in range(16)]
		self.block = [[None for i in range(4)] for j in range(4)]
		return

	def updateBoardState(self, boardState, blockState, oldMove):
		for i in xrange(4):
			for j in xrange(4):
				self.block[i][j] = blockState[i][j]

		movesMade = 0
		for i in xrange(16):
			for j in xrange(16):
				self.board[i][j] = boardState[i][j]
				if boardState[i][j] != config['EM']:
					movesMade += 1 

		# If FIRST_MOVE: (Set pivot & Copy board?)
		if movesMade < 2:
			self.pivot[0] = 1 + (oldMove[0] < 3)
			self.pivot[1] = 1 + (oldMove[1] < 3)

	def isValuable(self, currBlock):
		if currBlock[0] == self.pivot[0] or currBlock[1] == self.pivot[1]:
			return True
		return False

	def isOpenMove(self, currBlock):
		if self.block[currBlock[0]][currBlock[1]] != config['EM']:
			return True
		return False

	def assignPoints(self, currBlock, points):
		if self.isValuable(currBlock):
			if self.isBonusMove:
				pass
			else:
				pass

		else:
			pass

		return points

	def findBestMove(self, points, offset):
		tableSize = len(points)
		best = (0, 0)
		for i in xrange(tableSize):
			for j in xrange(tableSize):
				if points[i][j] > best:
					best = (i, j)

		return (offset[0] + best[0], offset[1] + best[1])


	# Move the piece
	def move(self, board, oldMove, flag):
		startTime = int(time.time() * TUNIT)	# Get time in ms

		if flag == config['P1']:
			self.player = 'P1'
		else:
			self.player = 'P2'

		self.updateBoardState(board.board_status, board.block_status, oldMove)

		currBlock = (oldMove[0] % SZ, oldMove[1] % SZ)

		pointsTable = None
		if self.isOpenMove(currBlock):
			currBlock = (0, 0)
			pointsTable = [[None for i in range(16)] for j in range(16)]
			pointsBlock = [[None for i in range(4)] for j in range(4)]
			for i in xrange(4):
				for j in xrange(4):
					self.assignPoints((i, j), pointsBlock)
					for ii in xrange(4):
						for jj in xrange(4):
							pointsTable[i*4 + ii][j*4 + jj] = pointsBlock[ii][jj]
		else:
			pointsTable = [[None for i in range(4)] for j in range(4)]
			self.assignPoints(currBlock, pointsTable)

		foundMove = self.findBestMove(pointsTable, (currBlock[0] * 4, currBlock[1] * 4))

		print(foundMove)
