import pygame
from entity import Entity

class WalkingEnemy(Entity):
	def __init__(self, game, zone, char, pos, groups):
		super().__init__(game, zone, char, pos, groups)
		self.game = game
		self.zone = zone
		self.char = 'samurai'
		self.image = pygame.image.load(f'imgs/enemies/{char}/idle/0.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.inflation = [0, 0]

		self.import_imgs()
		
		self.vision_box = pygame.Rect(0,0,300, 80)

		self.alerted = False
		self.windup_timer = 0
		self.speed = 1
		self.attack_speed = self.speed * 8

		self.invincible_cooldown = 80
		self.knock_back_cooldown = 30

		self.attacking = False

		#self.coins_given = random.randint(4,6)

	def import_imgs(self):
		char_path = f'imgs/enemies/{self.char}/'
		self.animations = {'attack':[], 'run':[], 'idle':[], 'death':[], 'hit':[], 'fall':[], 'max_fall':[], 'windup':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def update(self):
		self.move()
		self.set_state()
		self.animate(self.frame_rate)

class LungingEnemy(Entity):
	def __init__(self, game, zone, char, pos, groups):
		super().__init__(game, zone, char, pos, groups)
		self.game = game
		self.zone = zone
		self.char = 'samurai'
		self.image = pygame.image.load(f'imgs/enemies/{char}/idle/0.png')
		self.rect = self.image.get_rect(topleft = pos)
		self.inflation = [0, 0]

		self.import_imgs()
		
		self.vision_box = pygame.Rect(0,0,300, 80)

		self.alerted = False
		self.windup_timer = 0
		self.speed = 1
		self.attack_speed = self.speed * 8

		self.invincible_cooldown = 80
		self.knock_back_cooldown = 30

		self.attacking = False

		self.state = 'fall'
		self.alive = True
		self.alpha = 255
		self.frame_index = 0
		self.frame_rate = 0.2
		self.animation_type = 'loop'

		#self.coins_given = random.randint(4,6)

	def import_imgs(self):
		char_path = f'imgs/enemies/{self.char}/'
		self.animations = {'attack':[], 'run':[], 'idle':[], 'death':[], 'hit':[], 'fall':[], 'max_fall':[], 'windup':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def lock_direction(self):
		return self.facing

	def seen_player(self):
		if self.zone.player.hitbox.colliderect(self.vision_box):
			self.alerted = True



	def action(self, direction, speed):
		if self.alive:

			if self.alerted and not self.attacking:
				self.vel.x = 0
				self.crouching = True
				self.windup_timer += 1
				if self.windup_timer >= 60:
					self.windup_timer = 0
					self.attacking = True

			elif self.attacking:
				self.facing = self.lock_direction()
				self.vel.x = self.attack_speed * self.facing
				self.attack_speed -= 0.1 
				if self.attack_speed <= 0:
					self.crouching = False
					self.attacking = False
					self.alerted = False
					self.attack_speed = 8

			else:
				if direction == 1 and self.vel.x >= 0:
					self.vel.x += self.acceleration
					self.facing = 1 
					if self.vel.x >= speed:
						self.vel.x = speed
				elif direction == -1 and self.vel.x <= 0:
					self.vel.x -= self.acceleration
					self.facing = -1
					if self.vel.x <= -speed:
						self.vel.x = -speed
				elif self.facing == 1:
					self.vel.x -= self.friction
					if self.vel.x <= 0:
						self.vel.x = 0
				else:
					self.vel.x += self.friction
					if self.vel.x >= 0:
						self.vel.x = 0
		

			self.hitbox.x += self.vel.x 
			self.x_collisions()
			self.apply_gravity()
			self.hitbox.y += self.vel.y
			self.y_collisions() 
			self.rect.center = self.hitbox.center

	def switch_direction(self):
		if self.on_right:
			self.facing = -1
		elif self.on_left:
			self.facing = 1
	
	# def switch_direction_collision_tile(self):
	# 	for sprite in self.zone.collision_tile_sprites:
	# 		if sprite.hitbox.colliderect(self.hitbox):
	# 			if self.vel.x > 0:
	# 				self.hitbox.right = sprite.hitbox.left
	# 				self.on_right = True

	# 			elif self.vel.x < 0:
	# 				self.hitbox.left = sprite.hitbox.right
	# 				self.on_left = True



	def update(self):
		self.vision_box.center = (self.hitbox.centerx + 150 * self.facing, self.hitbox.centery)
		self.seen_player()
		#self.animate(self.frame_rate)
		self.set_state()
		self.platforms()
		self.animate(self.frame_rate)
		# self.switch_direction_collision_tile()
		if not (self.attacking or self.alerted):
			self.switch_direction()
			self.action(self.facing, self.speed)
		else:
			self.action(self.facing, self.attack_speed)
