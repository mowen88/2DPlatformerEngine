import pygame, csv, random

class Camera(pygame.sprite.Group):
	def __init__(self, game, zone):
		super().__init__()
		self.game = game
		self.zone = zone
		self.surf = pygame.display.get_surface()
		
		self.fog_colour = self.game.BLUE
		self.fog_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		
		self.light_mask = pygame.image.load('imgs/white_gradient.png').convert_alpha()
		self.light_mask = pygame.transform.scale(self.light_mask, (700, 700))
		self.light_rect = self.light_mask.get_rect()
		self.dark = True

		self.zone_size = self.get_zone_size()

		self.offset = pygame.math.Vector2()
		self.cam_scroll_delay = 8

		self.bg0 = pygame.image.load(f'zones/{self.game.current_zone}/bg0.png').convert_alpha()
		self.bg0 = pygame.transform.scale(self.bg0, self.get_zone_size())
		self.bg1 = pygame.image.load(f'zones/{self.game.current_zone}/bg1.png').convert_alpha()
		self.bg1 = pygame.transform.scale(self.bg1, self.get_zone_size())
		self.bg2 = pygame.image.load(f'zones/{self.game.current_zone}/bg2.png').convert_alpha()
		self.bg2 = pygame.transform.scale(self.bg2, self.get_zone_size())
		self.bg3 = pygame.image.load(f'zones/{self.game.current_zone}/bg3.png').convert_alpha()
		self.bg3 = pygame.transform.scale(self.bg3, self.get_zone_size())

		self.bg_scroll = 0
		self.bg_scroll_speed = 4
		self.scrolling_bg_surf = pygame.transform.scale(self.bg1, self.get_zone_size())

	def get_zone_size(self):
		with open(f'zones/{self.game.current_zone}/{self.game.current_zone}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		size = (cols * self.game.TILESIZE, rows * self.game.TILESIZE)

		return size

	def screenshake(self):
		if self.game.screen_shaking:
			self.offset[0] += random.randint(-2, 2)
			self.offset[1] += random.randint(-2, 2)

	def blur(self):
		pass

	def scrolling_background(self):
		self.surf.blit(self.scrolling_bg_surf,(self.bg_scroll - int(self.offset[0]), 0 - int(self.offset[1])))
		if self.bg_scroll < 0:
			self.surf.blit(self.scrolling_bg_surf,(self.get_zone_size()[0] + self.bg_scroll - int(self.offset[0]), 0 - int(self.offset[1])))
		if self.bg_scroll < -self.get_zone_size()[0]:
			self.bg_scroll = 0

	def render_fog(self, target):
		self.fog_surf.fill(self.fog_colour)
		self.light_rect.center = target
		self.fog_surf.blit(self.light_mask, self.light_rect)
		self.surf.blit(self.fog_surf, (0,0), special_flags = pygame.BLEND_MULT)

	def keyboard_control(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a]:
			self.offset[0] -= 4
		if keys[pygame.K_d]:
			self.offset[0] += 4
		if keys[pygame.K_w]:
			self.offset[1] -= 4
		if keys[pygame.K_s]:
			self.offset[1] += 4


	def offset_draw(self, target):
		self.keyboard_control()
		self.screenshake()

		self.surf.blit(self.bg3,(0 - self.offset[0], 0 - self.offset[1]))
		self.surf.blit(self.bg2,(0 - self.offset[0] * 0.3, 0 - self.offset[1] * 0.3))
		self.surf.blit(self.bg1,(0 - self.offset[0] * 0.2, 0 - self.offset[1] * 0.2))
		self.surf.blit(self.bg0,(0 - self.offset[0] * 0.1, 0 - self.offset[1] * 0.1))
		
		
		# self.scrolling_background()
		# self.scrolling_bg_surf.set_alpha(100)
		# self.bg_scroll -= self.bg_scroll_speed
		
		self.offset[1] += (target[1] - self.offset[1] - self.game.HEIGHT *0.5)/self.cam_scroll_delay
		self.offset[0] += (target[0] - self.offset[0] - self.game.WIDTH *0.5)/(self.cam_scroll_delay/self.game.ASPECT_RATIO)


		# keeps the camera within the outer bounds of the current room
		if self.offset[0] <= 0:
			self.offset[0] = 0
		elif self.offset[0] >= self.zone_size[0] - (self.game.WIDTH):
			self.offset[0] = self.zone_size[0] - (self.game.WIDTH)
		if self.offset[1] <= 0:
			self.offset[1] = 0
		elif self.offset[1] >= self.zone_size[1] - (self.game.HEIGHT):
			self.offset[1] = self.zone_size[1] - (self.game.HEIGHT)

		if self.dark:
			self.render_fog((target[0] - self.offset[0], target[1] - self.offset[1]))

		for sprite in self.sprites():
			offset = sprite.rect.topleft - self.offset
			self.surf.blit(sprite.image, offset)

		


		
			