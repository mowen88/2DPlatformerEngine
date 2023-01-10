import pygame

class UI:
	def __init__(self, game, zone):

		self.game = game
		self.zone = zone

		self.square_size = self.game.TILESIZE
	
		self.ammo_icon_img = pygame.image.load('imgs/ui/ammo_icon.png').convert_alpha()
		self.ammo_bar_img = pygame.image.load('imgs/ui/ammo_bar.png').convert_alpha()
		self.coin_icon_img = pygame.image.load('imgs/ui/coin_icon.png').convert_alpha()
		self.shield_icon = pygame.image.load('imgs/ui/shield_icon.png').convert_alpha()
		self.shield_bar = pygame.Surface((self.shield_icon.get_width(), self.shield_icon.get_height()))
		# self.shield_bar.fill(self.game.LIGHT_BLUE)
		# self.shield_bar_rect = self.shield_bar.get_rect()


		self.pos = (0, self.game.HEIGHT * 0.05)
	
	def return_health(self):
		return self.game.current_health

	def got_shield(self, colour):
		return self.game.data['items'].count(f'{colour}_shield')

	def coin_display(self):
		self.coin_text_img = self.game.font.render(str(self.game.data['coins']), True, self.game.WHITE)
		self.game.screen.blit(self.coin_icon_img, (self.game.WIDTH - self.coin_icon_img.get_width(), self.game.HEIGHT - (self.coin_icon_img.get_height() * 2)))
		self.game.screen.blit(self.coin_text_img, (self.game.WIDTH - self.coin_icon_img.get_width() * 0.55, self.game.HEIGHT - (self.coin_icon_img.get_height() * 2.1)))

	def health_display(self):

		offset = self.game.TILESIZE * 1.1

		for box in range(self.game.data['max_health'] + self.got_shield('blue') + self.got_shield('green')):
			if box < self.game.data['max_health']:
				box *= offset
				pygame.draw.rect(self.game.screen, self.game.BLACK, (self.pos[0] + box + offset, self.pos[1], self.square_size, self.square_size), 3, border_radius = 2)
				
				for box in range(self.game.current_health):
					box *= offset
					pygame.draw.rect(self.game.screen, self.game.WHITE, (self.pos[0] + box + offset + 3, self.pos[1] + 3, self.square_size - 6, self.square_size - 6))

			elif box < self.game.data['max_health'] + 1:
				box *= offset
				pygame.draw.rect(self.game.screen, self.game.BLACK, (self.pos[0] + box + offset, self.pos[1], self.square_size, self.square_size), 3, border_radius = 2)
				shield_ratio = int((self.game.blue_shield / 100) * (self.square_size - 6))
				pygame.draw.rect(self.game.screen, self.game.LIGHT_BLUE, (self.pos[0] + box + offset + 3, self.pos[1] + self.square_size - 3 - shield_ratio, self.square_size - 6, shield_ratio))
				
			else:
				box *= offset
				pygame.draw.rect(self.game.screen, self.game.BLACK, (self.pos[0] + box + offset, self.pos[1], self.square_size, self.square_size), 3, border_radius = 2)
				shield_ratio = int((self.game.green_shield / 100) * (self.square_size - 6))
				pygame.draw.rect(self.game.screen, self.game.LIGHT_GREEN, (self.pos[0] + box + offset + 3, self.pos[1] + self.square_size - 3 - shield_ratio, self.square_size - 6, shield_ratio))
	
	
	def stamina_display(self):
		offset = 2
		stamina_bar = pygame.Rect((self.square_size, self.pos[1] * 0.4, 100 + (offset * 2), offset * 3))
		pygame.draw.rect(self.game.screen, self.game.BLACK, (stamina_bar))
		pygame.draw.rect(self.game.screen, self.game.WHITE, (stamina_bar[0] + offset, stamina_bar[1] + offset, (self.game.stamina), stamina_bar.height - offset * 2))


	def ammo_display(self):
		offset = self.game.TILESIZE * 0.5
		for box in range(self.game.data['max_bullets']):
			box *= offset
			self.game.screen.blit(self.ammo_bar_img, (box + offset + offset, self.pos[1] * 2.5))
		for box in range(self.game.current_bullets):
			box *= offset
			self.game.screen.blit(self.ammo_icon_img, (box + offset + offset, self.pos[1] * 2.5))

		
	def render(self):
		self.stamina_display()
		self.health_display()
		#self.coin_display()
		self.ammo_display()


