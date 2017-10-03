import pygame, sys, copy
from pygame.locals import *
from arena.arena import Arena
from arena.arenaconstant import ArenaConstant
from arena.arenautils import ArenaUtils
from robot.robot import Robot
from robot.robotconstant import Orientation, Attribute, Action, SensorRange
from simulator.robotsprite import RobotSprite
from algorithm.exploration import Exploration
from algorithm.fastestpath import FastestPath

class Simulator:

	def __init__(self):
		pygame.init()

	def init_objects(self, robot, map_file):
		self._robot = copy.deepcopy(robot)
		self._real_map = Arena(self._robot)
		ArenaUtils.load_arena_from_file(self._real_map, map_file)

		self._explore_map = Arena(self._robot)
		self._explore_map.set_allunexplored()

		self.BLOCK_SIZE = 30

		# Simulator Main Window
		self._arena_size = (ArenaConstant.ARENA_COL.value * self.BLOCK_SIZE, ArenaConstant.ARENA_ROW.value * self.BLOCK_SIZE)
		self._screen = pygame.display.set_mode((self._arena_size[0] * 2, self._arena_size[1]))
		self._screen.fill((0,0,0))

		# Simulator Background
		self._background = pygame.Surface(self._arena_size)
		self._background = self._background.convert()
		self._background.fill((169,169,169))

		# Simulator Background
		self._menu = pygame.Surface(self._arena_size)
		self._menu = self._menu.convert()
		self._menu.fill((255,255,255))

		# Prepare Background and Arena
		for row in range(ArenaConstant.ARENA_ROW.value):
			for col in range(ArenaConstant.ARENA_COL.value):
				if row == 17 and col == 0 :
					pygame.draw.rect(self._background, (0,100,0), (col * self.BLOCK_SIZE , row * self.BLOCK_SIZE, self.BLOCK_SIZE * 3, self.BLOCK_SIZE * 3))

				if row == 0 and col == 12 :
					pygame.draw.rect(self._background, (255,140,0), (col * self.BLOCK_SIZE , row * self.BLOCK_SIZE, self.BLOCK_SIZE * 3, self.BLOCK_SIZE * 3))

				pygame.draw.rect(self._background, (0,0,0), (col * self.BLOCK_SIZE, row * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)

		# Simulator Menu
		self._large_text = pygame.font.Font('freesansbold.ttf',20)
		self._coverage_ex_menu_surf, self._coverage_ex_menu_rect = self.text_objects("Coverage-Limited Exploration", self._large_text)
		self._coverage_ex_menu_rect.center = ((self._arena_size[0] / 2, 3 * self._arena_size[1] / 6))
		self._coverage_rect = pygame.Rect(self._coverage_ex_menu_rect.left - 15, self._coverage_ex_menu_rect.top - 15, self._coverage_ex_menu_rect.width + self.BLOCK_SIZE, self._coverage_ex_menu_rect.height + self.BLOCK_SIZE)
		pygame.draw.rect(self._menu, (0,0,0), self._coverage_rect, 3)
		self._menu.blit(self._coverage_ex_menu_surf, self._coverage_ex_menu_rect)

		self._ex_menu_surf, self._ex_menu_rect = self.text_objects("Exploration", self._large_text)
		self._ex_menu_rect.center = ((self._arena_size[0] / 2, self._arena_size[1] / 6))
		self._ex_rect = pygame.Rect.copy(self._coverage_rect)
		self._ex_rect.center = self._ex_menu_rect.center
		pygame.draw.rect(self._menu, (0,0,0), self._ex_rect, 3)
		self._menu.blit(self._ex_menu_surf, self._ex_menu_rect) 

		self._timed_ex_menu_surf, self._timed_ex_menu_rect = self.text_objects("Timed Exploration", self._large_text)
		self._timed_ex_menu_rect.center = ((self._arena_size[0] / 2, 2 * self._arena_size[1] / 6))
		self._timed_rect = pygame.Rect.copy(self._coverage_rect)
		self._timed_rect.center = self._timed_ex_menu_rect.center
		pygame.draw.rect(self._menu, (0,0,0), self._timed_rect, 3)
		self._menu.blit(self._timed_ex_menu_surf, self._timed_ex_menu_rect) 


		self._fp_menu_surf, self._fp_menu_rect = self.text_objects("Fastest Path", self._large_text)
		self._fp_menu_rect.center = ((self._arena_size[0] / 2, 4 * self._arena_size[1] / 6))
		self._fp_rect = pygame.Rect.copy(self._coverage_rect)
		self._fp_rect.center = self._fp_menu_rect.center
		pygame.draw.rect(self._menu, (0,0,0), self._fp_rect, 3)
		self._menu.blit(self._fp_menu_surf, self._fp_menu_rect) 

		self._mdf_menu_surf, self._mdf_menu_rect = self.text_objects("Generate MDF", self._large_text)
		self._mdf_menu_rect.center = ((self._arena_size[0] / 2, 5 * self._arena_size[1] / 6))
		self._mdf_rect = pygame.Rect.copy(self._coverage_rect)
		self._mdf_rect.center = self._mdf_menu_rect.center
		pygame.draw.rect(self._menu, (0,0,0), self._mdf_rect, 3)
		self._menu.blit(self._mdf_menu_surf, self._mdf_menu_rect) 

		self._screen.blit(self._background, (0,0))
		self._screen.blit(self._menu, (ArenaConstant.ARENA_COL.value * self.BLOCK_SIZE,0))
		pygame.display.update()

	def text_objects(self, text, font):
		text_surface = font.render(text, True, (0,0,0))
		return text_surface, text_surface.get_rect()

	def get_key(self):
		while 1:
			event = pygame.event.poll()
			if event.type == KEYDOWN:
				return event.key
			else:
				pass

	def display_box(self, screen, message):
		"Print a message in a box in the middle of the screen"
		fontobject = pygame.font.Font(None,18)
		pygame.draw.rect(screen, (0,0,0), ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10, 200,20), 0)
		pygame.draw.rect(screen, (255,255,255), ((screen.get_width() / 2) - 102, (screen.get_height() / 2) - 12, 204,24), 1)
		if len(message) != 0:
			screen.blit(fontobject.render(message, 1, (255,255,255)), ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
		pygame.display.flip()

	def ask(self, screen, question):
		"ask(screen, question) -> answer"
		pygame.font.init()
		current_string = []
		self.display_box(screen, question + ": " + ''.join(current_string))
		while 1:
			inkey = self.get_key()
			if inkey == K_BACKSPACE:
				current_string = current_string[0:-1]
			elif inkey == K_RETURN:
				break
			elif inkey == K_MINUS:
				current_string.append("_")
			elif inkey <= 127:
				current_string.append(chr(inkey))
			self.display_box(screen, question + ": " + ''.join(current_string))
		return ''.join(current_string)

	def run_exploration(self, robot, map_file):
		self.init_objects(robot, map_file)

		while True:
			_mouse = pygame.mouse.get_pos()

			if 450 + self._ex_rect.left < _mouse[0] < 450 + self._ex_rect.right and self._ex_rect.top < _mouse[1] < self._ex_rect.bottom:
				pygame.draw.rect(self._menu, (255,0,0), self._ex_rect, 3)
			else:
				pygame.draw.rect(self._menu, (0,0,0), self._ex_rect, 3)

			if 450 + self._timed_rect.left < _mouse[0] < 450 + self._timed_rect.right and self._timed_rect.top < _mouse[1] < self._timed_rect.bottom:
				pygame.draw.rect(self._menu, (255,0,0), self._timed_rect, 3)
			else:
				pygame.draw.rect(self._menu, (0,0,0), self._timed_rect, 3)

			if 450 + self._coverage_rect.left < _mouse[0] < 450 + self._coverage_rect.right and self._coverage_rect.top < _mouse[1] < self._coverage_rect.bottom:
				pygame.draw.rect(self._menu, (255,0,0), self._coverage_rect, 3)
			else:
				pygame.draw.rect(self._menu, (0,0,0), self._coverage_rect, 3)

			if 450 + self._fp_rect.left < _mouse[0] < 450 + self._fp_rect.right and self._fp_rect.top < _mouse[1] < self._fp_rect.bottom:
				pygame.draw.rect(self._menu, (255,0,0), self._fp_rect, 3)
			else:
				pygame.draw.rect(self._menu, (0,0,0), self._fp_rect, 3)

			if 450 + self._mdf_rect.left < _mouse[0] < 450 + self._mdf_rect.right and self._mdf_rect.top < _mouse[1] < self._mdf_rect.bottom:
				pygame.draw.rect(self._menu, (255,0,0), self._mdf_rect, 3)
			else:
				pygame.draw.rect(self._menu, (0,0,0), self._mdf_rect, 3)

			self._screen.blit(self._menu, (ArenaConstant.ARENA_COL.value * self.BLOCK_SIZE,0))
			pygame.display.update()

			keys = pygame.key.get_pressed()
			for event in pygame.event.get():
				if event.type == QUIT or keys[pygame.K_ESCAPE]:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if 450 + self._ex_rect.left < _mouse[0] < 450 + self._ex_rect.right and self._ex_rect.top < _mouse[1] < self._ex_rect.bottom:
						self.init_objects(robot, map_file)
						_explore = Exploration(self._explore_map, self._real_map, self._robot, 300, 3600, (self._screen, self._background))
						_explore.run()
					elif 450 + self._fp_rect.left < _mouse[0] < 450 + self._fp_rect.right and self._fp_rect.top < _mouse[1] < self._fp_rect.bottom:
						_go_to_wp = FastestPath(self._explore_map, self._robot, self._real_map, (self._screen, self._background))
						_go_to_wp.do_fastest_path((11,13))
						_go_to_goal = FastestPath(self._explore_map, self._robot, self._real_map, (self._screen, self._background))
						_go_to_goal.do_fastest_path(ArenaConstant.GOAL_POS.value)
					elif 450 + self._timed_rect.left < _mouse[0] < 450 + self._timed_rect.right and self._timed_rect.top < _mouse[1] < self._timed_rect.bottom:
						self.init_objects(robot, map_file)
						_steps = self.ask(self._screen, "Enter Robot Speed")
						_speed = 1000 / int(_steps)
						self._robot.set_speed(int(_speed))
						_time_limit = self.ask(self._screen, "Enter Time Limit")
						
						self._screen.blit(self._background, (0,0))
						self._screen.blit(self._menu, (ArenaConstant.ARENA_COL.value * self.BLOCK_SIZE,0))
						pygame.display.update()
						
						_timed_explore = Exploration(self._explore_map, self._real_map, self._robot, 300, int(_time_limit), (self._screen, self._background))
						_timed_explore.run()
					elif 450 + self._coverage_rect.left < _mouse[0] < 450 + self._coverage_rect.right and self._coverage_rect.top < _mouse[1] < self._coverage_rect.bottom:
						self.init_objects(robot, map_file)
						_steps = self.ask(self._screen, "Enter Robot Speed")
						_speed = 1000 / int(_steps)
						self._robot.set_speed(int(_speed))
						_coverage_limit_percent = self.ask(self._screen, "Enter Coverage Limit %")
						_coverage_limit = (int(_coverage_limit_percent) / 100) * 300
						
						self._screen.blit(self._background, (0,0))
						self._screen.blit(self._menu, (ArenaConstant.ARENA_COL.value * self.BLOCK_SIZE,0))
						pygame.display.update()
						
						_timed_explore = Exploration(self._explore_map, self._real_map, self._robot, int(_coverage_limit), 3600, (self._screen, self._background))
						_timed_explore.run()
					elif 450 + self._mdf_rect.left < _mouse[0] < 450 + self._mdf_rect.right and self._mdf_rect.top < _mouse[1] < self._mdf_rect.bottom:
						ArenaUtils.generate_arena_descriptor(self._explore_map)
						print(ArenaUtils.hex_string('map/generated/MapExplored.txt'))
						print(ArenaUtils.hex_string('map/generated/MapObstacle.txt'))