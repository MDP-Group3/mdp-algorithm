from arena.block import Block
from arena.arenaconstant import ArenaConstant
from robot.robot import Robot
from robot.robotconstant import Orientation, Action, Attribute

class FastestPath:

	def __init__(self, _map, robot, _real_map = None, simulator_surface = None):
		self._real_map = _real_map
		self._surface = simulator_surface
		if self._real_map is not None:
			self._exploration_mode = True

		self.init_object(_map, robot)

	def init_object(self, _map, robot):
		self._robot = robot
		self._map = _map
		self._to_visit = []
		self._visited = []
		self._parents = {}
		self._neighbours = [None] * 4
		self._cur = self._map.get_block(self._robot.get_pos())
		self._cur_ori = self._robot.get_ori()
		self._path_cost = [[None for col in range(ArenaConstant.ARENA_COL.value)] for row in range(ArenaConstant.ARENA_ROW.value)]

		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				_block = self._map.get_block((row, col))
				if not self.can_be_visited(_block):
					self._path_cost[row][col] = Attribute.INFINITE_COST.value
				else:
					self._path_cost[row][col] = -1

		self._to_visit.append(self._cur)

		self._path_cost[self._robot.get_pos()[0]][self._robot.get_pos()[1]] = 0
		self._loop_count = 0

	def can_be_visited(self, block):
		return block.is_explored() and not block.is_obstacle() and not block.is_virtualwall()

	def minimum_cost_block(self, goal_pos):
		_size = len(self._to_visit)
		_min_cost = Attribute.INFINITE_COST.value
		_result = None

		for i in range(_size - 1, -1, -1):
			_block = self._to_visit[i]
			_path_cost = self._path_cost[_block.get_pos()[0]][_block.get_pos()[1]]
			_cost = _path_cost + self.h_cost(_block, goal_pos)
			if _cost < _min_cost:
				_min_cost = _cost
				_result = _block

		return _result

	def h_cost(self, block, goal_pos):
		_move_cost = (abs(goal_pos[1] - block.get_pos()[1]) + abs(goal_pos[0] - block.get_pos()[0])) * Attribute.MOVE_COST.value
		if _move_cost == 0:
			return 0

		_turn_cost = 0
		if goal_pos[1] - block.get_pos()[1] != 0 and goal_pos[0] - block.get_pos()[0] != 0:
			_turn_cost = Attribute.TURN_COST.value

		return _move_cost + _turn_cost

	def get_target_ori(self, from_pos, from_ori, target):
		if from_pos[1] - target.get_pos()[1] > 0:
			return Orientation.WEST.value
		elif target.get_pos()[1] - from_pos[1] > 0:
			return Orientation.EAST.value
		else:
			if from_pos[0] - target.get_pos()[0] > 0:
				return Orientation.NORTH.value
			elif target.get_pos()[0] - from_pos[0] > 0:
				return Orientation.SOUTH.value
			else:
				return from_ori

	def get_turn_cost(self, ori_a, ori_b):
		_num_of_turn = abs(ori_a - ori_b)
		if _num_of_turn > 2:
			_num_of_turn = _num_of_turn % 2

		return _num_of_turn * Attribute.TURN_COST.value

	def path_cost(self, block_a, block_b, ori_a):
		_move_cost = Attribute.MOVE_COST.value

		_ori_target = self.get_target_ori((block_a.get_pos()[0], block_a.get_pos()[1]), ori_a, block_b)
		_turn_cost = self.get_turn_cost(ori_a, _ori_target)

		return _move_cost + _turn_cost

	def do_fastest_path(self, goal_pos):
		print('Fastest Path From {} to {}'.format(self._cur.get_pos(), goal_pos))

		while True:
			self._loop_count += 1

			self._cur = self.minimum_cost_block(goal_pos)

			if self._cur in self._parents:
				self._cur_ori = self.get_target_ori(self._parents.get(self._cur).get_pos(), self._cur_ori, self._cur) 

			self._visited.append(self._cur)
			self._to_visit.remove(self._cur)

			if self._map.get_block(goal_pos) in self._visited:
				print('Reached Goal, Path Found!')
				_path = self.get_path(goal_pos)
				self.print_fastest_path(_path)
				return self.execute_path(_path, goal_pos)

			# Top Neighbour
			if self._map.check_valid_coord((self._cur.get_pos()[0] - 1, self._cur.get_pos()[1])):
				self._neighbours[0] = self._map.get_block((self._cur.get_pos()[0] - 1, self._cur.get_pos()[1]))
				if not self.can_be_visited(self._neighbours[0]):
					self._neighbours[0] = None

			# Bottom Neighbour
			if self._map.check_valid_coord((self._cur.get_pos()[0] + 1, self._cur.get_pos()[1])):
				self._neighbours[1] = self._map.get_block((self._cur.get_pos()[0] + 1, self._cur.get_pos()[1]))
				if not self.can_be_visited(self._neighbours[1]):
					self._neighbours[1] = None

			# Left Neighbour
			if self._map.check_valid_coord((self._cur.get_pos()[0], self._cur.get_pos()[1] - 1)):
				self._neighbours[2] = self._map.get_block((self._cur.get_pos()[0], self._cur.get_pos()[1] - 1))
				if not self.can_be_visited(self._neighbours[2]):
					self._neighbours[2] = None

			# Right Neighbour
			if self._map.check_valid_coord((self._cur.get_pos()[0], self._cur.get_pos()[1] + 1)):
				self._neighbours[3] = self._map.get_block((self._cur.get_pos()[0], self._cur.get_pos()[1] + 1))
				if not self.can_be_visited(self._neighbours[3]):
					self._neighbours[3] = None

			for i in range(4):
				if self._neighbours[i] is not None:
					if self._neighbours[i] in self._visited:
						continue

					_new_path_cost = self._path_cost[self._cur.get_pos()[0]][self._cur.get_pos()[1]] + self.path_cost(self._cur, self._neighbours[i], self._cur_ori)
					if self._neighbours[i] not in self._to_visit:
						self._parents[self._neighbours[i]] = self._cur
						self._path_cost[self._neighbours[i].get_pos()[0]][self._neighbours[i].get_pos()[1]] = _new_path_cost
						self._to_visit.append(self._neighbours[i])
					else:
						_cur_path_cost = self._path_cost[self._neighbours[i].get_pos()[0]][self._neighbours[i].get_pos()[1]]
						if _new_path_cost < _cur_path_cost:
							self._path_cost[self._neighbours[i].get_pos()[0]][self._neighbours[i].get_pos()[1]] = _new_path_cost
							self._parents[self._neighbours[i]] = self._cur

			if len(self._to_visit) == 0:
				break;

		print('Path cannot be found!')
		return None

	def get_path(self, goal_pos):
		_actual_path = []
		_temp_block = self._map.get_block(goal_pos)

		while True:
			_actual_path.append(_temp_block)
			_temp_block = self._parents.get(_temp_block)
			if _temp_block is None:
				break

		return _actual_path

	def execute_path(self, path, goal_pos):
		_output_string = []

		_temp_block = path.pop()

		_ori_target = None

		_actions = []

		_temp_robot = Robot(self._robot.get_pos(), False)
		_temp_robot.set_ori(self._robot.get_ori())
		_temp_robot.set_speed(0)

		while _temp_robot.get_pos()[0] != goal_pos[0] or _temp_robot.get_pos()[1] != goal_pos[1]:
			if _temp_robot.get_pos()[0] == _temp_block.get_pos()[0] and _temp_robot.get_pos()[1] == _temp_block.get_pos()[1]:
				_temp_block = path.pop()

			_ori_target = self.get_target_ori(_temp_robot.get_pos(), _temp_robot.get_ori(), _temp_block)

			_action = None
			if _temp_robot.get_ori() != _ori_target:
				_action = self.get_target_move(_temp_robot.get_ori(), _ori_target)
			else:
				_action = Action.FORWARD

			print('Action {} from {} to {}'.format(_action.value, _temp_robot.get_pos(), _temp_block.get_pos()))
			print(_temp_robot.get_ori())
			_temp_robot.move(_action)
			_actions.append(_action)
			_output_string.append(_action.value)
		
		if not self._robot.is_actual_robot() or self._exploration_mode:
			for _act in _actions:
				print('{} from {}'.format(_act, self._robot.get_pos()))
				if _act == Action.FORWARD:
					if not self.can_move_forward():
						print("Fastest Path Execution terminated!")
						return "T"

				self._robot.move(_act)
				if self._surface is not None:
					self._map.draw(self._surface)

				if self._exploration_mode:
					self._robot.set_sensor()
					self._robot.sense(self._map, self._real_map)
					if self._surface is not None:
						self._map.draw(self._surface)

		print('Actions: {}'.format(''.join(_output_string)))
		return ''.join(_output_string)

	def can_move_forward(self):
		_pos = self._robot.get_pos()
		_ori = self._robot.get_ori()
		#print(_ori)

		if _ori == Orientation.NORTH.value:
			#print('{},{},{}'.format(self._map.is_obstacle((_pos[0] - 2, _pos[1] - 1)), (_pos[0] - 2, _pos[1]), self._map.is_obstacle((_pos[0] - 2, _pos[1] + 1))))
			if not self._map.is_obstacle((_pos[0] - 2, _pos[1] - 1)) and not self._map.is_obstacle((_pos[0] - 2, _pos[1])) and not self._map.is_obstacle((_pos[0] - 2, _pos[1] + 1)):
				return True
		elif _ori == Orientation.EAST.value:
			#print('{},{},{}'.format(self._map.is_obstacle((_pos[0] - 1, _pos[1] + 2)), (_pos[0], _pos[1] + 2), self._map.is_obstacle((_pos[0] + 1, _pos[1] + 2))))
			if not self._map.is_obstacle((_pos[0] - 1, _pos[1] + 2)) and not self._map.is_obstacle((_pos[0], _pos[1] + 2)) and not self._map.is_obstacle((_pos[0] + 1, _pos[1] + 2)):
				return True
		elif _ori == Orientation.SOUTH.value:
			#print('{},{},{}'.format(self._map.is_obstacle((_pos[0] + 2, _pos[1] - 1)), (_pos[0] + 2, _pos[1]), self._map.is_obstacle((_pos[0] + 2, _pos[1] + 1))))
			if not self._map.is_obstacle((_pos[0] + 2, _pos[1] - 1)) and not self._map.is_obstacle((_pos[0] + 2, _pos[1])) and not self._map.is_obstacle((_pos[0] + 2, _pos[1] + 1)):
				return True
		elif _ori == Orientation.WEST.value:
			#print('{},{},{}'.format(self._map.is_obstacle((_pos[0] - 1, _pos[1] - 2)), (_pos[0], _pos[1] - 2), self._map.is_obstacle((_pos[0] + 1, _pos[1] - 2))))
			if not self._map.is_obstacle((_pos[0] - 1, _pos[1] - 2)) and not self._map.is_obstacle((_pos[0], _pos[1] - 2)) and not self._map.is_obstacle((_pos[0] + 1, _pos[1] - 2)):
				return True

	def get_target_move(self, _ori_a, _ori_b):
		if _ori_a == Orientation.NORTH.value:
			if _ori_b == Orientation.NORTH.value:
				return Action.ERROR
			elif _ori_b == Orientation.SOUTH.value:
				return Action.LEFT
			elif _ori_b == Orientation.WEST.value:
				return Action.LEFT
			elif _ori_b == Orientation.EAST.value:
				return Action.RIGHT
		elif _ori_a == Orientation.SOUTH.value:
			if _ori_b == Orientation.NORTH.value:
				return Action.LEFT
			elif _ori_b == Orientation.SOUTH.value:
				return Action.ERROR
			elif _ori_b == Orientation.WEST.value:
				return Action.RIGHT
			elif _ori_b == Orientation.EAST.value:
				return Action.LEFT
		elif _ori_a == Orientation.WEST.value:
			if _ori_b == Orientation.NORTH.value:
				return Action.RIGHT
			elif _ori_b == Orientation.SOUTH.value:
				return Action.LEFT
			elif _ori_b == Orientation.WEST.value:
				return Action.ERROR
			elif _ori_b == Orientation.EAST.value:
				return Action.LEFT
		elif _ori_a == Orientation.EAST.value:
			if _ori_b == Orientation.NORTH.value:
				return Action.LEFT
			elif _ori_b == Orientation.SOUTH.value:
				return Action.RIGHT
			elif _ori_b == Orientation.WEST.value:
				return Action.LEFT
			elif _ori_b == Orientation.EAST.value:
				return Action.ERROR

		return Action.ERROR

	def print_fastest_path(self, path):
		print('Executed {} Loops'.format(self._loop_count))
		print('Number of steps required: {}'.format((len(path) - 1)))

		_print_path = list(path)
		_temp_block = None
		print('Fastest Path: ')
		while len(_print_path) != 0:
			_temp_block = _print_path.pop()
			if len(_print_path) != 0:
				print('{} --> '.format(_temp_block.get_pos()), end='')
			else:
				print('{}'.format(_temp_block.get_pos()))