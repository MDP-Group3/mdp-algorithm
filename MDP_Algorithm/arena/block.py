class Block:

	def __init__(self, pos):
		self._pos = pos
		self._isObstacle = False
		self._isVirtualWall = False
		self._isExplored = False
		self._isWaypoint = False
		self._lastCheck = 0

	def get_pos(self):
		return self._pos

	def get_lastCheck(self):
		return self._lastCheck

	def increment_lastCheck(self):
		self._lastCheck = self._lastCheck + 1

	def set_obstacle(self, obstacle):
		self._isObstacle = obstacle

	def is_obstacle(self):
		return self._isObstacle

	def set_virtualwall(self, virtualwall):
		self._isVirtualWall = virtualwall

	def is_virtualwall(self):
		return self._isVirtualWall

	def set_explored(self, explored):
		self._isExplored = explored

	def is_explored(self):
		return self._isExplored

	def set_waypoint(self, waypoint):
		self._isWaypoint = waypoint

	def is_waypoint(self):
		return self._isWaypoint