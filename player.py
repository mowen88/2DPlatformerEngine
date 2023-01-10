import pygame
from entity import Entity

class Player(pygame.sprite.Sprite):
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

		#moving
		self.moving_right = False
		self.moving_left = False
		self.max_speed = 2

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
		self.max_fall_speed = 5
		self.jump_counter = 0
		self.cyote_timer = 0
		self.cyote_timer_thresh = 8


		self.on_platform = False
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		self.on_left_wall = False
		self.on_right_wall = False
		self.collided = False

		#attacking
		self.sword_path = 'imgs/sword_animations/sword'
	
		self.attacking = False
		self.can_attack = True
		self.next_attack_pending = False
		self.attack_time = None
		self.attack_count = 0
		self.max_chain_attacks = 3
		self.attack_cooldown = 600
		
		self.attack_speed = self.max_speed * 0.75
		self.attack_deceleration = self.max_speed *0.05
	
		self.attack_count_reset = True
		self.last_attack_time = None
		self.last_attack_cooldown = 700

		#shooting
		self.shooting = False
		self.can_shoot = True
		self.shoot_time = None
		self.shoot_cooldown = self.game.data['shoot_cooldown']
		self.shoot_knockback_speed = 3
		self.shoot_knockback_deceleration = self.shoot_knockback_speed * 0.1

		#dashing
		self.dashing = False
		self.can_dash = True
		self.dash_time = None
		self.dash_cooldown = 800
		self.dash_speed = self.max_speed * 5
		self.dash_deceleration = self.dash_speed * 0.05
		self.dashed_off_wall = False

		# special attack build up
		self.attack_key_held = False
		self.can_special_attack = True
		self.building_special_attack = False
		self.special_buildup_timer = 0
		self.build_up_time = 60

		#special attacking
		self.special_attacking = False
		self.special_attack_time = None
		self.special_attack_cooldown = 700

		# wall kicking
		self.wall_kicking = False
		self.can_wall_kick = True
		self.wall_kick_time = None
		self.wall_kick_cooldown = 100
		self.wall_kickoff_speed = self.max_speed * 2
		self.wall_slide_speed = 1
		
		# wall cooldown
		self.wall_hang_timer = 0
		self.stationary_timer = 0
		self.wall_hang_cooldown = 15

	def import_imgs(self):
		char_path = f'imgs/{self.char}/'
		self.animations = {'shooting':[],'attack':[],'attack_2':[],'build_up':[], 'special':[], 'crawling':[], 'crouching':[], 
		'run':[], 'idle':[], 'jump':[],'fall':[], 'max_fall':[], 'death':[], 'hit':[], 'dashing':[], 'on_wall':[]}

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
				if (self.on_right_wall and keys[pygame.K_RIGHT]) or (self.on_left_wall and keys[pygame.K_LEFT]):
					self.wall_kick()
					# if self.crouching:
					# 	self.crouch('up')
					# elif self.on_right or self.on_left:
					# 	self.wall_kick()
					# else:
				else:
					self.on_left_wall, self.on_right_wall = False, False
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



	def wall_slide(self):
		if self.stationary_timer > self.wall_hang_cooldown:
			if self.vel.y >= self.wall_slide_speed and self.state == 'on_wall':
				self.vel.y = self.wall_slide_speed

	def wall_kick(self):
		if self.can_wall_kick:
			self.wall_kicking = True
			self.on_left_wall, self.on_right_wall = False, False
			self.vel.x = self.wall_kickoff_speed * self.facing
			self.vel.y = -self.jump_height
			self.can_wall_kick = False
			self.wall_kick_time = pygame.time.get_ticks()

	def dash(self):
		if self.can_dash: #and not self.crouching:
			self.dashing = True
			self.shooting = False
			self.vel.x = self.dash_speed * self.facing
			self.can_dash = False
			self.dash_time = pygame.time.get_ticks()

	def shoot_gun(self):
		if self.can_shoot and not (self.attacking or self.building_special_attack or self.special_attacking) and not (self.on_left_wall or self.on_right_wall) and self.game.current_bullets > 0: #and not self.crouching:
			self.shooting = True
			self.frame_index = 0
			self.zone.create_gun_blast()
			self.game.current_bullets -= 1
			self.vel.x = self.shoot_knockback_speed * -self.facing
			self.can_shoot = False
			self.shoot_time = pygame.time.get_ticks()

	def build_special(self):
		if self.attack_key_held and not self.attacking and self.game.stamina == 100 and self.can_attack:
			self.special_buildup_timer += 1
			if self.special_buildup_timer < self.build_up_time:
				self.building_special_attack = True
			elif self.special_buildup_timer >= self.build_up_time:
				self.special_attacking = True
				self.zone.create_special_attack()
				self.game.stamina = 0
				self.special_buildup_timer = 0
				self.special_attack_time = pygame.time.get_ticks()
				self.last_attack_time = pygame.time.get_ticks()
		else:
			self.building_special_attack = False
			self.special_buildup_timer = 0
	
	def melee(self):
		if self.can_dash and not self.special_attacking:	# if not self.crouching:
			if self.game.actions['z'] == False and (self.attack_count > 0 and self.attack_count < self.max_chain_attacks):
				self.next_attack_pending = True

			elif self.game.actions['z'] == False and not self.attacking and not self.dashing:
				if self.can_attack:
					if self.vel.x < self.attack_speed * self.facing:
						self.vel.x = self.attack_speed * self.facing

					self.attacking = True
					self.attack_count += 1
					self.attack_count_reset = False
					self.attack_time = pygame.time.get_ticks()
					self.zone.create_attack()
					if self.vel.x != self.max_speed * self.facing:
						self.vel.x = self.attack_speed * self.facing
					self.game.actions['z'] = True

			if self.attack_count == self.max_chain_attacks:
				self.last_attack_time = pygame.time.get_ticks()
				self.can_attack = False
				self.game.actions['z'] = True


			if self.next_attack_pending and not self.attacking:
				self.attacking = True
				self.attack_count += 1
				self.attack_count_reset = False
				self.attack_time = pygame.time.get_ticks()
				self.zone.create_attack()
				if self.vel.x != self.max_speed * self.facing:
					self.vel.x = self.attack_speed * self.facing
				self.next_attack_pending = False
				self.game.actions['z'] = True

	def change_state(self, new_state, new_frame_rate, new_animation_type):
		if self.state != new_state:
			self.frame_index = 0
			self.state = new_state
			self.frame_rate = new_frame_rate
			self.animation_type = new_animation_type

	def set_state(self):
		if self.alive:
			if self.dashing:
				self.change_state('dashing', 0.2, 'end_on_last_frame')
			elif self.shooting:
				self.change_state('shooting', 0.25, 'end_on_last_frame')
			elif self.special_attacking:
				self.change_state('special', 0.3, 'end_on_last_frame')
			elif self.building_special_attack:
				self.change_state('build_up', 0.3, 'end_on_last_frame')
			elif self.attacking:
				if self.attack_count % 2 == 0:
					self.change_state('attack', 0.2, 'end_on_last_frame')
				else:
					self.change_state('attack_2', 0.2, 'end_on_last_frame')
			elif self.on_ground:
				if not (self.moving_right or self.moving_left) or self.on_right or self.on_left:
					self.change_state('idle', 0.1, 'loop')
				else:
					self.change_state('run', 0.2, 'loop')
			elif self.on_right_wall or self.on_left_wall:
				self.change_state('on_wall', 0.2, 'end_on_last_frame')
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

		
	def move_logic(self):
		keys = pygame.key.get_pressed()
		# lets player immediately bounce off wall instead of waiting for frixtion before they can turnaround
	
		if self.on_ground:
			if (self.moving_right and self.on_left) or (self.moving_left and self.on_right):
				self.vel.x = 0

		if self.state == 'shooting':
			self
			self.vel.x -= self.shoot_knockback_deceleration * -self.facing
			if self.vel.y >= 0:
				self.vel.y = 0
			if self.facing == 1:
				if self.vel.x >= self.idle_speed:
					self.vel.x = self.idle_speed
					self.shooting = False
			elif self.facing == -1:
				if self.vel.x < self.idle_speed:
					self.vel.x = self.idle_speed
					self.shooting = False

		elif self.state == 'dashing':
			if self.vel.y >= 0:
				self.vel.y = 0
			
			self.vel.x -= self.dash_deceleration * self.facing
			if self.facing == 1:
				if self.vel.x <= self.idle_speed:
					self.vel.x = self.idle_speed
					self.dashing = False

			elif self.facing == -1:
				if self.vel.x >= self.idle_speed:
					self.vel.x = self.idle_speed
					self.dashing = False

		elif self.state =='on_wall':
			if self.on_left_wall and not self.on_ground:
				self.facing = 1
				self.stationary_timer += 1
				if self.stationary_timer < self.wall_hang_cooldown and self.vel.y >= 0:
					self.vel = pygame.math.Vector2()

				if keys[pygame.K_RIGHT]:
					self.wall_hang_timer += 1
				else:
					self.wall_hang_timer = 0
				if self.wall_hang_timer > self.wall_hang_cooldown:
					self.vel.x = 1
					self.on_left_wall = False
			
			elif self.on_right_wall and not self.on_ground:
				self.vel.x = 0
				self.facing = -1
				self.stationary_timer += 1
				if self.stationary_timer < self.wall_hang_cooldown and self.vel.y >= 0:
					self.vel = pygame.math.Vector2()

				if keys[pygame.K_LEFT]:
					self.wall_hang_timer += 1
				else:
					self.wall_hang_timer = 0
				if self.wall_hang_timer > self.wall_hang_cooldown:
					self.vel.x = -1
					self.on_right_wall = False

		elif self.state == 'attack' or self.state == 'attack_2' or self.state == 'build_up' or self.state == 'special':
			self.vel.y = 0
			self.vel.x -= self.attack_deceleration * self.facing
			if (self.facing == 1 and self.vel.x <= self.idle_speed) or (self.facing == -1 and self.vel.x >= self.idle_speed):
				self.vel.x = self.idle_speed
		
		elif self.moving_right:

			self.facing = 1

			if self.vel.x <= self.idle_speed:
				self.vel.x += self.friction
			else:
				self.vel.x += self.acceleration

			if self.vel.x > self.max_speed + self.idle_speed:
				self.vel.x = self.max_speed + self.idle_speed
		
		elif self.moving_left:

			self.facing = -1

			if self.vel.x >= self.idle_speed:
				self.vel.x -= self.friction
			else:
				self.vel.x -= self.acceleration

			if self.vel.x < -self.max_speed + self.idle_speed:
				self.vel.x = -self.max_speed + self.idle_speed

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

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		# if self.alive:
		# 	if self.invincible:
		# 		self.invincibility_timer += 1
		# 		if self.invincibility_timer >= self.invincible_cooldown:
		# 			self.invincible = False
		# 			self.invincibility_timer = 0

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
			if self.frame_index >= len(self.animations[self.state])-1:
				self.shooting = False
				
	def screenshake(self):
		if self.state == 'shooting':
			self.game.screen_shaking = True
		else:
			self.game.screen_shaking = False

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
					self.vel.y = 0
					self.hitbox.y += platform.vel.y

			else:
				self.on_platform = False

	def refresh_shields_and_stamina(self):
		if self.game.blue_shield <= 100:
			self.game.blue_shield += self.game.data['shield_refresh_rate']

		if self.game.green_shield <= 100:
			self.game.green_shield += self.game.data['shield_refresh_rate']

		if self.game.green_shield >= 100:
			self.game.green_shield = 100

		if self.game.blue_shield >= 100:
			self.game.blue_shield = 100

	def stop_at_edge_of_room(self):
		if self.hitbox.right >= self.zone.rendered_sprites.zone_size[0] and self.facing == 1:
			self.vel.x = 0
			self.on_right = True
		elif self.hitbox.left <= 0 and self.facing == -1:
			self.vel.x = 0
			self.on_left = True
		if self.hitbox.bottom >= self.zone.rendered_sprites.zone_size[1]:
			self.vel.y = 0
			self.cyote_timer = 0
			self.on_ground = True
		elif self.hitbox.top <= 0:
			self.vel.y = 1
			self.on_ceiling = True

	def update(self):
		self.cyote_timer += 1
		self.idle_speed = self.platform_speed
		self.refresh_shields_and_stamina()
		self.platforms()
		self.wall_slide()
		self.set_state()
		self.move_logic()
		self.melee()
		self.build_special()
		self.stop_at_edge_of_room()
		self.cooldowns()
		self.screenshake()
		self.animate(self.frame_rate)
		# if falling, this gives the player one jump
		if self.jump_counter == 0 and self.cyote_timer < self.cyote_timer_thresh:
			self.jump_counter = 1
		if self.game.stamina < 100:
			self.game.stamina += self.game.data['stamina_refresh_rate']
		else:
			self.game.stamina = 100










