import pygame
import random

class Unit(pygame.sprite.Sprite):
    def __init__(self, unit_type:str, position:pygame.Vector2, shape:dict, stats:dict, spawn_time:int):
        pygame.sprite.Sprite.__init__(self)

        self.position:pygame.Vector2 = position
        self.shape:dict = shape
        self.stats:dict = stats
        self.unitType:str = unit_type
        self.visible = False
        self.spawn_time = spawn_time

    def draw(self, screen):
        pygame.draw.circle(screen, self.shape["color"], self.position, self.shape["radius"])


mele_shape = {"color":0, "radius":0}
mele_stats = {"health":0, "atk":0, "def":0, "speed":0, "vision":0}

pygame.init()
test_screen = pygame.display.set_mode((1280, 720))
test_pos = pygame.Vector2(test_screen.get_width() / 2, test_screen.get_height() / 2)
test_spawn_time = random.randint(0,500)

test_unit = Unit("test_type", test_pos, mele_shape, mele_stats, test_spawn_time)