from arena.arenaconstant import ArenaConstant
from arena.arenautils import ArenaUtils
from robot.robotconstant import Orientation, Attribute, Action, SensorRange
from robot.sensor import Sensor
from comm.comm import CommMgr
from multiprocessing import Process

class Robot:

	def __init__(self, pos, actualRobot):
		self._pos = pos # Robot Start Position -> (row, col)
		self._ori = Attribute.START_ORI.value # Robot Start Orientation 
		self._speed = Attribute.SPEED.value # Robot Speed

		self._actualRobot = actualRobot # Simulated or Real Robot

		self._LSRightCenter = Sensor(SensorRange.LONG_RANGE.value, (self._pos[0], self._pos[1] + 1), Orientation.EAST.value, 'RC0L') # Left-facing Center Short Range Sensor
		self._SSLeftTop = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] - 1), Orientation.WEST.value, 'LT1') # Left-facing Top Short Range Sensor
		self._SSFrontLeft = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] - 1), Orientation.NORTH.value, 'FL2') # Front-facing Left Short Range Sensor
		self._SSFrontCenter = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1]), Orientation.NORTH.value, 'FC3') # Front-facing Center Long Range Sensor
		self._SSFrontRight = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] + 1), Orientation.NORTH.value, 'FR4') # Front-facing Right Short Range Sensor
		self._SSRightTop = Sensor((1,3), (self._pos[0] - 1, self._pos[1] + 1), Orientation.EAST.value, 'RT5') # Right-facing Center Short Range Sensor

		self._reachedGoal = False # If Robot reached goal

	def set_pos(self, row, col):
		self._pos = (row, col)

	def get_pos(self):
		return self._pos

	def set_ori(self, ori):
		self._ori = ori

	def get_ori(self):
		return self._ori

	def set_speed(self, speed):
		self._speed = speed

	def get_speed(self):
		return self._speed

	def is_actual_robot(self):
		return self._actualRobot

	def set_reachedGoal(self):
		if self._pos == ArenaConstant.GOAL_POS.value:
			self._reachedGoal = True

	def get_reachedGoal(self):
		return self._reachedGoal
	
	def getNewOrientation(self, action):
		if action == Action.RIGHT:
			return Orientation.getNext(self._ori)
		elif action == Action.LEFT:
			return Orientation.getPrev(self._ori)
		elif action == Action.UTURN:
			return Orientation.getOpp(self._ori)

	def move(self, action):
		if action == Action.FORWARD:
			if self._ori == Orientation.NORTH.value:
				self._pos = (self._pos[0] - 1, self._pos[1])
			elif self._ori == Orientation.EAST.value:
				self._pos = (self._pos[0], self._pos[1] + 1)
			elif self._ori == Orientation.SOUTH.value:
				self._pos = (self._pos[0] + 1, self._pos[1])
			elif self._ori == Orientation.WEST.value:
				self._pos = (self._pos[0], self._pos[1] - 1)
		elif action == Action.BACKWARD:
			if self._ori == Orientation.NORTH.value:
				self._pos = (self._pos[0] + 1, self._pos[1])
			elif self._ori == Orientation.EAST.value:
				self._pos = (self._pos[0], self._pos[1] - 1)
			elif self._ori == Orientation.SOUTH.value:
				self._pos = (self._pos[0] - 1, self._pos[1])
			elif self._ori == Orientation.WEST.value:
				self._pos = (self._pos[0], self._pos[1] + 1)
		elif action == Action.RIGHT or action == Action.LEFT or action == Action.UTURN:
			self._ori = self.getNewOrientation(action)

		self.set_reachedGoal()

	def move_multiple(self, count):
		if count == 1:
			self.move(Action.FORWARD)
		else:
			if self._ori == Orientation.NORTH.value:
				self._pos = (self._pos[0] - count, self._pos[1])
			elif self._ori == Orientation.EAST.value:
				self._pos = (self._pos[0], self._pos[1] + count)
			elif self._ori == Orientation.SOUTH.value:
				self._pos = (self._pos[0] + count, self._pos[1])
			elif self._ori == Orientation.WEST.value:
				self._pos = (self._pos[0], self._pos[1] - count)

	def set_sensor(self):
		if self._ori == Orientation.NORTH.value:
			self._SSFrontLeft.set_sensor((self._pos[0] - 1, self._pos[1] - 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0] - 1, self._pos[1]), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] - 1, self._pos[1] + 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] - 1, self._pos[1] - 1), Orientation.WEST.value)
			self._SSRightTop.set_sensor((self._pos[0] - 1, self._pos[1] + 1), Orientation.EAST.value)
			self._LSRightCenter.set_sensor((self._pos[0], self._pos[1] + 1), Orientation.EAST.value)
		elif self._ori == Orientation.EAST.value:
			self._SSFrontLeft.set_sensor((self._pos[0] - 1, self._pos[1] + 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0], self._pos[1] + 1), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] + 1, self._pos[1] + 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] - 1, self._pos[1] + 1), Orientation.NORTH.value)
			self._SSRightTop.set_sensor((self._pos[0] + 1, self._pos[1] + 1), Orientation.SOUTH.value)
			self._LSRightCenter.set_sensor((self._pos[0] + 1, self._pos[1]), Orientation.SOUTH.value)
		elif self._ori == Orientation.SOUTH.value:
			self._SSFrontLeft.set_sensor((self._pos[0] + 1, self._pos[1] + 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0] + 1, self._pos[1]), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] + 1, self._pos[1] - 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] + 1, self._pos[1] + 1), Orientation.EAST.value)
			self._SSRightTop.set_sensor((self._pos[0] + 1, self._pos[1] - 1), Orientation.WEST.value)
			self._LSRightCenter.set_sensor((self._pos[0], self._pos[1] - 1), Orientation.WEST.value)
		elif self._ori == Orientation.WEST.value:
			self._SSFrontLeft.set_sensor((self._pos[0] + 1, self._pos[1] - 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0], self._pos[1] - 1), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] - 1, self._pos[1] - 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] + 1, self._pos[1] - 1), Orientation.SOUTH.value)
			self._SSRightTop.set_sensor((self._pos[0] - 1, self._pos[1] - 1), Orientation.NORTH.value)
			self._LSRightCenter.set_sensor((self._pos[0] - 1, self._pos[1]), Orientation.NORTH.value)

	def sense(self, explored_map, real_map=None):
		result = [None for x in range(6)]

		# if not self._actualRobot:
		# 	result[0] = self._SSFrontLeft.sense(explored_map, real_map)
		# 	result[1] = self._SSFrontCenter.sense(explored_map, real_map)
		# 	result[2] = self._SSFrontRight.sense(explored_map, real_map)
		# 	result[3] = self._SSLeftTop.sense(explored_map, real_map)
		# 	result[4] = self._LSRightCenter.sense(explored_map, real_map)
		# 	result[5] = self._SSRightTop.sense(explored_map, real_map)
		# else:
		_sensor_str = CommMgr.recv().rstrip()
		print(_sensor_str)
		result = _sensor_str.split('-')
		for i in range(len(result)):
			if result[i] == '':
				result[i] = 0
			else:
				result[i] = int(float(result[i]))

		self._LSRightCenter.sense_real(explored_map, result[0])#, (10 <= result[0] < 20 and 10 <= result[1] < 20))
		self._SSLeftTop.sense_real(explored_map, result[1])#, (10 <= result[0] < 20 and 10 <= result[1] < 20))
		self._SSFrontLeft.sense_real(explored_map, result[2])#, (10 <= result[2] < 20 and 10 <= result[3] < 20 and 10 <= result[4] < 20))
		self._SSFrontCenter.sense_real(explored_map, result[3])#, (10 <= result[2] < 20 and 10 <= result[3] < 20 and 10 <= result[4] < 20))
		self._SSFrontRight.sense_real(explored_map, result[4])#, (10 <= result[2] < 20 and 10 <= result[3] < 20 and 10 <= result[4] < 20))
		self._SSRightTop.sense_real(explored_map, result[5])#, (10 <= result[5] < 20))
		return result

	def notify_android(self, action, explored_map):
		if self._actualRobot and action != Action.CALIBRATE:
			ArenaUtils.generate_arena_descriptor(explored_map)
			_ex_mdf = ArenaUtils.hex_string('map/generated/MapExplored.txt')
			_obs_mdf = ArenaUtils.hex_string('map/generated/MapObstacle.txt')

			_pos = str(self._pos[0]).zfill(2) + str(self._pos[1]).zfill(2)
			_to_android = "***{},{},{}:{}:{}".format(_pos, Orientation.getText(self._ori), action, _ex_mdf, _obs_mdf)
			CommMgr.send(_to_android, CommMgr.ANDROID)
			#while CommMgr.recv() != 'ACK':
			#	continue

	def notify_arduino(self, action):
		if self._actualRobot:
			#if isinstance(action, str):
			#	CommMgr.send(action, CommMgr.ARDUINO)
			#else:
			CommMgr.send(action, CommMgr.ARDUINO)
			# if action.value != 'd':
			# 	while True:
			# 		_ack = CommMgr.recv().rstrip()
			# 		if _ack == 'X':
			# 			break;

	def notify(self, action, explored_map, to_android):
		if self._actualRobot:
			# _p2 = Process(target=self.notify_arduino(action))
			# _p2.start()
			# _p2.join()
			self.notify_arduino(action)

			if to_android:
			# 	_p1 = Process(target=self.notify_android(action, explored_map))
			# 	_p1.start()
			# 	_p1.join()
				self.notify_android(action, explored_map)