from player import Player 

class FSM(Player):
	def __init__(self, state):
		super().__init__(groups)

	def physics(self):
		self.hitbox.x += self.vel.x 
		self.wall_slide()
		self.x_collisions()
		self.apply_gravity()
		self.hitbox.y += self.vel.y 
		self.y_collisions()	
		self.rect.center = self.hitbox.center
		self.stop_at_edge_of_room()
		self.cooldowns()