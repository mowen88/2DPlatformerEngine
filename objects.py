import pygame, pytweening

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

class Exit(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf, number):
		super().__init__(groups)
		self.game = game
		self.number = number
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(12.5, 12.5)

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups, path):
		super().__init__(groups)

		#self.sprite_type = sprite_type
		self.game = game
		self.zone = zone
		self.frames = self.game.import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()

class TrickPlatform(AnimatedTile):
	def __init__(self, game, zone, pos, groups, path):
		super().__init__(game, zone, pos, groups, path)
		self.game = game
		self.zone = zone
		self.frames = self.game.import_folder(path)
		self.on_platform = False
		self.frame_rate = 0.2
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,2.5)
		

	def collide_platforms(self):
		
		#collided = pygame.sprite.spritecollide(self.zone.target, self.zone.trick_platform_sprites, False)
		if self.hitbox.colliderect(self.zone.target.hitbox): 
			if self.zone.target.hitbox.bottom <= self.hitbox.top + 6 and self.zone.target.vel.y >= 0:
				if self.frame_index < 8:
					self.on_platform = True
					self.zone.target.cyote_timer = 0
					self.zone.target.vel.y = 0
					self.zone.target.hitbox.bottom = self.hitbox.top +1
					self.zone.target.on_ground = True
					self.zone.target.on_wall = False

	def animate(self):
		if self.on_platform:
			self.frame_index += self.frame_rate
			if self.frame_index >= len(self.frames) -1:
				self.on_platform = False
				self.frame_index = 0
				
			self.frame_index += self.frame_rate
			self.image = self.frames[int(self.frame_index)]

		else:
			self.frame_index = 0

	def update(self):
		self.collide_platforms()
		self.animate()

class Platform(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups, surf, direction):
		super().__init__(groups)
		self.game = game
		self.zone = zone
		self.direction = direction
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

		self.vel = pygame.math.Vector2()

		self.on_platform = False
		self.timer = 0
		self.time = 10

	def move(self):

		if self.direction == 'right':
			self.vel.x += 0.1
			if self.vel.x >= 3:
				self.vel.x = 3
				self.timer += 1
				if self.timer >= self.time:
					self.timer = 0
					self.direction = 'left'

		elif self.direction == 'left':
			self.vel.x -= 0.1
			if self.vel.x <= -2.1:
				self.vel.x = -2.1
				self.timer += 1
				if self.timer >= self.time:
					self.timer = 0
					self.direction = 'right'

		elif self.direction == 'down':
			self.vel.y += 0.1
			if self.vel.y >= 3:
				self.vel.y = 3
				self.timer += 1
				if self.timer >= self.time:
					self.timer = 0
					self.direction = 'up'

		elif self.direction == 'up':
			self.vel.y -= 0.1
			if self.vel.y <= -2.1:
				self.vel.y = -2.1
				self.timer += 1
				if self.timer >= self.time:
					self.timer = 0
					self.direction = 'down'
		else:
			self.vel = pygame.math.Vector2()


		self.hitbox.x += self.vel.x
		self.hitbox.y += self.vel.y
		self.rect.center = self.hitbox.center

	def update(self):
		self.move()
		
class SawBlade(Platform):
	def __init__(self, game, zone, pos, groups, surf, direction):
		super().__init__(game, zone, pos, groups, surf, direction)
		self.game = game
		self.zone = zone
		self.direction = direction
		self.image_type = pygame.image.load(surf).convert_alpha()
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,0)
		
		self.rotate = 0
		
	def rotate_sprite(self):
		self.rotate -= 3
		self.image = pygame.transform.rotate(self.image_type, self.rotate)
		self.rect = self.image.get_rect(center = self.rect.center)
		self.hitbox.center = self.rect.center

	def update(self):
		self.move()
		self.rotate_sprite()

class Attack(pygame.sprite.Sprite):
	def __init__(self, game, zone, sprite, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.zone = zone
		self.sprite = sprite
		self.frames = self.game.import_folder(str(self.sprite.sword_path))
		self.opposite_frames = self.game.import_folder(str(self.sprite.sword_path)+'_2')
		self.hit_wall_frames = self.game.import_folder(str(self.sprite.sword_path)+'_wall')
		self.frame_index = 0
		self.frame_rate = 0.3
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.sprite.rect.center)
		self.hitbox = self.rect.inflate(0, 0)
		self.vel = pygame.math.Vector2()

	def animate(self):
		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1 or self.sprite.dashing:
			self.kill()
			self.sprite.attacking = False
			if self.sprite.attack_count == self.sprite.max_chain_attacks:
				self.sprite.attack_count = 0


		if pygame.sprite.spritecollide(self, self.zone.block_sprites, False, pygame.sprite.collide_rect_ratio(0.8)):
			self.image = self.hit_wall_frames[int(self.frame_index)]
		elif self.sprite.attack_count % 2 == 0:
			self.image = self.opposite_frames[int(self.frame_index)]
		else:
			self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.zone.surf.blit(pygame.Surface((28, 28)), self.rect)
		self.animate()

		if self.sprite.facing == -1:
			self.rect = self.image.get_rect(midright = (self.sprite.rect.midright[0] + 20, self.sprite.rect.midright[1]))
			self.image = pygame.transform.flip(self.image, True, False)
		else:
			self.rect = self.image.get_rect(midleft = (self.sprite.rect.midleft[0] - 20, self.sprite.rect.midleft[1]))


class SpecialAttack(pygame.sprite.Sprite):
	def __init__(self, game, zone, sprite, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.zone = zone
		self.sprite = sprite
		self.frames = self.game.import_folder(str(self.sprite.sword_path)+ '_special')
		self.frame_index = 0
		self.frame_rate = 0.3
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.sprite.rect.center)
		self.hitbox = self.rect.inflate(0, 0)
	

	def animate(self):
		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1 or self.sprite.dashing:
			self.kill()
	
		self.image = self.frames[int(self.frame_index)]


	def update(self):
		
		self.rect = self.image.get_rect(center = self.sprite.rect.center)
		self.animate()

		