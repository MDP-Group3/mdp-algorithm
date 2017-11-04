from arena.arena import Arena
from arena.arenaconstant import ArenaConstant

class ArenaUtils:
	@staticmethod
	def load_arena_from_file(arena, filename):
		with open(filename, 'r') as file:
			content = file.readlines()

		content = [list(line.strip()) for line in content]
		content = list(reversed(content))

		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if int(content[row][col]) == 1:
					arena.set_obstacle((row, col), True)

		arena.set_allexplored()

	@staticmethod
	def bin_to_hex(string):
		output = ''
		while string:
			input_string = string[:4]
			hex_value = format(int(input_string, 2), 'x')
			output += hex_value
			string = string[4:]

		return output

	@staticmethod
	def hex_string(filename):
		with open(filename, 'r') as file:
			content = file.readlines()

		for i in range(len(content)-1):
			content[i] = content[i].rstrip()
		hex_val = ""
		hex_val = ''.join(content)
		hex_val = ArenaUtils.bin_to_hex(hex_val)
		return hex_val


	@staticmethod
	def generate_arena_descriptor(arena):
		s = ""
		exploredArea = []
		exploredArea.append("11")
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if arena.get_block((row, col)).is_explored():
					s += "1"
				else:
					s += "0"
			exploredArea.append(s)
			s = ""
		exploredArea.append("11")
		exploredArea.reverse()

		with open('map/generated/MapExplored.txt', 'w') as file:
			file.writelines("\n".join(exploredArea))

		s = ""
		num = 0
		obstacleArea = []
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if arena.get_block((row, col)).is_explored():
					if arena.get_block((row,col)).is_obstacle():
						s += "1"
						num += 1
					else:
						s += "0"
						num += 1
			obstacleArea.append(s)
			s = ""
		padding = 8 - (num % 8)
		s = "0" * padding
		obstacleArea.append(s)
		obstacleArea.reverse()

		with open('map/generated/MapObstacle.txt', 'w') as file:
			file.writelines("\n".join(obstacleArea))

		s = ""
		num = 0
		virtualobstacleArea = []
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if arena.get_block((row, col)).is_explored():
					if arena.get_block((row,col)).is_obstacle():
						s += "1"
						num += 1
					elif arena.get_block((row,col)).is_virtualwall():
						s += "2"
						num += 1
					else:
						s += "0"
						num += 1
			virtualobstacleArea.append(s)
			s = ""
		padding = 8 - (num % 8)
		s = "0" * padding
		virtualobstacleArea.append(s)
		virtualobstacleArea.reverse()

		with open('map/generated/MapObstacleVirtual.txt', 'w') as file:
			file.writelines("\n".join(virtualobstacleArea))

		#ArenaUtils.hex_string('map/generated/MapExplored.txt')
		#ArenaUtils.hex_string('map/generated/MapObstacle.txt')
