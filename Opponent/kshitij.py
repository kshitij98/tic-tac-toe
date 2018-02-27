import sys
import random
import time
import hashlib
import copy
import os
import traceback
import signal

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
		self.miniMaxMove = None
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
			self.pivot[0] = 1 + (oldMove[0]//4 < 2)
			self.pivot[1] = 1 + (oldMove[1]//4 < 2)

		self.miniMaxMoveH = -config['INF']
		self.stratH = -config['INF']

	def isValuable(self, currBlock):
		if currBlock[0] == self.pivot[0] or currBlock[1] == self.pivot[1]:
			return True
		return False

	def isOpenMove(self, currBlock):
		if currBlock == (-1, -1) or self.block[currBlock[0]][currBlock[1]] != config['EM']:
			return True
		return False


	# TODO: Assign exponential probabilities?
	def getWinProb(self, filled):
		if filled < 0:
			return 0
		return pow(1.7, filled-1)


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
			return 13 # TODO: Set constant value, Not infinity

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
				c1, c2, c3 = 2, 1, 4
			else: # Give high weight to winning this block, lesser to useless transfer
				c1, c2, c3 = 4, 1, 2

		else: # Give higher weight to winning this block, then to blocking, then to useless transfer
			c1, c2, c3 = 5, 4, 3.5

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


	def diamondCheckBlock(self, currBlock, flag, coord):
		x, y = currBlock[0] * 4 + coord[0], currBlock[1] * 4 + coord[1] 
		winning = ((self.board[x - 1][y] == flag)
						and (self.board[x][y - 1] == flag)
						and (self.board[x + 1][y] == flag)
						and (self.board[x][y + 1] == flag))

		return winning

	def diamondCheckGame(self, flag, coord):
		x, y = coord[0], coord[1] 
		winning = ((self.block[x - 1][y] == flag)
						and (self.block[x][y - 1] == flag)
						and (self.block[x + 1][y] == flag)
						and (self.block[x][y + 1] == flag))

		return winning


	def checkWinInBlock(self, currBlock, flag):
		x, y = currBlock[0] * 4, currBlock[1] * 4
		winning = False
		
		for i in xrange(4):
			bwinning = True
			for j in xrange(4):
				bwinning = bwinning and (self.board[x + i][y + j] == flag)
			winning = winning or bwinning
		
		# Vertical Line Check
		for i in xrange(SZ):
			bwinning = True
			for j in xrange(SZ):
				bwinning = bwinning and (self.board[x + j][y + i] == flag)
			winning = winning or bwinning
		
		# Diamond Check
		winning = winning or self.diamondCheck(currBlock, flag, (1, 1))
		winning = winning or self.diamondCheck(currBlock, flag, (1, 2))
		winning = winning or self.diamondCheck(currBlock, flag, (2, 1))
		winning = winning or self.diamondCheck(currBlock, flag, (2, 2))
		
		return winning


	def addMove(self, playedMove, flag):
		self.board[playedMove[0]][playedMove[1]] = flag
		currBlock = (playedMove[0] // 4, playedMove[1] // 4)
		if self.block[currBlock[0]][currBlock[1]] == config['EM'] and self.checkWinInBlock(currBlock, flag):
			self.block[currBlock[0]][currBlock[1]] = flag


	def removeMove(self, playedMove, flag):
		self.board[playedMove[0]][playedMove[1]] = config['EM']
		currBlock = (playedMove[0] // 4, playedMove[1] // 4)
		if self.block[currBlock[0]][currBlock[1]] == flag and not self.checkWinInBlock(currBlock, flag):
			self.block[currBlock[0]][currBlock[1]] = config['EM']


	def getValidMoves(self, currBlock):
		validMoves = []
		if self.isOpenMove(currBlock):
			for i in xrange(16):
				for j in xrange(16):
					if self.block[i//4][j//4] == config['EM'] and self.board[i][j] == config['EM']:
						validMoves.append((i, j))
		else:
			x, y = currBlock[0] * 4, currBlock[1] * 4
			for i in xrange(4):
				for j in xrange(4):
					if self.board[x+i][y+j] == config['EM']:
						validMoves.append((x+i, y+j))

		return validMoves


	def isFinished():
		# winning = False
		p1Won = False
		p2Won = False

		for i in xrange(4):
			p1winning = True
			p2winning = True
			for j in xrange(4):
				p1winning = p1winning and (self.board[i][j] == config['P1'])
				p2winning = p2winning and (self.board[i][j] == config['P2'])
			p1Won = p1Won or p1winning
			p2Won = p2Won or p2winning

		
		# Vertical Line Check
		for i in xrange(4):
			p1winning = True
			p2winning = True
			for j in xrange(4):
				p1winning = p1winning and (self.board[j][i] == config['P1'])
				p2winning = p2winning and (self.board[j][i] == config['P2'])
			p1Won = p1Won or p1winning
			p2Won = p2Won or p2winning
		
		# Diamond Check
		P1Won = P1Won or self.diamondCheckGame(config['P1'], (1, 1))
		P1Won = P1Won or self.diamondCheckGame(config['P1'], (1, 2))
		P1Won = P1Won or self.diamondCheckGame(config['P1'], (2, 1))
		P1Won = P1Won or self.diamondCheckGame(config['P1'], (2, 2))
		
		P2Won = P2Won or self.diamondCheckGame(config['P2'], (1, 1))
		P2Won = P2Won or self.diamondCheckGame(config['P2'], (1, 2))
		P2Won = P2Won or self.diamondCheckGame(config['P2'], (2, 1))
		P2Won = P2Won or self.diamondCheckGame(config['P2'], (2, 2))

		if P1Won:
			if self.player == 'P1':
				self.winnerH = config['INF']
			else:
				self.winnerH = -config['INF']

		elif P2Won:
			if self.player == 'P2':
				self.winnerH = config['INF']
			else:
				self.winnerH = -config['INF']

		return P1Won or P2Won


	def diamondWinChance(self, move, player):
		return self.getWinningChance((move[0] + 1, move[1]), player) * self.getWinningChance((move[0] - 1, move[1]), player) * self.getWinningChance((move[0], move[1] + 1), player) * self.getWinningChance((move[0], move[1] - 1), player)

	def getH(self, lastMove, player):
		# self.board
		maxProb = 0
		for i in xrange(4):
			prob = 1
			for j in xrange(4):
				prob *= self.getWinningChance((i, j), player)
			maxProb = max(maxProb, prob)

		for i in xrange(4):
			prob = 1
			for j in xrange(4):
				prob *= self.getWinningChance((j, i), player)
			maxProb = max(maxProb, prob)

		maxProb = max(maxProb, self.getWinningChance((1, 1), player))
		maxProb = max(maxProb, self.getWinningChance((1, 2), player))
		maxProb = max(maxProb, self.getWinningChance((2, 1), player))
		maxProb = max(maxProb, self.getWinningChance((2, 2), player))

		return maxProb

	def miniMax(self, currDepth, alpha, beta, ourMove, lastMove):
		if currDepth == self.maxDepth:
			if ourMove:
				return self.getH(lastMove, self.player)
			else:
				return self.getH(lastMove, self.opponent)

		elif self.isFinished():
			return self.winnerH
	
		if ourMove:
			finalH = -config['INF']
			currBlock = (lastMove[0] % 4, lastMove[1] % 4)

			validMoves = self.getValidMoves(currBlock)

			numOfMoves = len(validMoves)
			for i in xrange(numOfMoves):		# for each child of node
				addMove(validMoves[i], config[self.player])
				finalH = max(finalH, miniMax(currDepth + 1, alpha, beta, False, validMoves[i]))
				alpha = max(alpha, finalH)
				if beta <= alpha:
					break
				removeMove(validMoves[i], config[self.player])

			if currDepth == 1 and lastMove == self.foundMove:
				self.stratH = finalH
			elif currDepth == 1 and finalH > self.miniMaxMoveH:
				self.miniMaxMoveH = finalH
				self.miniMaxMove = lastMove

			return finalH
		else:
			finalH = config['INF']
			currBlock = (lastMove[0] % 4, lastMove[1] % 4)

			validMoves = self.getValidMoves(currBlock)

			numOfMoves = len(validMoves)
			for i in xrange(numOfMoves):		# for each child of node
				addMove(validMoves[i], config[self.opponent])
				finalH = min(finalH, miniMax(currDepth + 1, alpha, beta, True, validMoves[i]))
				beta = min(beta, finalH)
				if beta <= alpha:
					break # (* alpha cut-off *)
				removeMove(validMoves[i], config[self.opponent])
			return finalH


	def signal_handler(self, signum, frame):
		raise Exception('Timed out!')


	# Move the piece
	def move(self, board, oldMove, flag):
		signal.signal(signal.SIGALRM, self.signal_handler)
		signal.alarm(15)

		bestMove = None

		try:
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
	
			self.foundMove = self.findBestMove(pointsTable, currBlock)
	
			# print("Executed properly.\n")
			print(self.player)
			print(self.pivot)

			for i in xrange(3, 50):
				print(i)
				self.maxDepth = i
				self.miniMax(i, -config['INF'], config['INF'], True, oldMove)

		except Exception as e:
			print 'Exception occurred ', e

		if self.stratH * 1.5 < self.miniMaxMoveH:
			return self.miniMaxMove
		return self.foundMove
