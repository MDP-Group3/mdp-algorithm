class Block:

	def __init__(self, pos):
		self._pos = pos
		self._isObstacle = False
		self._isVirtualWall = False
		self._isExplored = False

	def get_pos(self):
		return self._pos

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