from enum import Enum

class Orientation(Enum):
	NORTH = 0
	EAST = 1
	SOUTH = 2
	WEST = 3

	@classmethod
	def getNext(cls, cur_ori):
		return (cur_ori + 1) % 4

	@classmethod
	def getPrev(cls, cur_ori):
		return (cur_ori + 3) % 4

	@classmethod
	def getOpp(cls, cur_ori):
		return (cur_ori + 2) % 4

	@classmethod
	def getText(cls, ori):
		if ori == 0:
			return 'N'
		elif ori == 1:
			return 'E'
		elif ori == 2:
			return 'S'
		elif ori == 3:
			return 'W'

class Attribute(Enum):
	START_POS = (18, 1)
	START_ORI = Orientation.NORTH.value
	MOVE_COST = 10
	TURN_COST = 20
	INFINITE_COST = 9999
	SPEED = 100

class Action(Enum):
	FORWARD = 'F'
	BACKWARD = 'B'
	RIGHT = 'R'
	LEFT = 'L'
	UTURN = 'U'
	CALIBRATE = 'C'
	ERROR = 'E'
	SENSOR = 'd'

class SensorRange(Enum):
	SHORT_RANGE = (1, 2) # Range of short range sensor -> (lower range, upper range)
	LONG_RANGE = (3, 5) # Range of long range sensor -> (lower range, upper range)