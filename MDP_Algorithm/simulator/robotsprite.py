import pygame, sys
from pygame.locals import *

class RobotSprite(pygame.sprite.Sprite):


	def __init__(self, robot):
		pygame.sprite.Sprite.__init__(self)
		self._ori = [0, 270, 180, 90]
		self._robot = robot

		self.image = pygame.Surface((90, 90), pygame.SRCALPHA)
		self.image.fill((255,255,255,0)) 
		pygame.draw.circle(self.image, (0,0,0), (45, 45), 30, 0)
		pygame.draw.polygon(self.image, (153,0,0), [(45, 15), (30, 30), (60, 30)])
		self.rect = self.image.get_rect()
		self._tempimage = self.image

	def update(self):
		self.rect.center = (self._robot.get_pos()[1] * 30 + 15, self._robot.get_pos()[0] * 30 + 15)

		temp_center = self.rect.center
		self._angle = self._ori[self._robot.get_ori()]
		self.image = pygame.transform.rotate(self._tempimage, self._angle)
		self.rect = self.image.get_rect(center=temp_center)
