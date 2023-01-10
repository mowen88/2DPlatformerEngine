
import os, time, pygame, csv, json
from os import walk
from csv import reader
from title import Title

class Game():
	def __init__(self):

		pygame.init()

		self.ASPECT_RATIO = 9/16
		self.TILESIZE = 16
		self.WIDTH = 480
		self.HEIGHT = self.WIDTH * self.ASPECT_RATIO
		self.FPS = 60
		self.BLACK = ((9, 9, 14))
		self.GREY = ((26,28,38))
		self.WHITE = ((255, 255, 255)) 
		self.BLUE = ((99, 129, 222))
		self.LIGHT_BLUE = ((113, 181, 219))
		self.RED = ((112, 21, 31))
		self.ORANGE = ((227, 133, 36))
		self.PINK = ((195, 67, 92))
		self.GREEN = ((88, 179, 150))
		self.LIGHT_GREEN = ((106, 226, 145))
		self.CYAN = ((0, 255, 255))
		self.MAGENTA = ((153, 60, 139))
		self.YELLOW = ((224, 225, 146))
		self.clock = pygame.time.Clock()
		#self.monitor_info = pygame.display.Info()
		self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN|pygame.SCALED)
		#self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

		self.running, self.playing = True, True
		self.actions = {'F4': False, 'left': False, 'right': False, 'up': False, 'down': False, 'return': False, 'backspace': False, 'tab': False,\
		 'space': False, 'x': False, 'z': False, 'c': False, 'm': False, 'i': False, 'escape': False, 'left_click': False, 'right_click': False, 'scroll_up': False, 'scroll_down': False} 
		
		# with open('data_dicts/dialogue.txt') as f: self.dialog_dict = eval(f.read())

		self.cutscene_data = {0:(pygame.Rect(300, 400, 20, 100))}
		self.cutscenes_completed = []
		self.screen_shaking = False

		self.room_dict = {
		'test':{1: 'left_room', 2: 'left_room'},
		'left_room':{1:'test', 2: 'left_room'},
		'right_room':{1:'test'},
		}
		self.areas = {0: ['test','test3','test4', ], 1: ['left_room']}
		
		self.data = {'shoot_cooldown': 400, 'stamina_refresh_rate': 0.2, 'shield_refresh_rate': 0.06, 'max_health': 4, 'max_bullets': 6, 'coins': 0, 'bag': False, 'max_items': 3,

					'items': ['green_shield', 'blue_shield'], 

					'amulets':['arrow', 'cat', 'cloud', 'doll', 'fan', 'fish', 'flower', 'sword', 'tree', 'turtle', 'wind', 'shrine'],
					'equipped':[]}

		self.current_zone = 'test'
		self.current_area = None
		self.room_transition_speed = 20
		self.spawn_point = 0

		self.current_health = self.data['max_health']

		self.current_bullets = self.data['max_bullets']

		self.max_equip_slots = 4
		self.stamina = 100
		self.green_shield = 100
		self.blue_shield = 100

		self.stack = []
		self.font = pygame.font.Font('font/UASQUARE.ttf', 16)
		self.small_font = pygame.font.Font('font/UASQUARE.ttf', 8)

		self.get_area()
		self.load_states()
		
	def get_area(self):
		for i in self.areas.values():
			if self.current_zone in i:
				self.current_area = list(self.areas.values()).index(i)

		# for rooms in self.areas.values():
		# 	if self.current_zone in rooms:
				# self.current_area = list(self.areas.keys())[rooms.index(self.current_zone)]

	def game_loop(self):
		self.clock.tick(self.FPS)
		self.show_fps = str(int(self.clock.get_fps()))
		self.get_events()
		self.update()
		self.render()

	def get_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				self.playing = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.actions['escape'] = True
					self.running = False
					self.playing = False
				elif event.key == pygame.K_F4:
					self.actions['F4'] = True
				elif event.key == pygame.K_TAB:
					self.actions['tab'] = True
				elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
					self.actions['left'] = True
				elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					self.actions['right'] = True
				elif event.key == pygame.K_UP or event.key == pygame.K_w:
					self.actions['up'] = True
				elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
					self.actions['down'] = True
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = True
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = True
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = True
				elif event.key == pygame.K_x:
					self.actions['x'] = True
				elif event.key == pygame.K_z or event.key == pygame.K_RSHIFT:
					self.actions['z'] = True
				elif event.key == pygame.K_c:
					self.actions['c'] = True
				elif event.key == pygame.K_m:
					self.actions['m'] = True
				elif event.key == pygame.K_i:
					self.actions['i'] = True

			if event.type == pygame.KEYUP:
				
				if event.key == pygame.K_F4:
					self.actions['F4'] = False
				elif event.key == pygame.K_TAB:
					self.actions['tab'] = False
				elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
					self.actions['left'] = False
				elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					self.actions['right'] = False
				elif event.key == pygame.K_UP or event.key == pygame.K_w:
					self.actions['up'] = False
				elif event.key == pygame.K_DOWN  or event.key == pygame.K_s: 
					self.actions['down'] = False
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = False
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = False
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = False
				elif event.key == pygame.K_x:
					self.actions['x'] = False
				elif event.key == pygame.K_z or event.key == pygame.K_RSHIFT:
					self.actions['z'] = False
				elif event.key == pygame.K_c:
					self.actions['c'] = False
				elif event.key == pygame.K_m:
					self.actions['m'] = False
				elif event.key == pygame.K_i:
					self.actions['i'] = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.actions['left_click'] = True
				elif event.button == 3:
					self.actions['right_click'] = True
				elif event.button == 4:
					self.actions['scroll_down'] = True
				elif event.button == 2:
					self.actions['scroll_up'] = True

			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.actions['left_click'] = False
				elif event.button == 3:
					self.actions['right_click'] = False
				elif event.button == 4:
					self.actions['scroll_down'] = False
				elif event.button == 2:
					self.actions['scroll_up'] = False

	def update(self):
		self.stack[-1].update(self.actions)

	def render(self):
		self.stack[-1].render(self.screen)
		pygame.display.flip()

	def load_states(self):
		self.title_screen = Title(self)
		self.stack.append(self.title_screen)

	def draw_text(self, surf, text, colour, size, pos):
		text_surf = self.font.render(text, True, colour, size)
		text_rect = text_surf.get_rect(center = pos)
		surf.blit(text_surf, text_rect)

	def import_csv(self, path):
		room_map = []
		with open(path) as map:
			room = reader(map, delimiter=',')
			for row in room:
				room_map.append(list(row))

		return room_map

	def import_folder(self, path):
		surf_list = []

		for _, __, img_files in walk(path):
			for img in img_files:
				full_path = path + '/' + img
				img_surf = pygame.image.load(full_path).convert_alpha()
				surf_list.append(img_surf)

		return surf_list

	def reset_keys(self):
		for key_pressed in self.actions:
			self.actions[key_pressed] = False
		
if __name__ == "__main__":
	g = Game()
	while g.running:
		g.game_loop()