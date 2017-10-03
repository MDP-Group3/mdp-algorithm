import pygame, sys
from pygame.locals import *
from simulator.robotsprite import RobotSprite
from arena.arenaconstant import ArenaConstant
from arena.block import Block
from robot.robotconstant import Attribute

class Arena:

	def __init__(self, robot):
		self._robot = robot
		self._robot_group = pygame.sprite.Group()
		self._robotsprite = RobotSprite(self._robot)
		self._robot_group.add(self._robotsprite)

		self._grid = [[None for col in range(ArenaConstant.ARENA_COL.value)] for row in range(ArenaConstant.ARENA_ROW.value)]
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				self._grid[row][col] = Block((row, col))

				if row == 0 or col == 0 or row == ArenaConstant.ARENA_ROW.value - 1 or col == ArenaConstant.ARENA_COL.value - 1:
					self._grid[row][col].set_virtualwall(True)

	def check_valid_coord(self, pos):
		return 0 <= pos[0] < ArenaConstant.ARENA_ROW.value and 0 <= pos[1] < ArenaConstant.ARENA_COL.value

	def is_startzone(self, pos):
		return 17 <= pos[0] <= 19 and 0 <= pos[1] <= 2

	def is_goalzone(self, pos):
		return 0 <= pos[0] <= 2 and 12 <= pos[1] <= 14

	def get_block(self, pos):
		return self._grid[pos[0]][pos[1]]

	def is_obstacle(self, pos):
		if self.check_valid_coord(pos):
			return self._grid[pos[0]][pos[1]].is_obstacle()

	def is_virtualwall(self, pos):
		return self._grid[pos[0]][pos[1]].is_virtualwall()

	def set_allexplored(self):
		for row in range(len(self._grid)):
			for col in range(len(self._grid[row])):
				self._grid[row][col].set_explored(True) 

	def set_allunexplored(self):
		for row in range(len(self._grid)):
			for col in range(len(self._grid[row])):
				if self.is_startzone((row, col)) or self.is_goalzone((row, col)):
					self._grid[row][col].set_explored(True)
				else:
					self._grid[row][col].set_explored(False)

	def set_obstacle(self, pos, obstacle):
		if obstacle and (self.is_startzone(pos) or self.is_goalzone(pos)):
			return

		self._grid[pos[0]][pos[1]].set_obstacle(obstacle)

		if pos[0] >= 0:
			_temp_pos = (pos[0] + 1, pos[1])
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # bottom block

			if pos[1] < ArenaConstant.ARENA_COL.value:
				_temp_pos = (pos[0] + 1, pos[1] + 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # bottom-right block

			if pos[1] >= 0:
				_temp_pos = (pos[0] + 1, pos[1] - 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # bottom-left block

		if pos[0] < ArenaConstant.ARENA_ROW.value:
			_temp_pos = (pos[0] - 1, pos[1])
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # top block

			if pos[1] < ArenaConstant.ARENA_COL.value:
				_temp_pos = (pos[0] - 1, pos[1] + 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # top-right block

			if pos[1] >= 0:
				_temp_pos = (pos[0] - 1, pos[1] - 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # top-left block

		if pos[1] >= 0:
			_temp_pos = (pos[0], pos[1] - 1)
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # left block

		if pos[1] < ArenaConstant.ARENA_COL.value:
			_temp_pos = (pos[0], pos[1] + 1)
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_virtualwall(obstacle) # right block

	def checkObstacleOrWall(self, pos):
		return not check_valid_coord(pos) or self.get_block(pos).is_obstacle()

	def draw(self, surface):
		self._robot_group.clear(surface[0], surface[1])
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if self.is_startzone((row, col)):
					_block_color = ArenaConstant.C_START.value
				elif self.is_goalzone((row, col)):
					_block_color = ArenaConstant.C_GOAL.value
				else:
					if not self._grid[row][col].is_explored():
						_block_color = ArenaConstant.C_UNEXPLORED.value
					elif self._grid[row][col].is_obstacle():
						_block_color = ArenaConstant.C_OBSTACLE.value
					else:
						_block_color = ArenaConstant.C_CLEARED.value

				pygame.draw.rect(surface[1], _block_color, (col * ArenaConstant.BLOCK_SIZE.value , row * ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value))
				pygame.draw.rect(surface[1], (0,0,0), (col * ArenaConstant.BLOCK_SIZE.value, row * ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value), 1)

		surface[0].blit(surface[1], (0,0))
		self._robotsprite.update()
		self._robot_group.draw(surface[0])
		pygame.display.update()
		#pygame.time.Clock().tick(20)
		pygame.time.delay(self._robot.get_speed())