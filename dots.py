import pygame
import random
import matplotlib.pyplot as plt

pygame.init()

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
        self.color = shape["color"]
        self.signal_to_score = False
        #####
        self.can_charge = 0
    

    def draw(self, screen):
        """called by pygame to render sprite to the screen"""
        pygame.draw.circle(screen, self.color, self.position, self.shape["radius"])
        L = self.position.x-self.shape["radius"]
        H = 4
        T = self.position.y-self.shape["radius"]-H - 5 #padding
        W = self.shape["radius"]*2
        
        pygame.draw.rect(screen, "red", pygame.Rect(L,T,W,H))
        pygame.draw.rect(screen, "green", pygame.Rect(L,T,W*(self.health/self.stats["max_health"]),H))

    def update(self, screen, targets, goal):
        """called by pygame to execute sprite behavior"""
        self.spawn_logic()
        if self.visible:
            self.movement_behavior(targets, goal)
            self.attack_behavior(targets)
            self.reach_goal_logic(goal)
            self.report_if_dead()
            self.draw(screen)


    def spawn_logic(self,dt=1):
        self.spawn_time -= dt
        self.visible = self.spawn_time <= 0


    def movement_behavior(self, target_group:pygame.sprite.Group, goal_position:pygame.Vector2):
        for target in target_group:
            if self.position.distance_to(target.position) < self.stats["vision"]:
                if self.unitType in ["Mele", "Rusher"]:
                    self.move_towards(target.position)
                    break
                elif self.unitType == "Tank":
                    if (target.stats["atk"] - self.stats["def"]) < self.health:
                        self.move_towards(target.position)
                        break
                elif self.unitType == "Defense":
                    if self.can_charge % 50 == 24:
                        self.stats["speed"] *= 2
                        self.color = self.shape["charge_color"]

                    elif self.can_charge % 50 == 49:
                        self.stats["speed"] *= 0.5
                        self.color = self.shape["color"]

                    self.can_charge += 1
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
            if self.position.distance_to(target.position) < max(self.shape["radius"],target.shape["radius"]):
                self.attack(target)


    def attack(self, target):
        target.health -= max(1, self.stats["atk"] - target.stats["def"]) #always do 1 dmg minimum


    def report_if_dead(self):
        global DEATH_LOG
        if self.health <= 0:
            DEATH_LOG.append(self.ID)

    def reach_goal_logic(self, goal):
        GOAL_THRESHOLD = 20
        if self.position.distance_to(goal) < GOAL_THRESHOLD and self.visible:
            self.signal_to_score = True
            self.health = -1
##################################################################################################
# Unit Definitions #

# Mele Unit
mele_shape = {"radius":20}
mele_stats = {"max_health":100, "atk":10, "def":5, "speed":5, "vision":100}

# Tank Unit
tank_shape = {"radius":80}
tank_stats = {"max_health":200, "atk":5, "def":10, "speed":3, "vision":200}

# Rush Unit
rush_shape = {"radius":10}
rush_stats = {"max_health":50, "atk":40, "def":2, "speed":9, "vision":80}

# Defense Unit
defense_shape = {"radius":40, "charge_color":"yellow"}
defense_stats = {"max_health":150, "atk":8, "def":40, "speed":4, "vision":150}

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
    num_defense = 2
    max_spawn_time = 500

    for _ in range(num_mele):
        player_army.add(Unit("Mele",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             mele_shape | {"color": "blue"},
                             mele_stats,
                             random.randint(0, max_spawn_time)))
        enemy_army.add(Unit("Mele",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             mele_shape | {"color": "red"},
                             mele_stats,
                             random.randint(0, max_spawn_time)))
        
    for _ in range(num_tank):
        player_army.add(Unit("Tank",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             tank_shape | {"color": "blue"},
                             tank_stats,
                             random.randint(0, max_spawn_time)))
        enemy_army.add(Unit("Tank",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             tank_shape | {"color": "red"},
                             tank_stats,
                             random.randint(0, max_spawn_time)))
        
    for _ in range(num_rush):
        player_army.add(Unit("Rusher",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             rush_shape | {"color": "blue"},
                             rush_stats,
                             random.randint(0, max_spawn_time)))
        enemy_army.add(Unit("Rusher",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             rush_shape | {"color": "red"},
                             rush_stats,
                             random.randint(0, max_spawn_time)))
        
    for _ in range(num_defense):
        player_army.add(Unit("Defense",
                             pygame.Vector2(0, get_random_y_pos(screen_height)),
                             defense_shape | {"color": "blue"},
                             defense_stats,
                             random.randint(0, max_spawn_time)))
        enemy_army.add(Unit("Defense",
                             pygame.Vector2(screen_width, get_random_y_pos(screen_height)),
                             defense_shape | {"color": "red"},
                             defense_stats,
                             random.randint(0, max_spawn_time)))

    return player_army, enemy_army


FONT = pygame.font.Font(None, 36)
def display_HUD(screen, p_army_size, e_army_size, p_score, e_score):
    global FONT
    # show army count on screen top left
    army_text_p = FONT.render(f"Player Army: {p_army_size}", True, "black")
    army_text_e = FONT.render(f"Enemy Army: {e_army_size}", True, "black")
    screen.blit(army_text_p, (0, 0))
    screen.blit(army_text_e, (0, 40))

    # show scores
    score_text_p = FONT.render(f"Player Score: {p_score}", True, "black")
    score_text_e = FONT.render(f"Enemy Score: {e_score}", True, "black")
    screen.blit(score_text_p, (0, 80))
    screen.blit(score_text_e, (0, 120))


##################################################################################################

# MAIN (all runtime code goes in here)
if __name__ == "__main__":
    try:
        win_log = []

        # Global consts for game state
        screen = pygame.display.set_mode((1920, 1080))
        clock = pygame.time.Clock() 
        dt = 0
        goal_left = pygame.Vector2(0, screen.get_height() / 2)
        goal_right = pygame.Vector2(screen.get_width(), screen.get_height() / 2)

        #global variables for game state
        player_army, enemy_army = reset_game_state(screen.get_height(), screen.get_width())
        player_score = enemy_score = 0

        #running state
        running = True

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player_army, enemy_army = reset_game_state(screen.get_height(), screen.get_width())
                        player_score = enemy_score = 0


            if len(player_army) + len(enemy_army) == 0:
                win_log.append((player_score, enemy_score))
                player_army, enemy_army = reset_game_state(screen.get_height(), screen.get_width())
                player_score = enemy_score = 0
            
            # fill the screen with a color to wipe away anything from last frame
            screen.fill("grey")

            #update all sprites (draw, attack, move, spawn, and death logic within)
            enemy_army.update(screen, player_army, goal_left)
            player_army.update(screen, enemy_army, goal_right)
            

            # update scores
            player_score += sum([int(unit.signal_to_score) for unit in player_army])
            enemy_score += sum([int(unit.signal_to_score) for unit in enemy_army])

            # update HUD info
            display_HUD(screen, len(player_army), len(enemy_army), player_score, enemy_score)

            #remove dead units
            player_army.remove([sprite for sprite in player_army if sprite.ID in DEATH_LOG])
            enemy_army.remove([sprite for sprite in enemy_army if sprite.ID in DEATH_LOG])
            DEATH_LOG = []

            
            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = clock.tick(45) / 1000

    except KeyboardInterrupt:
        from statistics import mean
        P, E = list(zip(*win_log))
        L = len(win_log)
        print()
        print(f"Player {mean(P)}; Enemy {mean(E)}; Win Ratio (P) {mean([1 if p>e else 0 for p,e in win_log])}")

pygame.quit()