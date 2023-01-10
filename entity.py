import pygame
from math import atan2, degrees, pi, sin
from map import Map
from inventory import Inventory

class Entity(pygame.sprite.Sprite):
	def __init__(self, game, zone, char, pos, groups):
		super().__init__(groups)

		self.game = game
		self.zone = zone
		self.char = char
		self.import_imgs()

		self.image = pygame.image.load(f'imgs/player/run/00.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-7.5, -2.5)
		self.inflation = [-18, -6]

		self.vel = pygame.math.Vector2()
		self.current_x = 0

		self.state = 'fall'
		self.alive = True
		self.alpha = 255
		self.frame_index = 0
		self.frame_rate = 0.2
		self.animation_type = 'loop'

		self.on_platform = False
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		self.on_left_wall = False
		self.on_right_wall = False
		self.collided = False
		
		self.moving_right = False
		self.moving_left = False
		
		self.idle_speed = 0
		self.platform_speed = 0
		self.facing = 1
		self.max_speed = 2
		self.friction = self.max_speed * 0.2
		self.acceleration = self.max_speed * 0.1
		self.gravity = 0.2
		self.normal_gravity = self.gravity
		self.double_gravity = self.gravity *2
		self.jump_height = 4.5
		self.max_fall_speed = 4
		self.jump_counter = 0
		self.cyote_timer = 0
		self.cyote_timer_thresh = 8

		#knockback
		self.knocked_back = False
		self.can_be_knocked_back = True
		self.knock_back_time = None
		self.knock_back_cooldown = 20
		self.knock_back_speed = 2


	def import_imgs(self):
		char_path = f'imgs/{self.char}/'
		self.animations = {'shooting':[],'attack':[],'attack_2':[],'build_up':[], 'special':[], 'crawling':[], 'crouching':[], 
		'run':[], 'idle':[], 'jump':[],'fall':[], 'max_fall':[], 'death':[], 'hit':[], 'dashing':[], 'wall_hanging':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def input(self):
		keys = pygame.key.get_pressed()
		if not self.zone.exiting_area:
			# dash input
			if self.game.actions['c']:
				self.dash()
				self.game.actions['c'] = False

			# attack input
			if keys[pygame.K_z]:
				self.attack_key_held = True
			else:
				self.attack_key_held = False
				
			if self.game.actions['z']:
				self.can_standard_melee = True
	
			#show map
			if self.game.actions['m']:
				new_state = Map(self.game, self.zone)
				new_state.enter_state()
				self.game.actions['m'] = False

			# show inventory
			if self.game.actions['i']:
				new_state = Inventory(self.game, self.zone)
				new_state.enter_state()
				self.game.actions['i'] = False

			if keys[pygame.K_x]:
				self.shoot_gun()
				
			if self.game.actions['right'] and not self.game.actions['left']:
				self.moving_right = True

			if self.game.actions['left'] and not self.game.actions['right']:
				self.moving_left = True

			if self.game.actions['right'] == False:
				self.moving_right = False

			if self.game.actions['left'] == False:
				self.moving_left = False

			if self.game.actions['up']:
				if self.on_right_wall or self.on_left_wall:
					self.wall_kick()
					# if self.crouching:
					# 	self.crouch('up')
					# elif self.on_right or self.on_left:
					# 	self.wall_kick()
					# else:
				else:
					self.jump(self.jump_height)
				self.game.actions['up'] = False

			# if not holding the jump key, gravity increases while moving up to give variable jump height
			if not (keys[pygame.K_UP] or keys[pygame.K_w]) and self.vel.y < 0:
					self.gravity = self.double_gravity
			else:
				# set gravity back to normal
				self.gravity = self.normal_gravity

			# refresh bullets for testing
			if self.game.actions['backspace']:
				if 'green_shield' in self.game.data['items'] and self.game.green_shield == 100:	
					self.game.green_shield = 0	
				elif 'blue_shield' in self.game.data['items'] and self.game.blue_shield == 100:	
					self.game.blue_shield = 0	
				else:
					self.game.current_health -= 1

				self.game.current_bullets = self.game.data['max_bullets']
		
				self.game.actions['backspace'] = False


			if self.game.actions['tab']:
				if 'green_shield' in self.game.data['items']:
					self.game.data['items'].remove('green_shield')
				elif 'blue_shield' in self.game.data['items']:
					self.game.data['items'].remove('blue_shield')
				self.game.actions['tab'] = False

				self.game.data['max_bullets'], self.game.current_bullets = 10, 10
				self.game.data['max_health'], self.game.current_health = 8, 8
			else:
				pass


	def change_state(self, new_state, new_frame_rate, new_animation_type):
		if self.state != new_state:
			self.frame_index = 0
			self.state = new_state
			self.frame_rate = new_frame_rate
			self.animation_type = new_animation_type

	def set_state(self):
		if self.alive:
			
			if self.attacking:
				self.change_state('attack', 0.2, 'end_on_last_frame')
			
			elif self.on_ground:
				if not (self.moving_right or self.moving_left) or self.on_right or self.on_left:
					self.change_state('idle', 0.1, 'loop')
				else:
					self.change_state('run', 0.2, 'loop')
			elif self.vel.y < 0:
				self.change_state('jump', 0.2, 'end_on_last_frame')
			elif self.vel.y < self.max_fall_speed:
				self.change_state('fall', 0.2, 'end_on_last_frame')
			else:
				self.change_state('max_fall', 0.3, 'loop')
		else:
			self.change_state('death', 0.2, 'end_on_last_frame')

	def animate(self, frame_rate):

		animation = self.animations[self.state]	

		self.frame_index += frame_rate

		if self.frame_index >= len(animation):
			if self.animation_type == 'loop':
				self.frame_index = 0
			elif self.animation_type == 'end_on_last_frame':
				self.frame_index = len(animation) -1
			else:
				self.kill()
		
		right_img = animation[int(self.frame_index)]
		if self.facing == 1:
			self.image = right_img
		else:
			left_img = pygame.transform.flip(right_img, True, False)
			self.image = left_img

		
		# moves the rect into correct place if different size, ie. the crouch frame 
		#will stick to floor and not topleft of rect
		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
			self.hitbox = self.rect.inflate(self.inflation)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
			self.hitbox = self.rect.inflate(self.inflation)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
			self.hitbox = self.rect.inflate(self.inflation)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
			self.hitbox = self.rect.inflate(self.inflation)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
			self.hitbox = self.rect.inflate(self.inflation)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)
			self.hitbox = self.rect.inflate(self.inflation)
		else:
			self.rect = self.image.get_rect(center = self.rect.center)
			self.hitbox = self.rect.inflate(self.inflation)

	def x_collisions(self):
		if pygame.sprite.spritecollide(self, self.zone.block_sprites, False, pygame.sprite.pygame.sprite.collide_rect_ratio(0.63)):
			self.collided = True
		else:
			self.collided = False
	
		for sprite in self.zone.block_sprites:

			if sprite.hitbox.colliderect(self.hitbox):
				if self.vel.x > 0:
					self.hitbox.right = sprite.hitbox.left
					self.on_right = True
					self.on_right_wall = True
					self.current_x = self.hitbox.right

				elif self.vel.x < 0:
					self.hitbox.left = sprite.hitbox.right
					self.on_left = True
					self.on_left_wall = True
					self.current_x = self.hitbox.left

		if self.on_right or self.on_left:
			self.jump_counter = 1
			self.dashing = False
			self.can_dash = True

		if not self.collided:
			self.stationary_timer = 0
			self.on_left_wall = False
			self.on_right_wall = False
					
		if self.on_right and (self.hitbox.right > self.current_x or self.vel.x <= 0):
			self.on_right = False
			self.game.actions['z'] = True #stops the up key creating an attack as z is set to false when 'can_attack'

		if self.on_left and (self.hitbox.left < self.current_x or self.vel.x >= 0):
			self.on_left = False

		
	def y_collisions(self):
		for sprite in self.zone.block_sprites:
			if sprite.hitbox.colliderect(self.hitbox):
				if self.vel.y > 0:
					self.hitbox.bottom = sprite.hitbox.top
					self.vel.y = 0
					self.on_ground = True
					self.cyote_timer = 0

				elif self.vel.y < 0:
					self.hitbox.top = sprite.hitbox.bottom
					self.vel.y = 0
					self.on_ceiling = True

		if self.on_ground and self.vel.y < -1 or self.vel.y > 1:
			self.on_ground = False

		if self.on_ceiling and self.vel.y > 0:
			self.on_ceiling = False


	def jump(self, height):
		if self.cyote_timer < self.cyote_timer_thresh:
			self.vel.y = -height
			self.jump_counter = 1
		elif self.jump_counter == 1:
			self.vel.y = -height
			self.jump_counter = 0

	def apply_gravity(self):
		self.vel.y += self.gravity
		self.rect.y += self.vel.y
		if self.vel.y > self.max_fall_speed:
		 	self.vel.y = self.max_fall_speed

	def move(self):
		if self.moving_right and self.vel.x >= self.idle_speed:
			self.vel.x += self.acceleration
			self.facing = 1

		elif self.moving_left and self.vel.x <= self.idle_speed:
			self.vel.x -= self.acceleration
			self.facing = -1

		elif self.facing == 1:
				self.vel.x -= self.friction
				if self.vel.x <= self.idle_speed:
					self.vel.x = self.idle_speed
		else:
				self.vel.x += self.friction
				if self.vel.x >= self.idle_speed:
					self.vel.x = self.idle_speed
			

		self.hitbox.x += self.vel.x 
		self.x_collisions()
		self.apply_gravity()
		self.hitbox.y += self.vel.y 
		self.y_collisions()	
		self.rect.center = self.hitbox.center

	def platforms(self):
		for platform in self.zone.platform_sprites:
			platform_raycast = pygame.Rect(platform.hitbox.x, platform.hitbox.y - platform.hitbox.height * 0.2, platform.hitbox.width, platform.hitbox.height)
			if self.hitbox.colliderect(platform.hitbox) or self.hitbox.colliderect(platform_raycast): 
				if self.hitbox.bottom <= platform.hitbox.top + 8 and self.vel.y >= 0:
					self.hitbox.bottom = platform.hitbox.top
					self.on_platform = True
					self.on_ground = True
					self.idle_speed = platform.vel.x
					self.cyote_timer = 0
					self.vel.y = 1
					self.hitbox.y += platform.vel.y

			else:
				self.on_platform = False

	def knockback(self):
		if self.can_be_knocked_back:
			self.knocked_back = True
			self.vel.x = self.knock_back_speed * - self.facing
			self.can_be_knocked_back = False
			self.knock_back_time = pygame.time.get_ticks()

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		# if self.alive:
		# 	if self.invincible:
		# 		self.invincibility_timer += 1
		# 		if self.invincibility_timer >= self.invincible_cooldown:
		# 			self.invincible = False
		# 			self.invincibility_timer = 0

		
		if not self.can_be_knocked_back:
			if current_time - self.knock_back_time >= self.knock_back_cooldown:
				self.can_be_knocked_back = True

		if self.knocked_back:
			if current_time - self.knock_back_time >= self.knock_back_cooldown:
				self.knocked_back = False

		if not self.can_wall_kick:
			if current_time - self.wall_kick_time >= self.wall_kick_cooldown:
				self.can_wall_kick = True
				self.wall_kicking = False

		if not self.can_attack:
			if current_time - self.last_attack_time >= self.last_attack_cooldown:
				if self.game.actions['z']:
					self.can_attack = True

		if not self.attack_count_reset and self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attack_count_reset = True
				self.attack_count = 0

		if self.special_attacking:
			self.game.actions['z'] = True
			if current_time - self.special_attack_time >= self.special_attack_cooldown:
				self.special_attacking = False
				

		if not self.can_dash:
			if current_time - self.dash_time >= self.dash_cooldown:
				self.can_dash = True
				self.dashed_off_wall = False
				self.game.actions['z'] = True

		if not self.can_shoot:
			if current_time - self.shoot_time >= self.shoot_cooldown:
				self.can_shoot = True

		if self.shooting:
			self.game.screen_shaking = True
			if self.frame_index >= len(self.animations[self.state])-1:
				self.shooting = False
				self.game.screen_shaking = False

		
	def update(self):
		self.cyote_timer += 1
		self.idle_speed = self.platform_speed
		self.refresh_shields_and_stamina()
		self.platforms()
		self.set_state()
		self.move_logic()
		self.melee()
		self.build_special()
		self.animate(self.frame_rate)
		# if falling, this gives the player one jump
		if self.jump_counter == 0 and self.cyote_timer < self.cyote_timer_thresh:
			self.jump_counter = 1
		if self.game.stamina < 100:
			self.game.stamina += self.game.data['stamina_refresh_rate']
		else:
			self.game.stamina = 100


		


