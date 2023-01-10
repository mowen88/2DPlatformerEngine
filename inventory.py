import pygame
from state import State

class Inventory(State):
	def __init__(self, game, zone):
		State.__init__(self, game)
		self.game = game
		self.zone = zone
		self.surf = pygame.display.get_surface()
		self.mx, self.my = (0,0)
		self.menu_state = 'Inventory'

		self.coloured_board_offset = self.game.WIDTH * 0.65
		self.colour = self.game.YELLOW
		self.radius = 8

		self.amulet_board_height = self.game.HEIGHT * 0.55
		self.inventory_board_height = self.game.HEIGHT * 0.7
		self.amulet_rows = 2
		self.inventory_rows = 3

		self.board_height = self.amulet_board_height
		self.board_rows = self.amulet_rows
		self.board_cols = 6

		self.black_board_size = (self.game.WIDTH * 0.8, self.board_height)
		self.black_board_pos = (self.game.WIDTH * 0.5 - self.game.WIDTH * 0.4, self.game.HEIGHT * 0.5 - self.game.HEIGHT * 0.35)
		self.coloured_board_pos = (self.coloured_board_offset, self.black_board_pos[1])
		self.coloured_board_size = (self.black_board_pos[0] + self.black_board_size[0] - self.coloured_board_offset, self.board_height)

		self.index = None
		self.amulet_imgs = []
		self.equipped_imgs = []
		self.selection_index = 0
		self.amulet_selected = None
		self.amulet_slot_num = None
		self.returning_amulet = False
		self.return_amulet = None
		self.return_amulet_num = None

		self.slot_size = self.game.TILESIZE * 1.5
		self.slot_surf = pygame.Surface((self.slot_size, self.slot_size))
		self.slot_surf.fill((self.game.BLACK))
		self.slot_surf.set_alpha(150)
		self.slot_rect = self.slot_surf.get_rect()

		self.inventory_button_surf = self.game.font.render(str('   Inventory   '), False, self.game.WHITE)
		self.inventory_button_rect = self.inventory_button_surf.get_rect(center = (self.coloured_board_offset - ((self.coloured_board_offset - self.black_board_pos[0])*0.66), self.black_board_pos[1] + self.slot_size*0.75))
		self.amulet_button_surf = self.game.font.render(str('      Amulets      '), False, self.game.WHITE)
		self.amulet_button_rect = self.amulet_button_surf.get_rect(center = (self.coloured_board_offset - ((self.coloured_board_offset - self.black_board_pos[0])*0.33), self.black_board_pos[1] + self.slot_size*0.75))

		self.description = 'arrow'
		self.description_surf = self.game.small_font.render(str(self.description), False, self.game.BLACK)
		self.description_rect = self.description_surf.get_rect()

		self.amulet_descriptions = {'arrow': ['Provides a ranged weapon upgrade.', 'This will give your grenades a', 'larger blast radius.'],
									 'cat': ['The lucky cat charm is for wealth', 'When this is equipped, you will get', 'more neobit drops from enemies.'], 
									 'cloud': ['This amulet lets you save half', 'of your neobits to the cloud upon','death, instead of losing them all.'], 
									 'doll': ['The lucky doll amulet attracts', 'neobits. When enemies die, their', 'neobits will automatically go to you.'], 
									 'fan': ['Keep you cool with fan amulet.', 'This reduces you dash cooldown,', 'so you can dash more often.'], 
									 'fish': ['Allows you to be more slippery', 'in melee combat, reducing your', 'third strike combo cooldown.'], 
									 'flower': ['A symbol of growth, any shields', 'currently proptecting you will', 'regenerate faster.'], 
									 'sword': ['With the fighting spirit of this', 'amulet, your third melee strike', 'will have twice the power.'], 
									 'tree': ['Another symbol of greater growth,', 'your grenades will regenrate faster', 'with the amulet equipped.'], 
									 'turtle': ["With the spirit of the turtle's tough",'shell, you will be granted longer', 'recovery time between hits.'], 
									 'wind': ['You speed will increase with this', 'amulet equipped, enabling you to', 'run like the wind.'], 
									 'shrine': ['Special amulet from the shrine. When', 'equipped, your special melee attack', 'cooldown will be reduced.']}

		self.amulet_tuples = list(self.amulet_descriptions.items())
		self.confirm_window_showing = False


		for image in self.game.data['amulets']:
			text_img = self.game.font.render(str(image), False, self.game.WHITE)
			item_img = pygame.image.load(f'imgs/ui/items/{image}.png').convert_alpha()
			item_img = pygame.transform.scale(item_img, (self.slot_size, self.slot_size))
			self.amulet_imgs.append(item_img)


		for image in self.game.data['equipped']:
			item_img = pygame.image.load(f'imgs/ui/items/{image}.png').convert_alpha()
			item_img = pygame.transform.scale(item_img, (self.slot_size, self.slot_size))
			self.equipped_imgs.append(item_img)


	def show_description(self):
		
		txt = self.amulet_descriptions[self.description]
		offset = self.game.TILESIZE
		for line in range(len(txt)):
			line_surf =  self.game.small_font.render(str(txt[line]), False, self.game.WHITE)
			line *= offset
			
			light_surf = pygame.image.load('imgs/white_gradient.png').convert_alpha()
			light_surf = pygame.transform.scale(light_surf, (self.slot_size * 2, self.slot_size * 2))
			light_surf.set_alpha(120)
			light_rect =  light_surf.get_rect()

			img_surf = pygame.image.load(f'imgs/ui/inverted_amulet_imgs/{self.description}.png').convert_alpha()
			img_rect = img_surf.get_rect(center = (self.coloured_board_offset + self.coloured_board_size[0] * 0.5, self.coloured_board_pos[1] + self.board_height * 0.33))
			
			light_rect.center = img_rect.center
			self.surf.blit(light_surf, light_rect)
			self.surf.blit(img_surf, img_rect)
			
			line_rect = line_surf.get_rect(midleft = (self.coloured_board_offset + self.game.TILESIZE * 0.5, (light_rect.bottom) + line + offset))	
			self.surf.blit(line_surf, line_rect)
			self.surf.blit(line_surf, line_rect)


	def return_to_game_logic(self):
		text_surf = self.game.font.render(str('   < Return to game    '), False, self.game.WHITE)
		text_rect = text_surf.get_rect(bottomleft = (self.game.WIDTH * 0.025, self.game.HEIGHT - (self.game.HEIGHT * 0.05)))
		self.surf.blit(text_surf, text_rect)
		if text_rect.collidepoint(self.mx, self.my) and not self.confirm_window_showing:
			pygame.draw.rect(self.surf, self.game.WHITE, text_rect, 2)
			if pygame.mouse.get_pressed()[0] == 1:
				self.exit_state()


	def menu_state_button_logic(self):
		mouse = pygame.mouse.get_pressed(num_buttons=5)

		self.surf.blit(self.inventory_button_surf, self.inventory_button_rect)
		self.surf.blit(self.amulet_button_surf, self.amulet_button_rect)

		if self.inventory_button_rect.collidepoint(self.mx, self.my):
			pygame.draw.rect(self.surf, self.game.WHITE, self.inventory_button_rect, 2)
			if pygame.mouse.get_pressed()[0] == 1:
				self.menu_state = 'Inventory'


		elif self.amulet_button_rect.collidepoint(self.mx, self.my):
			pygame.draw.rect(self.surf, self.game.WHITE, self.amulet_button_rect, 2)
			if pygame.mouse.get_pressed()[0] == 1:
				self.menu_state = 'Amulets'


	def show_equipped_slots(self):
		self.equipped_index = -1
		offset = self.game.TILESIZE * 2
		for slot in range(self.game.max_equip_slots):
			slot *= offset
			self.equipped_index += 1
			slot_surf = pygame.Surface((self.slot_size, self.slot_size))
			slot_surf.fill((self.game.BLACK))
			slot_surf.set_alpha(150)
			slot_rect = slot_surf.get_rect(topleft = (self.black_board_pos[0] + self.black_board_size[0] - slot - offset, (self.black_board_pos[1] + self.black_board_size[1] + 20)))
			self.surf.blit(slot_surf, slot_rect)
			if self.equipped_index <= len(self.equipped_imgs)-1:
				self.surf.blit(self.equipped_imgs[self.equipped_index], slot_rect.topleft)
			
				if slot_rect.collidepoint(self.mx, self.my) and not self.confirm_window_showing:
					self.description = self.game.data['equipped'][self.equipped_index]
					pygame.draw.rect(self.surf, self.game.WHITE, slot_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:

						# glow_surf = pygame.Surface((self.slot_size, self.slot_size))
						# glow_surf.fill((self.game.WHITE))
						# glow_surf.set_alpha(100)
						# glow_rect = glow_surf.get_rect(topleft = slot_rect.topleft)
						# self.surf.blit(glow_surf, glow_rect)

						self.return_amulet = self.game.data['equipped'][self.equipped_index]
						self.return_amulet_num = self.equipped_index
						self.confirm_window_showing = True
						self.returning_amulet = True

		available_slots_left_text_surf = self.game.font.render(str('Amulets equipped >'), False, self.game.WHITE)
		available_slots_left_text_rect = available_slots_left_text_surf.get_rect(midright = (self.black_board_pos[0] + self.black_board_size[0] - offset * self.game.max_equip_slots - (self.slot_size * 0.5), (self.black_board_pos[1] + self.black_board_size[1] + 20 + (self.slot_size * 0.5))))
		self.surf.blit(available_slots_left_text_surf, available_slots_left_text_rect)


	def show_amulets(self, left, right, top, bottom):
		self.index = -1
		for x in range(left + self.game.TILESIZE, right - self.game.TILESIZE, (right - left -self.game.TILESIZE)//self.board_cols):
			for y in range(top + int(self.slot_size + self.game.TILESIZE), bottom - self.game.TILESIZE, (bottom - int(self.slot_size + self.game.TILESIZE) - top)//self.board_rows):
				slot = pygame.draw.rect(self.surf, self.game.GREY, (x, y, self.slot_size, self.slot_size))
				self.index += 1
				if self.index <= len(self.amulet_imgs)-1:
					self.surf.blit(self.amulet_imgs[self.index], slot.topleft)

					if not self.confirm_window_showing:
						if slot.collidepoint(self.mx, self.my):
							self.description = self.game.data['amulets'][self.index]
							pygame.draw.rect(self.surf, self.game.WHITE, slot, 2)
							if pygame.mouse.get_pressed()[0] == 1 and self.menu_state == 'Amulets':
								self.amulet_selected = self.game.data['amulets'][self.index]
								self.amulet_slot_num = self.index
								self.confirm_window_showing = True

					
	def confirm_window(self):
		if self.confirm_window_showing:

			box_surf = pygame.Surface((self.game.WIDTH * 0.6,self.game.HEIGHT * 0.6))
			box_surf.fill((self.game.GREY))
			box_rect = box_surf.get_rect(center = (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.5))

			yes_surf = self.game.font.render(str('      Yes      '), False, self.game.WHITE)
			yes_rect = yes_surf.get_rect(center = (box_rect.centerx - (self.game.WIDTH * 0.1), box_rect.centery + (self.game.HEIGHT * 0.1)))

			cancel_surf = self.game.font.render(str('    Cancel    '), False, self.game.WHITE)
			cancel_rect = cancel_surf.get_rect(center = (box_rect.centerx + (self.game.WIDTH * 0.1), box_rect.centery + (self.game.HEIGHT * 0.1)))

			back_surf = self.game.font.render(str('    Back    '), False, self.game.WHITE)
			back_rect = back_surf.get_rect(center = (box_rect.centerx, box_rect.centery + (self.game.HEIGHT * 0.1)))

			self.surf.blit(box_surf, box_rect, special_flags = pygame.BLEND_MULT)

			
			if self.returning_amulet:
				msg = f'Do you want to return the {self.return_amulet} amulet?'
				return_item_msg = 'Do you want to unequip this amulet?'
				self.surf.blit(yes_surf, yes_rect)
				self.surf.blit(cancel_surf, cancel_rect)
				if yes_rect.collidepoint(self.mx, self.my):
					pygame.draw.rect(self.surf, self.game.WHITE, yes_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:
						self.amulet_imgs.append(self.equipped_imgs[self.return_amulet_num])
						self.game.data['amulets'].append(self.return_amulet)
						self.equipped_imgs.pop(self.return_amulet_num)
						self.game.data['equipped'].remove(self.return_amulet)

						self.confirm_window_showing = False
						self.returning_amulet = False

				elif cancel_rect.collidepoint(self.mx, self.my):
					pygame.draw.rect(self.surf, self.game.WHITE, cancel_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:
						self.confirm_window_showing = False
						self.returning_amulet = False


			elif len(self.equipped_imgs) >= self.game.max_equip_slots:
				msg = 'No more space available!'
				self.surf.blit(back_surf, back_rect)
				if back_rect.collidepoint(self.mx, self.my):
					pygame.draw.rect(self.surf, self.game.WHITE, back_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:		

						self.confirm_window_showing = False

			else:
				msg = f'Add the {self.amulet_selected} amulet to your equipment?'
				return_item_msg = 'Do you want to unequip this amulet?'
				self.surf.blit(yes_surf, yes_rect)
				self.surf.blit(cancel_surf, cancel_rect)
				if yes_rect.collidepoint(self.mx, self.my):
					pygame.draw.rect(self.surf, self.game.WHITE, yes_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:
						#item_to_remove = self.amulet_imgs.index(self.amulet_selected)
						if len(self.equipped_imgs) <= self.game.max_equip_slots:
							self.equipped_imgs.append(self.amulet_imgs[self.amulet_slot_num])
							self.game.data['equipped'].append(self.amulet_selected)
							self.amulet_imgs.pop(self.amulet_slot_num)
							self.game.data['amulets'].remove(self.amulet_selected)

						# appends removed item to the end of the list :)
						# return_item = pygame.image.load(f'imgs/ui/items/{self.amulet_selected}.png').convert_alpha()
						# return_item = pygame.transform.scale(return_item, (self.slot_size, self.slot_size))
						# if len(self.game.data['amulets']) < self.game.max_equip_slots:
						# 	self.amulet_imgs.append(return_item)
						# 	self.game.data['amulets'].append('boots')

						self.confirm_window_showing = False

				elif cancel_rect.collidepoint(self.mx, self.my):
					pygame.draw.rect(self.surf, self.game.WHITE, cancel_rect, 2)
					if pygame.mouse.get_pressed()[0] == 1:
						self.confirm_window_showing = False

			msg_surf = self.game.font.render(str(msg), False, self.game.WHITE)
			msg_rect = msg_surf.get_rect(midtop = (box_rect.centerx, box_rect.y + (box_rect.height * 0.33)))

			self.surf.blit(msg_surf, msg_rect)


	def show_menu_state(self, state, display):
		if state == 'Inventory':
			self.colour = self.game.LIGHT_GREEN
			self.board_height = self.inventory_board_height
			self.board_rows = self.inventory_rows
			pygame.draw.rect(self.surf, self.game.WHITE, self.inventory_button_rect, 2)

		elif state == 'Amulets':
			self.colour = self.game.ORANGE
			self.board_height = self.amulet_board_height
			self.board_rows = self.amulet_rows
			pygame.draw.rect(self.surf, self.game.WHITE, self.amulet_button_rect, 2)
			self.show_equipped_slots()
			self.show_description()
			self.confirm_window()
		
	def update(self, actions):
		self.mx, self.my = pygame.mouse.get_pos()

		if actions['i']:
			actions['z'] = True # stop it being false where the sword is used immediately when exiting this state
			self.exit_state()
		actions['i'] = False


	def render(self, display):
		self.prev_state.render(display)
		pygame.draw.rect(display, self.game.BLACK, (self.black_board_pos, (self.black_board_size[0], self.board_height)), border_radius=(self.radius))
		pygame.draw.rect(display, self.colour, (self.coloured_board_pos, (self.coloured_board_size[0], self.board_height)), border_top_right_radius=(self.radius), border_bottom_right_radius=(self.radius))
		self.show_amulets(int(self.black_board_pos[0]), int(self.coloured_board_pos[0]), int(self.black_board_pos[1]), int((self.black_board_pos[1]+ self.board_height)))
		self.show_menu_state(self.menu_state, display)
		self.menu_state_button_logic()
		self.return_to_game_logic()
	
		#print(self.equipped_imgs)
		#print(self.description)
		#print(self.amulet_imgs)
		#print(self.game.data['amulets'])
	
		
		
		