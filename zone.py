import pygame, os, csv
from state import State
from camera import Camera
from objects import Tile, Exit, Platform, TrickPlatform, SawBlade, Attack, SpecialAttack
from player import Player
from enemy import WalkingEnemy, LungingEnemy
from ui import UI
from particles import GunBlast

class Zone(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.surf = pygame.display.get_surface()

		# sprite groups
		self.rendered_sprites = Camera(self.game, self)
		self.updated_sprites = pygame.sprite.Group()

		self.enemy_sprites = pygame.sprite.Group()
		self.block_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		self.trick_platform_sprites = pygame.sprite.Group()
		self.hazard_sprites = pygame.sprite.Group()
		self.exit_sprites = pygame.sprite.Group()
		
		#single sprites
		self.attack_sprite = pygame.sprite.GroupSingle()

		self.target = None

		self.exit_cooldown = 0
		self.entry_cooldown = 600
		self.exiting_area = False
		self.entering_area = True

		self.fade_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.fade_surf.fill(self.game.BLACK)

		self.cutscene_running = False
		self.dialog_running = False
		self.npc_collided = False
		self.fade_timer = 0
		self.trigger_interact_box = True
		self.lever_on = False
		
		self.ui = UI(self.game, self)

		self.create_zone()

	def create_zone(self):
		layout_list = ['blocks', 'entries', 'objects', 'entries', 'exits', 'enemies']
		layouts = {}
		for i in layout_list:
			layouts.update({i:self.game.import_csv(f'zones/{self.game.current_zone}/{self.game.current_zone}_{i}.csv')})


		images = {
		'blocks':self.game.import_folder(f'imgs/tiles/blocks')
		}

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * self.game.TILESIZE
						y = row_index * self.game.TILESIZE

						if style == 'blocks':
							surf = images['blocks'][int(col)]
							sprite =  Tile(self.game, (x,y), [self.rendered_sprites, self.updated_sprites], surf)
							self.block_sprites.add(sprite)

						if style == 'entries':
							if col == str(self.game.spawn_point):
								self.player = Player(self.game, self, 'player', (x, y), [self.rendered_sprites, self.updated_sprites])
								self.target = self.player
								if self.target.hitbox.centerx > self.rendered_sprites.zone_size[0] * 0.5:
									self.target.facing = -1

						if style == 'enemies':
							if col == '0':
								self.walking_enemy = LungingEnemy(self.game, self, 'samurai', (x, y), [self.rendered_sprites, self.updated_sprites])
								self.enemy_sprites.add(self.walking_enemy)

						if style == 'exits':
							exit_number = int(col)
							sprite = Exit(self.game, (x,y-self.game.TILESIZE), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/exit.png', exit_number)
							self.exit_sprites.add(sprite)

						if style == 'objects':			
							if col == '0':
								sprite = Platform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/tiled_icons/0.png', '')
								self.platform_sprites.add(sprite)
							if col == '1':
								sprite = Platform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/tiled_icons/0.png', 'down')
								self.platform_sprites.add(sprite)
							if col == '2':
								sprite = Platform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/tiled_icons/0.png', 'up')
								self.platform_sprites.add(sprite)
							if col == '3':
								sprite = Platform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/tiled_icons/0.png', 'right')
								self.platform_sprites.add(sprite)
							if col == '4':
								sprite = Platform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/tiled_icons/0.png', 'left')
								self.platform_sprites.add(sprite)
							if col == '5':
								sprite = TrickPlatform(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/trick_platform')
								self.trick_platform_sprites.add(sprite)
							if col == '6':
								sprite = SawBlade(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/sawblade.png', 'down')
								self.hazard_sprites.add(sprite)
							if col == '7':
								sprite = SawBlade(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/sawblade.png', 'up')
								self.hazard_sprites.add(sprite)
							if col == '8':
								sprite = SawBlade(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/sawblade.png', 'right')
								self.hazard_sprites.add(sprite)
							if col == '9':
								sprite = SawBlade(self.game, self, (x, y), [self.rendered_sprites, self.updated_sprites], 'imgs/objects/sawblade.png', 'left')
								self.hazard_sprites.add(sprite)

	def collide_npc_dialog(self):
		for sprite in self.npc_sprites:
			if sprite.hitbox.colliderect(self.player.hitbox):
				self.npc_collided = True
				dialog = self.game.dialog_dict[sprite.char]
				if self.game.actions['space'] and not self.dialog_running:
					self.dialog_running = True	
					new_state = Dialogue(self.game, self, sprite.char, dialog)
					new_state.enter_state()
			else:
			 	self.npc_collided = False

	def collide_npc_render_box(self):
		for sprite in self.npc_sprites:
			collided = pygame.sprite.spritecollide(self.target, self.npc_sprites, False)
			if collided and not self.dialog_running and not self.cutscene_running:
				if sprite.hitbox.colliderect(self.player.hitbox): 
				
					if self.trigger_interact_box:
						self.create_interact_box((sprite.hitbox.centerx, sprite.hitbox.centery - sprite.hitbox.height * 1.5))
						self.trigger_interact_box = False
					self.fade_timer += 255/20
					if self.fade_timer >= 255:
						self.fade_timer = 255

			else:
				self.fade_timer -= 255/50
				if self.fade_timer <= 0:
					self.fade_timer = 0
					self.trigger_interact_box = True
					for box in self.interact_box_sprites:
						box.kill()

		for i in self.interact_box_sprites:
			i.image.set_alpha(self.fade_timer)

	def reduce_health(self, amount):
		if not self.target.invincible:
			self.game.current_health -= amount
			if self.game.current_health <= 0:
				self.target.alive = False
				self.target.die()

	def enemy_hit_logic(self):
		if self.attack_sprite:
			if pygame.sprite.spritecollide(self.attack_sprite, self.enemy_sprites, False):
				for enemy in self.enemy_sprites:
					if enemy.hitbox.colliderect(self.attack_sprite) and enemy.alive and self.target.attacking:
						if not enemy.invincible and enemy.alive:
							enemy.invincible = True
							enemy.health -= 1
							if enemy.health <= 0:
								for i in range(enemy.coins_given):
									coin = Coin(self.game, self, enemy.rect.center, [self.visible_sprites, self.active_sprites], 'img/items/coin/')
									self.coin_sprites.add(coin)
								enemy.alive = False
								enemy.die()

	def respawn(self):
		if self.player.alpha <= 100 and not self.player.alive:
			#self.game.current_health = self.game.max_health
			#self.game.current_room = 0
			new_state = Zone(self.game)
			new_state.enter_state()

	def cutscene(self):
		for sprite in self.cutscene_sprites:
			if sprite.rect.colliderect(self.player) and sprite.number not in self.game.cutscenes_completed:
				sprite.kill()
				self.cutscene_running = True
				new_state = Cutscene(self.game, self, sprite.number)
				new_state.enter_state()

	def exit_area(self):
		for sprite in self.exit_sprites:
			if sprite.hitbox.colliderect(self.player.hitbox):
				self.exiting_area = True
				self.game.current_zone = self.game.room_dict[self.game.current_zone][sprite.number]
				self.game.spawn_point = sprite.number

	def run_new_area(self):
		if self.exit_cooldown >= 255:
			self.game.get_area()
			new_state = Zone(self.game)
			new_state.enter_state()
			
	def run_fade(self):
		if self.exiting_area:
			self.player.speed = 0
			self.exit_cooldown += 255/self.game.room_transition_speed
			self.fade_surf.set_alpha(self.exit_cooldown)
			self.surf.blit(self.fade_surf, (0,0))

		elif self.entering_area:
			self.entry_cooldown -= 255/self.game.room_transition_speed
			if self.entry_cooldown <= 0:
				self.entry_cooldown = 0
				self.entering_area = False

			self.fade_surf.set_alpha(self.entry_cooldown)
			self.surf.blit(self.fade_surf, (0,0))
		
	def create_interact_box(self, pos):
		self.interact_box = Interact(self.game, (pos), [self.rendered_sprites, self.updated_spritess])
		self.interact_box_sprites.add(self.interact_box)

	def create_attack(self):
		self.attack_sprite = Attack(self.game, self, self.player, (self.player.hitbox.center), [self.rendered_sprites, self.updated_sprites], self.surf)
		
	def create_special_attack(self):
		self.attack_sprite = SpecialAttack(self.game, self, self.player, (self.player.hitbox.center), [self.rendered_sprites, self.updated_sprites], self.surf)

	def create_yoyo(self):
		self.yoyo_sprite = Yoyo(self.game, self, self.player, (self.player.hitbox.center), [self.rendered_sprites, self.updated_spritess], 'img/card.png')

	def create_yoyo_line(self):
		if self.player.yoyoing:
			pygame.draw.line(self.display_surf, ((self.game.BLACK)), (self.player.hitbox.centerx - self.rendered_sprites.offset[0], self.player.hitbox.centery - self.visible_sprites.offset[1]), \
			(self.yoyo_sprite.rect.centerx - self.rendered_sprites.offset[0], self.yoyo_sprite.rect.centery - self.rendered_sprites.offset[1]), 2)

	def create_gun_blast(self):
		if self.player.shooting:
			GunBlast(self.game, self, (self.player.hitbox.center), [self.rendered_sprites, self.updated_sprites], 'imgs/particles/gun_blast')

	def update(self, actions):
		self.updated_sprites.update()	
		if not self.cutscene_running and not self.dialog_running and self.entry_cooldown < 100:
			self.player.input()
		self.exit_area()
		self.run_new_area()
		self.respawn()
	
	def render(self, display):
		self.rendered_sprites.offset_draw(self.target.rect.center)
		#self.create_yoyo_line()
		#self.collide_npc_render_box()
		self.ui.render()
		self.run_fade()	
		# top debug messages
		self.game.draw_text(display, str(self.player.on_left), ((255,255,255)), 100, (self.game.WIDTH*0.33,40))
		self.game.draw_text(display, 'FPS: ' +str(self.player.state), ((255,255,255)), 100, (self.game.WIDTH*0.5,40))
		self.game.draw_text(display, str(self.player.on_ground), ((255,255,255)), 100, (self.game.WIDTH*0.66,40))

