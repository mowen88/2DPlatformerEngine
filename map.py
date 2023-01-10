import pygame
from state import State

class zoneSprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf):
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.vel = pygame.math.Vector2()


class Map(State):
	def __init__(self, game, zone):
		State.__init__(self, game)
		self.game = game
		self.zone = zone
		self.display_surf = pygame.display.get_surface()
		pos = (self.game.WIDTH // 12, self.game.HEIGHT // 12) # split the screen into 12x12 grid to place zone sprites easily
		

		self.zones = {
		'test': zoneSprite((pos[0] * 8, pos[1] * 4), 'zones/test/map_piece.png'),
		'left_room': zoneSprite((pos[0] * 8, pos[1] * 4), 'zones/left_room/map_piece.png'),
		'right_room': zoneSprite((pos[0] * 4, pos[1] * 4), 'zones/test/map_piece.png')
		}
		

		marker_offset_x = (self.zones[self.game.current_zone].rect.width * (self.zone.player.hitbox.centerx/self.zone.rendered_sprites.zone_size[0])) * self.game.SCALE
		marker_offset_y = (self.zones[self.game.current_zone].rect.height * (self.zone.player.hitbox.centery/self.zone.rendered_sprites.zone_size[1])) * self.game.SCALE


		marker_pos_x = self.zones[self.game.current_zone].rect.x + marker_offset_x
		marker_pos_y = self.zones[self.game.current_zone].rect.y + marker_offset_y
		self.marker_pos = (marker_pos_x, marker_pos_y)

		# player marker
		self.marker_surf = pygame.image.load('imgs/ui/marker.png').convert_alpha()
		self.marker_rect = self.marker_surf.get_rect(center = self.marker_pos)
		# self.icon_rect = self.marker_surf.get_rect(center = (self.game.WIDTH //2 - 120, self.game.HEIGHT - 192))
	
	def show_zones(self):
		for sprite in self.zones.values():
			sprite.image = pygame.transform.scale(sprite.image, (sprite.rect.width * self.game.SCALE, sprite.rect.height * self.game.SCALE))
			self.display_surf.blit(sprite.image, sprite.rect)


	def update(self, actions):
		if actions['m']:
			actions['z'] = True
			self.exit_state()
		actions['m'] = False

	def render(self, display):
		self.display_surf.fill(self.game.PINK)
		# self.prev_state.prev_state.render(display)
		#self.prev_state.render(display)

		self.show_zones()
		self.display_surf.blit(self.marker_surf, self.marker_rect)


		

	




		





	