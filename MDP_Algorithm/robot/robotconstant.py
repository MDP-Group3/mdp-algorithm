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
	CALIBRATE = 'C'
	ERROR = 'E'

class SensorRange(Enum):
	SHORT_RANGE = (1, 2) # Range of short range sensor -> (lower range, upper range)
	LONG_RANGE = (2, 5) # Range of long range sensor -> (lower range, upper range)