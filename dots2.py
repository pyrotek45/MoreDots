import pygame
import random

# Unit Class ############################################################################################
DEATH_LOG:list[int] = [] # Holds the IDs of Units in need of killing

class Unit(pygame.sprite.Sprite):
    _id: int = 0


    @classmethod
    def assign_id(cls) -> int:
        Unit._id += 1
        return Unit._id - 1


    def __init__(self, unit_type:str, position:pygame.Vector2, shape:dict, stats:dict, spawn_time:int):
        pygame.sprite.Sprite.__init__(self)
        self.ID = Unit.assign_id()
        #####
        self.position:pygame.Vector2 = position
        self.shape:dict = shape
        self.stats:dict = stats
        self.unitType:str = unit_type
        #####
        self.visible = False
        self.spawn_time = spawn_time
        self.health = stats["max_health"]
    

    def draw(self, screen):
        """called by pygame to render sprite to the screen"""
        pygame.draw.circle(screen, self.shape["color"], self.position, self.shape["radius"])


    def update(self,targets, goal):
        """called by pygame to execute sprite behavior"""
        self.movement_behavior(targets, goal)
        self.attack_behavior(targets)
        self.report_if_dead()


    def movement_behavior(self, target_group:pygame.sprite.Group, goal_position:pygame.Vector2):
        for target in target_group:
            if self.position.distance_to(target.position) < self.vision:
                if self.unitType in ["Mele", "Rusher"]:
                    self.move_towards(target.position)
                    break
                elif self.unitType == "Tank":
                    if target.attack_power < self.health:
                        self.move_towards(target.position)
                        break
        else:
            self.move_towards(goal_position)


    def move_towards(self, goal_position):
        direction = goal_position - self.position
        if direction.length() > 0:
            direction.normalize_ip()
        self.position += direction * self.stats["speed"]


    def attack_behavior(self, target_group:pygame.sprite.Group):
        for target in target_group:
            if self.position.distance_to(target.position) < self.shape["radius"]:
                self.attack(target)


    def attack(self, target):
        target.health -= max(1, self.stats["atk"] - target.stats["def"]) #always do 1 dmg minimum


    def report_if_dead(self):
        global DEATH_LOG
        if self.health <= 0:
            DEATH_LOG.append(self.ID)


##################################################################################################
# Unit Definitions #

# Mele Unit
mele_shape = {"color":0, "radius":0}
mele_stats = {"max_health":0, "atk":0, "def":0, "speed":0, "vision":0}

# Tank Unit
tank_shape = {"color":0, "radius":0}
tank_stats = {"max_health":0, "atk":0, "def":0, "speed":0, "vision":0}

# Rush Unit
rush_shape = {"color":0, "radius":0}
rush_stats = {"max_health":0, "atk":0, "def":0, "speed":0, "vision":0}

##################################################################################################

# MAIN (all runtime code goes in here)
if __name__ == "__main__":
    pygame.init()
    test_screen = pygame.display.set_mode((1280, 720))
    test_pos = pygame.Vector2(test_screen.get_width() / 2, test_screen.get_height() / 2)
    test_spawn_time = random.randint(0,500)

    test_unit = Unit("test_type", test_pos, mele_shape, mele_stats, test_spawn_time)