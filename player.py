import pygame
from entity import Entity

class Player(Entity):
	def __init__(self, game, zone, char, pos, groups):
		super().__init__(game, zone, char, pos, groups)

		#moving
		self.max_speed = 2

		#attacking
		self.sword_path = 'imgs/sword_animations/sword'
		self.can_standard_melee = False
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

	def wall_slide(self):
		if self.stationary_timer > self.wall_hang_cooldown:
			if self.vel.y >= self.wall_slide_speed:
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

			elif self.can_standard_melee == True and self.game.actions['z'] == False and not self.attacking and not self.dashing:
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
			elif self.vel.y < 0:
				self.change_state('jump', 0.2, 'end_on_last_frame')
			elif self.vel.y < self.max_fall_speed:
				self.change_state('fall', 0.2, 'end_on_last_frame')
			else:
				self.change_state('max_fall', 0.3, 'loop')
		else:
			self.change_state('death', 0.2, 'end_on_last_frame')
		
	def move_logic(self):
		keys = pygame.key.get_pressed()
		# lets player immediately bounce off wall instead of waiting for frixtion before they can turnaround
	
		if self.on_ground:
			if (self.moving_right and self.on_left) or (self.moving_left and self.on_right):
				self.vel.x = 0

		if self.shooting and not (self.attacking or self.building_special_attack or self.special_attacking or self.dashing):
			self.vel.x -= self.shoot_knockback_deceleration * -self.facing
			if self.vel.y >= 0:
				self.vel.y = 0
			if self.facing == 1:
				if self.vel.x >= self.idle_speed:
					self.vel.x = self.idle_speed
					#self.shooting = False
			elif self.facing == -1:
				if self.vel.x < self.idle_speed:
					self.vel.x = self.idle_speed
					#self.shooting = False

		elif self.dashing:
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

		elif self.on_left_wall and not self.on_ground:
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

		elif self.attacking or self.building_special_attack or self.special_attacking:
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
		self.wall_slide()
		self.x_collisions()
		self.apply_gravity()
		self.hitbox.y += self.vel.y 
		self.y_collisions()	
		self.rect.center = self.hitbox.center
		self.stop_at_edge_of_room()
		self.cooldowns()

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









