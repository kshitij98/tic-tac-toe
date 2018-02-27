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

class MiniMax:

	def __init__(self):
		self.clone = copy.deepcopy
		self.currentBlockStatus = None
		self.currentBoardStatus = None
		self.transpositionTable = dict()
		self.movesMade = 0
		return

	def drawPoints(self, boardState, myFlag):
		oppFlag = config['P1']
		if myFlag == config['P1']:
			oppFlag = config['P2']

		myScore = oppScore = 0
		for i in xrange(4):
			for j in xrange(4):
				if boardState[i][j] == myFlag:
					myScore += config['POINTS'][i][j]
				elif boardState[i][j] == oppFlag:
					oppScore += config['POINTS'][i][j]

		return (myScore, oppScore)

	def diamondCheck(self, boardState, blockCoord, flag, coord):
		flag = ((boardState[blockCoord[0] * SZ + coord[0] - 1][blockCoord[1] * SZ + coord[1]] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0]][blockCoord[1] * SZ + coord[1] - 1] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0] + 1][blockCoord[1] * SZ + coord[1]] == flag)
						and (boardState[blockCoord[0] * SZ + coord[0]][blockCoord[1] * SZ + coord[1] + 1] == flag))

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
				bFlag = bFlag and (boardState[blockCoord[0] * SZ + i][blockCoord[1] * SZ + j] == flag)
			flag = flag or bFlag

		# Vertical Line Check
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (boardState[blockCoord[0] * SZ + j][blockCoord[1] * SZ + i] == flag)
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
				bFlag = bFlag and (blockState[i][j] == flag)
			flag = flag or bFlag

		# Vertical Line Check
		for i in xrange(SZ):
			bFlag = True
			for j in xrange(SZ):
				bFlag = bFlag and (blockState[j][i] == flag)
			flag = flag or bFlag

		# Diamond Check
		flag = flag or self.diamondCheckBlock(blockState, flag, (1, 1))
		flag = flag or self.diamondCheckBlock(blockState, flag, (1, 2))
		flag = flag or self.diamondCheckBlock(blockState, flag, (2, 1))
		flag = flag or self.diamondCheckBlock(blockState, flag, (2, 2))

		return flag

	def getValidMoves(self, board, oldMove):
		validCells = []
		blockMove = (oldMove[0] % SZ, oldMove[1] % SZ)
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

	def listToTuple(self, T):
		X = [''.join(x) for x in T]
		return ''.join(X)

	def gameSimulation(self, boardState, move, flag):
		origFlag = flag
		winCount = 0
		self.stateList = list()

		# Play Gme until End
		while True:
			boardState.board_status[move[0]][move[1]] = flag # Place the marker on Board
			if flag == origFlag:
				self.stateList.append(hashlib.md5(self.listToTuple(boardState.board_status)).hexdigest())
			# Check if the Small Block is won
			if self.checkWinInBlock(boardState.board_status, (int(move[0] / 4), int(move[1] / 4)), flag) and winCount <= 2:
				winCount += 1
				boardState.block_status[int(move[0] / 4)][int(move[1] / 4)] = flag
				if self.checkWinOnBoard(boardState.block_status, flag):
					return (origFlag == flag)
			# Check if the win is 2 consecutive times
			elif self.checkWinInBlock(boardState.board_status, (int(move[0] / 4), int(move[1] / 4)),flag):
				boardState.block_status[int(move[0] / 4)][int(move[1] / 4)] = flag
				if self.checkWinOnBoard(boardState.block_status, flag):
					return (origFlag == flag)
				if flag == config['P1']:
					flag = config['P2']
				else:
					flag = config['P1']
				winCount = 0
			# Reverse the moves
			else:
				winCount = 0
				if flag == config['P1']:
					flag = config['P2']
				else:
					flag = config['P1']
			movesAvail = self.getValidMoves(boardState, move)
			if len(movesAvail) == 0:
				return boardState.block_status
			move = movesAvail[random.randint(0, len(movesAvail) - 1)]
		return boardState.block_status

	def updateTransposition(self, win=0, draw=0, loss=0):
		self.currentState = self.stateList[0]
		for i in self.stateList:
			if i in self.transpositionTable:
				temp = self.transpositionTable[i]
				temp['winMatch']  += win
				temp['drawMatch'] += draw
				temp['lossMatch'] += loss
			else:
				self.transpositionTable[i] = dict()
				temp = self.transpositionTable[i]
				temp['winMatch']  = win
				temp['lossMatch'] = draw
				temp['drawMatch'] = loss

	# Move the piece
	def move(self, board, oldMove, flag):
		startTime = int(time.time() * TUNIT)	# Get time in ms
		# Deep copy the Current Board State
		self.validMoveCells 	= self.getValidMoves(board, oldMove)
		self.movesMade 			+= 1

		# Seed random number generator
		random.seed(os.urandom(7))
		currentBestProb = 1.1
		currentBestCell = None
		eachCellTime = 1.0 * config['TIME_LIM'] / len(self.validMoveCells)
		currentCellStartTime = time.time() * TUNIT
		try:
			# Simulate Random Game Play from each cell
			for cell in self.validMoveCells:

				while currentCellStartTime + eachCellTime > time.time() * TUNIT:
					orignalBoard = copy.deepcopy(board)
					outcome = self.gameSimulation(orignalBoard, cell, flag)
					if outcome == True:
						self.updateTransposition(win=1)
					elif outcome == False:
						self.updateTransposition(loss=1)
					else:
						(myScore, oppScore) = self.drawPoints(outcome, flag)
						if myScore < oppScore:
							self.updateTransposition(loss=1)
						elif myScore > oppScore:
							self.updateTransposition(win=1)
						else:
							self.updateTransposition(draw=1)

				temp = self.transpositionTable[self.currentState]
				currentProb = 1.0 * temp['lossMatch'] / (temp['winMatch'] + temp['drawMatch'] + temp['lossMatch'])
				currentCellStartTime = time.time() * TUNIT
				# print cell
				# print currentProb
				# print temp['winMatch']
				if temp['winMatch'] > 0:
					print '=====A win Found!!======'
					exit(0)
				if currentProb < currentBestProb:
					currentBestProb = currentProb
					currentBestCell = cell
			if self.movesMade > 13:
				self.transpositionTable.clear()
				self.movesMade = 0
			return currentBestCell
		except:
			temp = self.transpositionTable[self.currentState]
			currentProb = 1.0 * temp['lossMatch'] / (temp['winMatch'] + temp['drawMatch'] + temp['lossMatch'])
			currentCellStartTime = time.time() * TUNIT
			if currentProb < currentBestProb:
				currentBestProb = currentProb
				currentBestCell = cell
			if self.movesMade > 13:
				self.transpositionTable.clear()
				self.movesMade = 0
			return currentBestCell
