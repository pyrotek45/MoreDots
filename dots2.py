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
mele_shape = {"radius":20}
mele_stats = {"max_health":100, "atk":10, "def":5, "speed":5, "vision":100}

# Tank Unit
tank_shape = {"radius":30}
tank_stats = {"max_health":200, "atk":20, "def":10, "speed":3, "vision":100}

# Rush Unit
rush_shape = {"radius":5}
rush_stats = {"max_health":50, "atk":40, "def":2, "speed":8, "vision":100}

##################################################################################################
def get_random_y_pos(screen_height):
    return screen_height*random.random()


def reset_game_state(screen_height, screen_width):
    """resets the game state (total erasure of all data)"""
    player_army = pygame.sprite.Group()
    enemy_army = pygame.sprite.Group()

    num_mele = 10
    num_tank = 5
    num_rush = 15

    for _ in range(num_mele):
        player_army.add(Unit("Mele",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             mele_shape | {"color": "blue"},
                             mele_stats,
                             random.randint(500)))
        enemy_army.add(Unit("Mele",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             mele_shape | {"color": "red"},
                             mele_stats,
                             random.randint(500)))
        
    for _ in range(num_tank):
        player_army.add(Unit("Tank",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             tank_shape | {"color": "blue"},
                             tank_stats,
                             random.randint(500)))
        enemy_army.add(Unit("Tank",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             tank_shape | {"color": "red"},
                             tank_stats,
                             random.randint(500)))
        
    for _ in range(num_rush):
        player_army.add(Unit("Rush",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             rush_shape | {"color": "blue"},
                             rush_stats,
                             random.randint(500)))
        enemy_army.add(Unit("Mele",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             rush_shape | {"color": "red"},
                             rush_stats,
                             random.randint(500)))

    return player_army, enemy_army



##################################################################################################

# MAIN (all runtime code goes in here)
if __name__ == "__main__":
    pygame.init()

    # Global Variables for game state
    screen = pygame.display.set_mode((1280, 720))
    goal_left = pygame.Vector2(0, screen.get_height() / 2)
    goal_right = pygame.Vector2(screen.get_width(), screen.get_height() / 2)

    player_army, enemy_army = reset_game_state(screen.get_height(), screen.get_width())