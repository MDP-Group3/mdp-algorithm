from robot.robotconstant import Orientation, Action
from comm.comm import CommMgr
class Sensor():

	def __init__(self, s_range, s_pos, s_ori, s_id):
		self._range = s_range # Sensor Range -> (lower range, upper range)
		self._pos = s_pos # Sensor Position -> (row, col)
		self._ori = s_ori # Sensor Orientation
		self._id = s_id
		self._offset = 5

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
		if self._range[0] > 1:
			# First Block
			_block = (self._pos[0] + row_inc, self._pos[0] + col_inc)
			if explored_map.check_valid_coord(_block):
				if explored_map.get_block(_block).is_obstacle():
					return

			# Second Block
			_block = (_block[0] + row_inc, _block[1] + col_inc)
			if explored_map.check_valid_coord(_block):
				if explored_map.get_block(_block).is_obstacle():
					return

		for i in range(self._range[0], self._range[1] + 1):
			_pos = (self._pos[0] + (row_inc * i), self._pos[1] + (col_inc * i))

			if not explored_map.check_valid_coord(_pos):
				return i

			explored_map.get_block(_pos).set_explored(True)

			if real_map.get_block(_pos).is_obstacle():
				explored_map.set_obstacle(_pos, True)
				return i

		return -1

	def sense_real(self, explored_map, sensor_val): #, check=False):
		if self._ori == Orientation.NORTH.value:
			self.process_sensor_val2(explored_map, sensor_val, -1, 0)#, check)
		elif self._ori == Orientation.EAST.value:
			self.process_sensor_val2(explored_map, sensor_val, 0, 1)#, check)
		elif self._ori == Orientation.SOUTH.value:
			self.process_sensor_val2(explored_map, sensor_val, 1, 0)#, check)
		elif self._ori == Orientation.WEST.value:
			self.process_sensor_val2(explored_map, sensor_val, 0, -1)#, check)

	def process_sensor_val(self, explored_map, sensor_val, row_inc, col_inc, check):
		sensor_val = sensor_val + 10

		if len(self._id) == 4:
			if explored_map.check_valid_coord((self._pos[0] + row_inc, self._pos[1] + col_inc)):
				if self._id[3] == 'L' and (explored_map.get_block((self._pos[0] + row_inc, self._pos[1] + col_inc)).is_obstacle()):
					return

			if explored_map.check_valid_coord((self._pos[0] + (row_inc * 2), self._pos[1] + (col_inc * 2))):
				if self._id[3] == 'L' and (explored_map.get_block((self._pos[0] + (row_inc * 2), self._pos[1] + (col_inc * 2))).is_obstacle()):
					return

		for i in range(self._range[0], self._range[1] + 1):
			_pos = (self._pos[0] + (row_inc * i), self._pos[1] + (col_inc * i))

			if not explored_map.check_valid_coord(_pos):
				print('{} Processing End'.format(self._id))
				return

			if explored_map.get_block(_pos).is_obstacle(): #or explored_map.get_block(_pos).is_explored():
				print('{} Processing End'.format(self._id))
				return


			explored_map.get_block(_pos).set_explored(True)

			#if (sensor_val - 10) <= 9:
			#	return

			if (sensor_val // 10) == 2 and check:
				CommMgr.send(Action.FORWARD.value, CommMgr.ARDUINO)
				print('{} Moving Forward to check'.format(self._id))
				_sensor_str = CommMgr.recv().rstrip()
				_check = int(float(_sensor_str.split('-')[int(self._id[2])])) + 10
				print('{} check value: {}'.format(self._id, _check))
				if _check // 10 == 1:
					print('{} sets {} as OBSTACLE => Sensor Value: {}'.format(self._id, _pos, sensor_val))
					explored_map.set_obstacle(_pos, True)
					CommMgr.send(Action.BACKWARD.value, CommMgr.ARDUINO)
					print('{} Moving Backward'.format(self._id))
					CommMgr.recv()
					return
				else:
					print('{} sets {} as CLEARED => Sensor Value: {}'.format(self._id, _pos, sensor_val))
					CommMgr.send(Action.BACKWARD.value, CommMgr.ARDUINO)
					print('{} Moving Backward'.format(self._id))
					CommMgr.recv()
					continue

			if (sensor_val // 10) == i:
				print('{} sets {} as OBSTACLE => Sensor Value: {}'.format(self._id, _pos, sensor_val))
				explored_map.set_obstacle(_pos, True)
				return
			else:
				print('{} sets {} as CLEARED => Sensor Value: {}'.format(self._id, _pos, sensor_val))
				continue

	def process_sensor_val2(self, explored_map, sensor_val, row_inc, col_inc):
		# check if long sensor is blocked
		if self._range[0] == 3:
			if sensor_val % 10 != 0:
				return
			# First Block
			_block = (self._pos[0] + row_inc, self._pos[1] + col_inc)
			if explored_map.check_valid_coord(_block):
				if not explored_map.get_block(_block).is_explored():
					return
				else:
					if explored_map.get_block(_block).is_obstacle():
						return

			# Second Block
			_block = (_block[0] + row_inc, _block[1] + col_inc)
			if explored_map.check_valid_coord(_block):
				if not explored_map.get_block(_block).is_explored():
					return
				else:
					if explored_map.get_block(_block).is_obstacle():
						return



		# Compute block that can be checked
		_block_list = {}
		for i in range(self._range[0], self._range[1] + 1):
			_block = (self._pos[0] + row_inc * i, self._pos[1] + col_inc * i)
			if explored_map.check_valid_coord(_block):
				_block_list[i] = _block
				#if explored_map.get_block(_block).is_obstacle():
				#	break
				#if not explored_map.get_block(_block).is_explored():
				#	_block_list[i] = _block
				#if explored_map.get_block(_block).get_lastCheck() < 5:
				#	if explored_map.get_block(_block).get_obstacleCount() < 3:

		# check if block is obstacle, if obstacle, exit function as the robot is block
		print('{} => {}'.format(self._id, _block_list))
		for k, block in _block_list.items():
			explored_map.get_block(block).set_explored(True)
			explored_map.get_block(block).increment_lastCheck()
			if k == 1 and sensor_val < 10:
				#if not explored_map.get_block(block).is_obstacle():
				explored_map.get_block(block).increment_obstacleCount()
				if explored_map.get_block(block).get_obstacleCount() < 3:
					explored_map.set_obstacle(block, True)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, True, sensor_val))
				return
			elif k == 2 and sensor_val == 10:
				#if not explored_map.get_block(block).is_obstacle():
				explored_map.get_block(block).increment_obstacleCount()
				if explored_map.get_block(block).get_obstacleCount() < 3:
					explored_map.set_obstacle(block, True)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, True, sensor_val))
				return
			elif k == 3 and sensor_val == 20:
				#if not explored_map.get_block(block).is_obstacle():
				explored_map.get_block(block).increment_obstacleCount()
				if explored_map.get_block(block).get_obstacleCount() < 3:
					explored_map.set_obstacle(block, True)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, True, sensor_val))
				return
			elif k == 4 and sensor_val == 30:
				#if not explored_map.get_block(block).is_obstacle():
				explored_map.get_block(block).increment_obstacleCount()
				if explored_map.get_block(block).get_obstacleCount() < 3:
					explored_map.set_obstacle(block, True)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, True, sensor_val))
				return
			elif k == 5 and sensor_val == 40:
				#if not explored_map.get_block(block).is_obstacle():
				explored_map.get_block(block).increment_obstacleCount()
				if explored_map.get_block(block).get_obstacleCount() < 3:
					explored_map.set_obstacle(block, True)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, True, sensor_val))
				return
			else:
				if explored_map.get_block(block).is_obstacle():
					explored_map.set_obstacle(block, False)
					explored_map.reset_virtualwall()
					print('{} sets {} as {} => Sensor Value: {}'.format(self._id, block, False, sensor_val))