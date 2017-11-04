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

	def is_waypoint(self, pos):
		if self.check_valid_coord(pos):
			return self._grid[pos[0]][pos[1]].is_waypoint()

	def set_waypoint(self, pos):
		if self.check_valid_coord(pos):
			self._grid[pos[0]][pos[1]].set_waypoint(True)

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

	def reset_virtualwall(self):
		# Remove all virtual wall for reset
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				self._grid[row][col].set_virtualwall(False)
		
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if row == 0 or col == 0 or row == ArenaConstant.ARENA_ROW.value - 1 or col == ArenaConstant.ARENA_COL.value - 1:
					self._grid[row][col].set_virtualwall(True)

				if self._grid[row][col].is_obstacle():
					self.set_obstacle((row,col), True)

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
		return not self.check_valid_coord(pos) or self.get_block(pos).is_obstacle()

	def findFurthestObstacle(self):
		_distance = []
		_distance.append(self.checkNorth())
		_distance.append(self.checkSouth())
		_distance.append(self.checkEast())
		_distance.append(self.checkWest())

		_furthest = max(_distance)
		if _distance.index(_furthest) == 0:
			_new_row = self._robot.get_pos()[0] - _furthest - 2
			if _new_row < 0:
				_new_row = 0
			elif _new_row > 19:
				_new_row = 19
			_new_col = self._robot.get_pos()[1]
			return (_new_row, _new_col)
		elif _distance.index(_furthest) == 1:
			_new_row = self._robot.get_pos()[0] + _furthest - 2
			if _new_row < 0:
				_new_row = 0
			elif _new_row > 19:
				_new_row = 19
			_new_col = self._robot.get_pos()[1]
			return (_new_row, _new_col)
		elif _distance.index(_furthest) == 2:
			_new_row = self._robot.get_pos()[0]
			_new_col = self._robot.get_pos()[1] + _furthest - 2
			if _new_col < 0:
				_new_col = 0
			elif _new_col > 14:
				_new_col = 14
			return (_new_row, _new_col)
		elif _distance.index(_furthest) == 4:
			_new_row = self._robot.get_pos()[0]
			_new_col = self._robot.get_pos()[1] - _furthest - 2
			if _new_col < 0:
				_new_col = 0
			elif _new_col > 14:
				_new_col = 14
			return (_new_row, _new_col)

	def checkNorth(self):
		_found = False
		_cur_row = self._robot.get_pos()[0] - 2
		_cur_col = self._robot.get_pos()[1]
		_distance_to_wall = 0
		while not _found:
			if self.check_valid_coord((_cur_row, _cur_col)):
				if self.get_block((_cur_row, _cur_col - 1)).is_obstacle() or self.get_block((_cur_row, _cur_col)).is_obstacle() or self.get_block((_cur_row, _cur_col + 1)).is_obstacle():
					_distance_to_wall = abs(int(_cur_row - self._robot.get_pos()[0]))
					_found = True
			else:
				_distance_to_wall = abs(int(_cur_row - self._robot.get_pos()[0]))
				_found = True

			_cur_row -= 1

		return _distance_to_wall

	def checkSouth(self):
		_found = False
		_cur_row = self._robot.get_pos()[0] + 2
		_cur_col = self._robot.get_pos()[1]
		_distance_to_wall = 0
		while not _found:
			if self.check_valid_coord((_cur_row, _cur_col)):
				if self.get_block((_cur_row, _cur_col - 1)).is_obstacle() or self.get_block((_cur_row, _cur_col)).is_obstacle() or self.get_block((_cur_row, _cur_col + 1)).is_obstacle():
					_distance_to_wall = abs(int(_cur_row - self._robot.get_pos()[0]))
					_found = True
			else:
				_distance_to_wall = abs(int(_cur_row - self._robot.get_pos()[0]))
				_found = True

			_cur_row += 1

		return _distance_to_wall

	def checkEast(self):
		_found = False
		_cur_row = self._robot.get_pos()[0]
		_cur_col = self._robot.get_pos()[1] + 2
		_distance_to_wall = 0
		while not _found:
			if self.check_valid_coord((_cur_row, _cur_col)):
				if self.get_block((_cur_row - 1, _cur_col)).is_obstacle() or self.get_block((_cur_row, _cur_col)).is_obstacle() or self.get_block((_cur_row + 1, _cur_col)).is_obstacle():
					_distance_to_wall = abs(int(_cur_col - self._robot.get_pos()[1]))
					_found = True
			else:
				_distance_to_wall = abs(int(_cur_col - self._robot.get_pos()[1]))
				_found = True

			_cur_col += 1

		return _distance_to_wall

	def checkWest(self):
		_found = False
		_cur_row = self._robot.get_pos()[0]
		_cur_col = self._robot.get_pos()[1] - 2
		_distance_to_wall = 0
		while not _found:
			if self.check_valid_coord((_cur_row, _cur_col)):
				if self.get_block((_cur_row - 1, _cur_col)).is_obstacle() or self.get_block((_cur_row, _cur_col)).is_obstacle() or self.get_block((_cur_row + 1, _cur_col)).is_obstacle():
					_distance_to_wall = abs(int(_cur_col - self._robot.get_pos()[1]))
					_found = True
			else:
				_distance_to_wall = abs(int(_cur_col - self._robot.get_pos()[1]))
				_found = True

			_cur_col -= 1

		return _distance_to_wall

	def set_robot_explored(self):
		pos = self._robot.get_pos()

		self._grid[pos[0]][pos[1]].set_explored(True)

		if pos[0] >= 0:
			_temp_pos = (pos[0] + 1, pos[1])
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # bottom block

			if pos[1] < ArenaConstant.ARENA_COL.value:
				_temp_pos = (pos[0] + 1, pos[1] + 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # bottom-right block

			if pos[1] >= 0:
				_temp_pos = (pos[0] + 1, pos[1] - 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # bottom-left block

		if pos[0] < ArenaConstant.ARENA_ROW.value:
			_temp_pos = (pos[0] - 1, pos[1])
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # top block

			if pos[1] < ArenaConstant.ARENA_COL.value:
				_temp_pos = (pos[0] - 1, pos[1] + 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # top-right block

			if pos[1] >= 0:
				_temp_pos = (pos[0] - 1, pos[1] - 1)
				if self.check_valid_coord(_temp_pos):
					self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # top-left block

		if pos[1] >= 0:
			_temp_pos = (pos[0], pos[1] - 1)
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # left block

		if pos[1] < ArenaConstant.ARENA_COL.value:
			_temp_pos = (pos[0], pos[1] + 1)
			if self.check_valid_coord(_temp_pos):
				self._grid[_temp_pos[0]][_temp_pos[1]].set_explored(True) # right block

	def draw(self, surface):
		self._robot_group.clear(surface[0], surface[1])
		_rect_list = []
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
					elif self._grid[row][col].is_waypoint():
						_block_color = ArenaConstant.C_WAYPOINT.value
					else:
						_block_color = ArenaConstant.C_CLEARED.value

				_rect = pygame.draw.rect(surface[1], _block_color, (col * ArenaConstant.BLOCK_SIZE.value , row * ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value))
				_border = pygame.draw.rect(surface[1], (0,0,0), (col * ArenaConstant.BLOCK_SIZE.value, row * ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value, ArenaConstant.BLOCK_SIZE.value), 1)
				_rect_list.append(_rect)
				_rect_list.append(_border)				

		surface[0].blit(surface[1], (0,0))
		self._robotsprite.update()
		self._robot_group.draw(surface[0])
		pygame.display.update(_rect_list)
		#pygame.time.Clock().tick(10)
		pygame.time.delay(self._robot.get_speed())
		#pygame.time.delay(1000)