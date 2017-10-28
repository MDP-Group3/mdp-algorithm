import time, sys
from arena.block import Block
from arena.arena import Arena
from arena.arenaconstant import ArenaConstant
from arena.arenautils import ArenaUtils
from robot.robot import Robot
from robot.robotconstant import Orientation, Action, Attribute
from algorithm.fastestpath import FastestPath
from comm.comm import CommMgr

class Exploration:

	def __init__(self, explored_map, robot, coverage_limit=300, time_limit=3600):#, simulator_surface = None):
		self._explored_map = explored_map
		#self._real_map = real_map
		self._robot = robot
		self._coverage_limit = coverage_limit
		self._time_limit = time_limit
		#self._surface = simulator_surface
		self._action_taken = []
		self._wp = None
		self.last_calibrate = 0
		self.calibration_mode = False

	def sense_and_update(self):
		self._robot.set_sensor()
		self._robot.sense(self._explored_map)
		#if self._surface is not None:
		#	self._explored_map.draw(self._surface)

	def run(self):
		if self._robot.is_actual_robot():
			print('Awaiting Start Point/Waypoint')
			while True:
				_spwp = CommMgr.recv()
				print(_spwp)
				if _spwp[:2] == 'SP':
					#spxxyywpxxyy
					_sp = (abs(int(_spwp[2:4]) - 19), int(_spwp[4:6]))
					print(_sp)
					#if self._surface is not None:
					#	self._explored_map.draw(self._surface)
					self._wp = (abs(int(_spwp[8:10]) - 19), int(_spwp[10:12]))
					print(self._wp)

					self._robot.notify_arduino(Action.CALIBRATE.value)
					CommMgr.recv()
					self._robot.notify_arduino(Action.RIGHT.value)
					CommMgr.recv()
					self._robot.notify_arduino(Action.CALIBRATE.value)
					CommMgr.recv()
					self._robot.notify_arduino(Action.RIGHT.value)
					CommMgr.recv()

					self._robot.set_pos(_sp[0], _sp[1])
					self._explored_map.set_robot_explored()
					print(_spwp[-1])
					if _spwp[-1] == 'N':
						self.turn_robot(Orientation.NORTH.value)
					elif _spwp[-1] == 'E':
						self.turn_robot(Orientation.EAST.value)
					elif _spwp[-1] == 'S':
						self.turn_robot(Orientation.SOUTH.value)
					elif _spwp[-1] == 'W':
						self.turn_robot(Orientation.WEST.value)
					break

			print('Awaiting EX_START')
			while True:
				_command = CommMgr.recv()
				print(_command)
				if _command == 'EX_START':
					break

		print("Starting Exploration")

		self._start_time = int(round(time.time() * 1000))
		self._end_time = self._start_time + (self._time_limit * 1000)

		if self._robot.is_actual_robot():
			self._robot.notify_arduino(Action.SENSOR.value)#, self._explored_map, False)

		self.sense_and_update()
		area_explored = self.calculate_area_explored()
		print("Explored Area: {}".format(area_explored))
		self.do_exploration(self._robot.get_pos())

	def do_exploration(self, pos):
		while True:
			self.next_move()
			#input_var = input("Enter something to continue: ")
			#print ("you entered " + input_var) 
			#time.sleep(self._robot.get_speed() / 1000)

			area_explored = self.calculate_area_explored()

			if self._robot.get_pos()[0] == pos[0] and self._robot.get_pos()[1] == pos[1]:
				if area_explored >= 100:
					break

			if area_explored > self._coverage_limit or int(round(time.time() * 1000)) > self._end_time:
				break;

		self.go_home()
		if self._robot.is_actual_robot():
			#self._robot.notify_android(Action.CALIBRATE, self._explored_map)
		 	print('Awaiting FP_START')
		 	while True:
		 		_command = CommMgr.recv()
		 		if _command == 'FP_START':
		 			CommMgr.send('X', CommMgr.ARDUINO)
		 			#time.sleep(1)
		 			break

		_go_to_wp_goal = FastestPath(self._explored_map, self._robot)
		_go_to_wp_goal.do_fastest_path_wp_goal(self._wp, ArenaConstant.GOAL_POS.value)

		# if self._wp is not None:
		# 	_go_to_wp_goal = FastestPath(self._explored_map, self._robot)#, self._real_map, self._surface)
		# 	_status = _go_to_wp_goal.do_fastest_path2(self._wp, ArenaConstant.GOAL_POS.value)

		# _go_to_wp_goal = FastestPath(self._explored_map, self._robot)#, self._real_map, self._surface)
		# _status = _go_to_wp_goal.do_fastest_path(ArenaConstant.GOAL_POS.value)
		#print(_status)

	def next_move(self):
		_temp_trace = list(self._action_taken)
		_check_act = None
		if len(_temp_trace) != 0:
			_check_act = _temp_trace.pop()
		_left_loop = False
		_check_counter = 0
		_loop = False
		while not _loop and _check_act is not None:
			if _check_act == Action.LEFT:
				if not _left_loop: 
					_left_loop = True
					_check_counter = 0
				_check_counter += 1
			elif _check_act == Action.RIGHT:
				if _left_loop:
					_left_loop = False
					_check_counter = 0
				_check_counter += 1

			if _check_counter == 8:
				_loop = True
			else:
				if len(_temp_trace) != 0:
					_check_act = _temp_trace.pop()
				else:
					break

		if _loop:
			self.turn_robot(Orientation.NORTH.value)
			_pos = self._explored_map.findFurthestObstacle()
			_go_to_furthest = FastestPath(self._explored_map, self._robot, True)#, self._real_map, self._surface)
			_go_to_furthest.do_fastest_path(_pos)

		if self.look_left():
			self.move_robot(Action.LEFT)
			if self.look_forward():
				self.move_robot(Action.FORWARD)
		# self.look_right():
		# 	self.move_robot(Action.RIGHT)
		# 	if self.look_forward():
		# 		self.move_robot(Action.FORWARD)
		
		elif self.look_forward():
			self.move_robot(Action.FORWARD)
		elif self.look_right():
			self.move_robot(Action.RIGHT)
			if self.look_forward():
				self.move_robot(Action.FORWARD)
		# self.look_left():
		#  	self.move_robot(Action.LEFT)
		#  	if self.look_forward():
		#  		self.move_robot(Action.FORWARD)
		else:
			self.move_robot(Action.UTURN)

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
					_go_to_goal = FastestPath(self._explored_map, self._robot, True)#, self._real_map, self._surface)
					_status = _go_to_goal.do_fastest_path(ArenaConstant.GOAL_POS.value)
					if _status != 'T':
						break

			_return_to_start = FastestPath(self._explored_map, self._robot, True)#, self._real_map, self._surface)
			_status = _return_to_start.do_fastest_path(Attribute.START_POS.value)

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


		self.calibration_mode = True
		if self.can_calibrate_on_spot(self._robot.get_ori()):
			self.last_calibrate = 0
			self.move_robot(Action.CALIBRATE)
			if self.can_calibrate_on_spot(Orientation.getPrev(self._robot.get_ori())):
				self.calibrate(Orientation.getPrev(self._robot.get_ori()))
			elif self.can_calibrate_on_spot(Orientation.getNext(self._robot.get_ori())):
				self.calibrate(Orientation.getNext(self._robot.get_ori()))
		else:
			_target_calibrate = self.get_calibrate_ori()
			if _target_calibrate is not None:
				self.last_calibrate = 0
				self.calibrate(_target_calibrate)
		self.calibration_mode = False
		self.turn_robot(Orientation.NORTH.value)

		print("Exploration Completed!")
		area_explored = self.calculate_area_explored()
		print("{:0.2f}% Coverage".format(((area_explored / 300.0) * 100)))
		print("{} Blocks".format(area_explored))
		print("{} seconds".format((int(round(time.time() * 1000)) - self._start_time) / 1000))


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

	def can_calibrate_on_spot(self, ori):
		_pos = self._robot.get_pos()
		if ori == Orientation.NORTH.value:
			return self._explored_map.checkObstacleOrWall((_pos[0] - 2, _pos[1] - 1)) and self._explored_map.checkObstacleOrWall((_pos[0] - 2, _pos[1])) and self._explored_map.checkObstacleOrWall((_pos[0] - 2, _pos[1] + 1))
		elif ori == Orientation.EAST.value:
			return self._explored_map.checkObstacleOrWall((_pos[0] - 1, _pos[1] + 2)) and self._explored_map.checkObstacleOrWall((_pos[0], _pos[1] + 2)) and self._explored_map.checkObstacleOrWall((_pos[0] + 1, _pos[1] + 2))
		elif ori == Orientation.SOUTH.value:
			return self._explored_map.checkObstacleOrWall((_pos[0] + 2, _pos[1] - 1)) and self._explored_map.checkObstacleOrWall((_pos[0] + 2, _pos[1])) and self._explored_map.checkObstacleOrWall((_pos[0] + 2, _pos[1] + 1))
		elif ori == Orientation.WEST.value:
			return self._explored_map.checkObstacleOrWall((_pos[0] - 1, _pos[1] - 2)) and self._explored_map.checkObstacleOrWall((_pos[0], _pos[1] - 2)) and self._explored_map.checkObstacleOrWall((_pos[0] + 1, _pos[1] - 2))
		return False

	def get_calibrate_ori(self):
		_cur_ori = self._robot.get_ori()

		_check_ori = Orientation.getNext(_cur_ori)
		if self.can_calibrate_on_spot(_check_ori):
			return _check_ori

		_check_ori = Orientation.getPrev(_cur_ori)
		if self.can_calibrate_on_spot(_check_ori):
			return _check_ori

		_check_ori = Orientation.getPrev(_check_ori)
		if self.can_calibrate_on_spot(_check_ori):
			return _check_ori

	def calibrate(self, target_ori):
		_cur_ori = self._robot.get_ori()
		self.turn_robot(target_ori)
		self.move_robot(Action.CALIBRATE)#, self._explored_map, False)
		self.turn_robot(_cur_ori)

	def move_robot(self, action):
		print(action)
		if not self.calibration_mode:
			self._action_taken.append(action)
		self._robot.move(action)
		self._robot.notify_arduino(action.value)#, self._explored_map, True)

		#if self._surface is not None:
		#	self._explored_map.draw(self._surface)
		
		if action is not Action.CALIBRATE:# and not self.calibration_mode:
			self.sense_and_update()
			self._robot.notify_android(action.value, self._explored_map)
		else:
			_status = CommMgr.recv()
			print(_status)

		if self._robot.is_actual_robot() and not self.calibration_mode:
			self.calibration_mode = True

			if self.can_calibrate_on_spot(self._robot.get_ori()):
				self.last_calibrate = 0
				self.move_robot(Action.CALIBRATE)
				if self.can_calibrate_on_spot(Orientation.getPrev(self._robot.get_ori())):
					self.calibrate(Orientation.getPrev(self._robot.get_ori()))
				elif self.can_calibrate_on_spot(Orientation.getNext(self._robot.get_ori())):
					self.calibrate(Orientation.getNext(self._robot.get_ori()))
			else:
				_last_act = self._action_taken[len(self._action_taken) - 1]
				if _last_act == Action.UTURN:
					self.last_calibrate += 2
				else:
					self.last_calibrate += 1

				if self.last_calibrate >= 5:
					_target_calibrate = self.get_calibrate_ori()
					if _target_calibrate is not None:
						self.last_calibrate = 0
						self.calibrate(_target_calibrate)

			self.calibration_mode = False

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
			self.move_robot(Action.UTURN)
