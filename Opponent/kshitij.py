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
					 [6, 4, 4, 6]],
	'INF': 999999999999999999,
}

class Kshitij:

	def __init__(self):
		# Set BONUS_MOVE = false
		self.player = 'P1'
		self.opponent = 'P2'
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


	# TODO: Assign exponential probabilities?
	def getWinProb(self, filled):
		if filled < 0:
			return 0
		return 2 ^ filled


				# 0, 0
	# 1, 0					1, 1
				# 0, 1
	def getDiamondChance(self, offset, player):
		chance = 0
		for i in xrange(2):
			for j in xrange(2):
				x, y = offset[0] + 1 - i + 2*j*i, offset[1] + i + (1-i)*j*2
				if self.board[x][y] == config[player]:
					chance += 1
				elif self.board[x][y] != config['EM']:
					chance = -config['INF']
		return chance


	def getWinningChance(self, currBlock, player):
		x, y = currBlock[0] * 4, currBlock[1] * 4

		if self.block[currBlock[0]][currBlock[1]] != config['EM']:
			return 5 # TODO: Set constant value, Not infinity

		chance = 0

		for i in xrange(4):
			currChance = 0
			for j in xrange(4):
				if self.board[x + i][y + j] == config[player]:
					currChance += 1
				elif self.board[x + i][y + j] != config['EM']:
					currChance = -config['INF']
			if currChance >= 0:
				# TODO: Can merge with a different function
				chance += self.getWinProb(currChance)

		for i in xrange(4):
			currChance = 0
			for j in xrange(4):
				if self.board[x + j][y + i] == config[player]:
					currChance += 1
				elif self.board[x + i][y + j] != config['EM']:
					currChance = -config['INF']
			if currChance >= 0:
				chance += self.getWinProb(currChance)

		for i in xrange(2):
			for j in xrange(2):
				chance += self.getWinProb(self.getDiamondChance((x + i, y + j), player))

		return chance


	def assignPoints(self, currBlock, points):
		x, y = currBlock[0] * 4, currBlock[1] * 4
		invalidBlock = self.isOpenMove(currBlock)

		winTable = [[0 for i in range(4)] for j in range(4)]
		oppWinTable = [[0 for i in range(4)] for j in range(4)]
		uselessnessTable = [[0 for i in range(4)] for j in range(4)]


		for i in xrange(4):
			for j in xrange(4):
				if self.board[x + i][y + j] != config['EM'] or invalidBlock:
					points[x + i][y + j] = -config['INF']
				else:
					self.board[x + i][y + j] = config[self.player]
					winTable[i][j] = self.getWinningChance(currBlock, self.player)
					oppWinTable[i][j] = self.getWinningChance((i, j), self.opponent)
					# TODO: Update constants
					if self.isValuable((i, j)):
						uselessnessTable[i][j] = 1
					else:
						uselessnessTable[i][j] = 5
						
					self.board[x + i][y + j] = config['EM']

		# print(winTable)
		# print(oppWinTable)
		# print(uselessnessTable)
		# print(points)

		# TODO: Set constants
		c1, c2, c3 = 1, 1, 1
		if self.isValuable(currBlock):
			if self.isBonusMove: # Give lesser wight to winning this block, more to useless transfer
				c1, c2, c3 = 2, 1, 3
			else: # Give high weight to winning this block, lesser to useless transfer
				c1, c2, c3 = 3, 1, 2

		else: # Give higher weight to winning this block, then to blocking, then to useless transfer
			c1, c2, c3 = 6, 5, 3

		for i in xrange(4):
			for j in xrange(4):
				if points[x + i][y + j] != -config['INF']:
					points[x + i][y + j] = c1 * winTable[i][j] - c2 * oppWinTable[i][j] + c3 * uselessnessTable[i][j]

		return points

	def findBestMove(self, points, currBlock):
		best = (0, 0)
		x, y = currBlock[0] * 4, currBlock[1] * 4
		if self.isOpenMove(currBlock):
			for i in xrange(16):
				for j in xrange(16):
					if points[i][j] > points[best[0]][best[1]]:
						best = (i, j)
		else:
			for i in xrange(4):
				for j in xrange(4):
					if points[x + i][y + j] > points[x + best[0]][y + best[1]]:
						best = (i, j)

		return (x + best[0], y + best[1])

	# def solve(self, depth, ):

	# def IDF(self, ):

	# Move the piece
	def move(self, board, oldMove, flag):
		startTime = int(time.time() * TUNIT)	# Get time in ms

		if flag == config['P1']:
			self.player, self.opponent = 'P1', 'P2'
		else:
			self.player, self.opponent = 'P2', 'P1'

		self.updateBoardState(board.board_status, board.block_status, oldMove)

		currBlock = (oldMove[0] % SZ, oldMove[1] % SZ)

		pointsTable = [[None for i in range(16)] for j in range(16)]
		if self.isOpenMove(currBlock):
			currBlock = (0, 0)
			for i in xrange(4):
				for j in xrange(4):
					self.assignPoints((i, j), pointsTable)
		else:
			self.assignPoints(currBlock, pointsTable)

		# print(pointsTable)

		foundMove = self.findBestMove(pointsTable, currBlock)

		# print("Executed properly.\n")
		print(self.player)
		return foundMove
