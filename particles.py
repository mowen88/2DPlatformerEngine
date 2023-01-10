import pygame

class GunBlast(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups, path):
		super().__init__(groups)

		#self.sprite_type = sprite_type
		self.game = game
		self.zone = zone
		self.frames = self.game.import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.zone.player.hitbox.center)
	
	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames)-1:
			self.kill()
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()

		if self.zone.player.facing == 1:
			self.rect = self.image.get_rect(midleft = self.zone.player.hitbox.midright)
		else:
			self.image = pygame.transform.flip(self.image, True, False)
			self.rect = self.image.get_rect(midright = self.zone.player.hitbox.midleft)
			

		


		
