from robot.robotconstant import Orientation
class Sensor():

	def __init__(self, s_range, s_pos, s_ori):
		self._range = s_range # Sensor Range -> (lower range, upper range)
		self._pos = s_pos # Sensor Position -> (row, col)
		self._ori = s_ori # Sensor Orientation

	def set_sensor(self, pos, ori):
		self._pos = pos
		self._ori = ori

	def sense(self, explored_map, real_map):
		if self._ori == Orientation.NORTH.value:
			return self.get_sensor_val(explored_map, real_map, -1, 0)
		elif self._ori == Orientation.EAST.value:
			return self.get_sensor_val(explored_map, real_map, 0, 1)
		elif self._ori == Orientation.SOUTH.value:
			return self.get_sensor_val(explored_map, real_map, 1, 0)
		elif self._ori == Orientation.WEST.value:
			return self.get_sensor_val(explored_map, real_map, 0, -1)
		return -1

	def get_sensor_val(self, explored_map, real_map, row_inc, col_inc):
		for i in range(self._range[0], self._range[1] + 1):
			_pos = (self._pos[0] + (row_inc * i), self._pos[1] + (col_inc * i))

			if not explored_map.check_valid_coord(_pos):
				return i

			if self._range[0] > 1 and explored_map.get_block((self._pos[0] + row_inc, self._pos[1] + col_inc)).is_obstacle():
				return -1

			explored_map.get_block(_pos).set_explored(True)

			if real_map.get_block(_pos).is_obstacle():
				explored_map.set_obstacle(_pos, True)
				return i

		return -1

	