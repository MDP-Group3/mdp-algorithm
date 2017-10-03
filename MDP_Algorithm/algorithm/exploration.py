import time
from arena.block import Block
from arena.arena import Arena
from arena.arenaconstant import ArenaConstant
from robot.robot import Robot
from robot.robotconstant import Orientation, Action, Attribute
from algorithm.fastestpath import FastestPath

class Exploration:

	def __init__(self, explored_map, real_map, robot, coverage_limit, time_limit, simulator_surface = None):
		self._explored_map = explored_map
		self._real_map = real_map
		self._robot = robot
		self._coverage_limit = coverage_limit
		self._time_limit = time_limit
		self._surface = simulator_surface
		self._action_taken = []

	def sense_and_update(self):
		self._robot.set_sensor()
		self._robot.sense(self._explored_map, self._real_map)
		if self._surface is not None:
			self._explored_map.draw(self._surface)

	def run(self):
		print("Starting Exploration")

		self._start_time = int(round(time.time() * 1000))
		self._end_time = self._start_time + (self._time_limit * 1000)

		self.sense_and_update()
		area_explored = self.calculate_area_explored()
		print("Explored Area: {}".format(area_explored))
		self.do_exploration(self._robot.get_pos())

	def do_exploration(self, pos):
		while True:
			self.next_move()

			area_explored = self.calculate_area_explored()

			if self._robot.get_pos()[0] == pos[0] and self._robot.get_pos()[1] == pos[1]:
				if area_explored >= 100:
					break

			if area_explored > self._coverage_limit or int(round(time.time() * 1000)) > self._end_time:
				break;

		self.go_home()

	def next_move(self):
		if self.look_right():
			self.move_robot(Action.RIGHT)
			if self.look_forward():
				self.move_robot(Action.FORWARD)
		elif self.look_forward():
			self.move_robot(Action.FORWARD)
		elif self.look_left():
			self.move_robot(Action.LEFT)
			if self.look_forward():
				self.move_robot(Action.FORWARD)
		else:
			self.move_robot(Action.RIGHT)
			self.move_robot(Action.RIGHT)

	def look_right(self):
		_ori = self._robot.get_ori()
		if _ori == Orientation.NORTH.value:
			return self.east_free()
		elif _ori == Orientation.EAST.value:
			return self.south_free()
		elif _ori == Orientation.SOUTH.value:
			return self.west_free()
		elif _ori == Orientation.WEST.value:
			return self.north_free()
		return False

	def look_forward(self):
		_ori = self._robot.get_ori()
		if _ori == Orientation.NORTH.value:
			return self.north_free()
		elif _ori == Orientation.EAST.value:
			return self.east_free()
		elif _ori == Orientation.SOUTH.value:
			return self.south_free()
		elif _ori == Orientation.WEST.value:
			return self.west_free()
		return False

	def look_left(self):
		_ori = self._robot.get_ori()
		if _ori == Orientation.NORTH.value:
			return self.west_free()
		elif _ori == Orientation.EAST.value:
			return self.north_free()
		elif _ori == Orientation.SOUTH.value:
			return self.east_free()
		elif _ori == Orientation.WEST.value:
			return self.south_free()
		return False

	def north_free(self):
		_cur_pos = self._robot.get_pos()
		return self.is_explored_not_obstacle((_cur_pos[0] - 1, _cur_pos[1] - 1)) and self.is_explored_and_free((_cur_pos[0] - 1, _cur_pos[1])) and self.is_explored_not_obstacle((_cur_pos[0] - 1, _cur_pos[1] + 1))

	def east_free(self):
		_cur_pos = self._robot.get_pos()
		return self.is_explored_not_obstacle((_cur_pos[0] + 1, _cur_pos[1] + 1)) and self.is_explored_and_free((_cur_pos[0], _cur_pos[1] + 1)) and self.is_explored_not_obstacle((_cur_pos[0] - 1, _cur_pos[1] + 1))

	def south_free(self):
		_cur_pos = self._robot.get_pos()
		return self.is_explored_not_obstacle((_cur_pos[0] + 1, _cur_pos[1] - 1)) and self.is_explored_and_free((_cur_pos[0] + 1, _cur_pos[1])) and self.is_explored_not_obstacle((_cur_pos[0] + 1, _cur_pos[1] + 1))

	def west_free(self):
		_cur_pos = self._robot.get_pos()
		return self.is_explored_not_obstacle((_cur_pos[0] + 1, _cur_pos[1] - 1)) and self.is_explored_and_free((_cur_pos[0], _cur_pos[1] - 1)) and self.is_explored_not_obstacle((_cur_pos[0] - 1, _cur_pos[1] - 1))

	def go_home(self):
		if self._coverage_limit == 300 and self._time_limit == 3600:
			if not self._robot.get_reachedGoal():
				while True:
					_go_to_goal = FastestPath(self._explored_map, self._robot, self._real_map, self._surface)
					_status = _go_to_goal.do_fastest_path(ArenaConstant.GOAL_POS.value)
					if _status != 'T':
						break

			while True:
				_return_to_start = FastestPath(self._explored_map, self._robot, self._real_map, self._surface)
				_status = _return_to_start.do_fastest_path(Attribute.START_POS.value)
				if _status != 'T':
					break
		else:
			_backtrace = list(self._action_taken)
			while len(_backtrace) != 0:
				_act = _backtrace.pop()
				if _act == Action.FORWARD:
					self.move_robot(Action.BACKWARD)
				elif _act == Action.RIGHT:
					self.move_robot(Action.LEFT)
				elif _act == Action.LEFT:
					self.move_robot(Action.RIGHT)
				elif _act == Action.BACKWARD:
					self.move_robot(Action.FORWARD)

		print("Exploration Completed!")
		area_explored = self.calculate_area_explored()
		print("{:0.2f}% Coverage".format(((area_explored / 300.0) * 100)))
		print("{} Blocks".format(area_explored))
		print("{} seconds".format((int(round(time.time() * 1000)) - self._start_time) / 1000))

		self.turn_robot(Orientation.NORTH.value)


	def is_explored_not_obstacle(self, pos):
		if self._explored_map.check_valid_coord(pos):
			_block = self._explored_map.get_block(pos)
			return _block.is_explored() and not _block.is_obstacle()
		return False

	def is_explored_and_free(self, pos):
		if self._explored_map.check_valid_coord(pos):
			_block = self._explored_map.get_block(pos)
			return _block.is_explored() and not _block.is_virtualwall() and not _block.is_obstacle()
		return False

	def calculate_area_explored(self):
		_result = 0
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if self._explored_map.get_block((row, col)).is_explored():
					_result += 1

		return _result

	def move_robot(self, action):
		self._action_taken.append(action)
		self._robot.move(action)
		if self._surface is not None:
			self._explored_map.draw(self._surface)
		if action is not Action.CALIBRATE:
			self.sense_and_update()

	def turn_robot(self, _ori_target):
		_num_of_turn = abs(self._robot.get_ori() - _ori_target)
		if _num_of_turn > 2:
			_num_of_turn = _num_of_turn % 2

		if _num_of_turn == 1:
			if Orientation.getNext(self._robot.get_ori()) == _ori_target:
				self.move_robot(Action.RIGHT)
			else:
				self.move_robot(Action.LEFT)
		elif _num_of_turn == 2:
			self.move_robot(Action.RIGHT)
			self.move_robot(Action.RIGHT)
