import pygame

class Background(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, img):
		self.game = game
		self.zone = zone
		self.image = pygame.image.load(img).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.game.WIDTH * self.game.SCALE, self.game.HEIGHT * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.vel = pygame.math.Vector2()