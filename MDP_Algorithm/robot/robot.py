from arena.arenaconstant import ArenaConstant
from robot.robotconstant import Orientation, Attribute, Action, SensorRange
from robot.sensor import Sensor

class Robot:

	def __init__(self, pos, actualRobot):
		self._pos = pos # Robot Start Position -> (row, col)
		self._ori = Attribute.START_ORI.value # Robot Start Orientation 
		self._speed = Attribute.SPEED.value # Robot Speed

		self._actualRobot = actualRobot # Simulated or Real Robot

		self._SSFrontLeft = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] - 1), Orientation.NORTH.value) # Front-facing Left Short Range Sensor
		self._SSFrontCenter = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1]), Orientation.NORTH.value) # Front-facing Center Long Range Sensor
		self._SSFrontRight = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] + 1), Orientation.NORTH.value) # Front-facing Right Short Range Sensor
		self._SSLeftTop = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] - 1), Orientation.WEST.value) # Left-facing Top Short Range Sensor
		self._LSLeftCenter = Sensor(SensorRange.LONG_RANGE.value, (self._pos[0], self._pos[1] - 1), Orientation.WEST.value) # Left-facing Center Short Range Sensor
		self._SSRightTop = Sensor(SensorRange.SHORT_RANGE.value, (self._pos[0] - 1, self._pos[1] + 1), Orientation.EAST.value) # Right-facing Center Short Range Sensor

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
		elif action == Action.RIGHT or action == Action.LEFT:
			self._ori = self.getNewOrientation(action)

		self.set_reachedGoal()


	def set_sensor(self):
		if self._ori == Orientation.NORTH.value:
			self._SSFrontLeft.set_sensor((self._pos[0] - 1, self._pos[1] - 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0] - 1, self._pos[1]), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] - 1, self._pos[1] + 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] - 1, self._pos[1] - 1), Orientation.WEST.value)
			self._LSLeftCenter.set_sensor((self._pos[0], self._pos[1] - 1), Orientation.WEST.value)
			self._SSRightTop.set_sensor((self._pos[0] - 1, self._pos[1] + 1), Orientation.EAST.value)
		elif self._ori == Orientation.EAST.value:
			self._SSFrontLeft.set_sensor((self._pos[0] - 1, self._pos[1] + 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0], self._pos[1] + 1), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] + 1, self._pos[1] + 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] - 1, self._pos[1] + 1), Orientation.NORTH.value)
			self._LSLeftCenter.set_sensor((self._pos[0] - 1, self._pos[1]), Orientation.NORTH.value)
			self._SSRightTop.set_sensor((self._pos[0] + 1, self._pos[1] + 1), Orientation.SOUTH.value)
		elif self._ori == Orientation.SOUTH.value:
			self._SSFrontLeft.set_sensor((self._pos[0] + 1, self._pos[1] + 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0] + 1, self._pos[1]), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] + 1, self._pos[1] - 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] + 1, self._pos[1] + 1), Orientation.EAST.value)
			self._LSLeftCenter.set_sensor((self._pos[0], self._pos[1] + 1), Orientation.EAST.value)
			self._SSRightTop.set_sensor((self._pos[0] + 1, self._pos[1] - 1), Orientation.WEST.value)
		elif self._ori == Orientation.WEST.value:
			self._SSFrontLeft.set_sensor((self._pos[0] + 1, self._pos[1] - 1), self._ori)
			self._SSFrontCenter.set_sensor((self._pos[0], self._pos[1] - 1), self._ori)
			self._SSFrontRight.set_sensor((self._pos[0] - 1, self._pos[1] - 1), self._ori)
			self._SSLeftTop.set_sensor((self._pos[0] + 1, self._pos[1] - 1), Orientation.SOUTH.value)
			self._LSLeftCenter.set_sensor((self._pos[0] + 1, self._pos[1]), Orientation.SOUTH.value)
			self._SSRightTop.set_sensor((self._pos[0] - 1, self._pos[1] - 1), Orientation.NORTH.value)

	def sense(self, explored_map, real_map):
		result = [None for x in range(6)]

		result[0] = self._SSFrontLeft.sense(explored_map, real_map)
		result[1] = self._SSFrontCenter.sense(explored_map, real_map)
		result[2] = self._SSFrontRight.sense(explored_map, real_map)
		result[3] = self._SSLeftTop.sense(explored_map, real_map)
		result[4] = self._LSLeftCenter.sense(explored_map, real_map)
		result[5] = self._SSRightTop.sense(explored_map, real_map)

		return result