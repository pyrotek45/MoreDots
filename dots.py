# global imports
import pygame
from random import random


# pygame setup #TODO can we make a custom game class to house all of the pygame boilerplate?
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

####
# Game object Handler and Class

OBJECTS = []




### reconx game where you have circles that fight each other in a 2d space
### is like watching a war of ants
### the goal is to have a better unit composition and strategy to win the game

class Unit:
    def __init__(self, name, position, drawFunc, health, attack_power, defense, speed, unitType, spawnTime) -> None:
        self.name = name
        self.position = position
        self.draw = drawFunc
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.speed = speed
        self.unitType = unitType
        self.vision = 100
        self.visible = False
        self.spawnTime = spawnTime

    def move(self, target) -> None:
        # move towards target
        direction = target - self.position
        if direction.length() > 0:
            direction.normalize_ip()
        self.position += direction * self.speed

    def attack(self, target:"Unit") -> None:
        target.take_damage(self.attack_power)

    def take_damage(self, damage) -> None:
        self.health -= damage

    def die(self) -> None:
        print(f"Unit {self.name} died")

    def do_move_as_type(self, target_list:list["Unit"], goalPos) -> None:
        for target in target_list:
            if self.position.distance_to(target.position) < self.vision:
                if self.unitType in ["Mele", "Rusher"]:
                    self.move(target.position)
                    break
                elif self.unitType == "Tank":
                    if target.attack_power < self.health:
                        self.move(target.position)
                        break
        else:
            self.move(goalPos)


    def do_attack_as_type(self,targets:list["Unit"]):
        global OBJECTS #TODO: make an object handler class and pass that as a parameter here
        match self.unitType:
            case "Melee":
                for target in targets:
                    if self.position.distance_to(target.position) < 20: #TODO: what is this radius? can we make it an object property?
                        #self.attack(target)#TODO: targets take twice dammage because this and the following call do the same thing
                        target.take_damage(self.attack_power)
                        if target.health <= 0:
                            target.die()
                            targets.remove(target)#TODO: this is bad to do in a loop where we are iterating over the list
                            # remove from OBJECTS
                            OBJECTS.remove(target)
            case "Tank":
                for target in targets:
                    if self.position.distance_to(target.position) < 20:
                        #self.attack(target)
                        target.take_damage(self.attack_power)
                        if target.health <= 0:
                            target.die()
                            targets.remove(target)
                            # remove from OBJECTS
                            OBJECTS.remove(target)
            case "Rusher":
                for target in targets:
                    if self.position.distance_to(target.position) < 5:
                        #self.attack(target)
                        target.take_damage(self.attack_power)
                        if target.health <= 0:
                            target.die()
                            targets.remove(target)
                            # remove from OBJECTS
                            OBJECTS.remove(target) 

player_army:list[Unit] = []
enemy_army:list[Unit] = []

player_score = 0
enemy_score = 0
# player army spawns on left side in random positions
# enemy army spawns on right side in random positions
def setup():

    global player_army, enemy_army, OBJECTS, player_score, enemy_score #TODO global badness
    player_army = []
    enemy_army = []
    player_score = 0
    enemy_score = 0
    OBJECTS = [] #TODO: why is objects cleared out when we add things into it in the global scope?

    for i in range(10):
        # player on left side
        player_pos = pygame.Vector2(0, screen.get_height()*random())
        def playerDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "blue", obj.position, 20)
        player_army.append(Unit("Player", player_pos, playerDraw, 100, 10, 5, 5, "Melee", random() * 500))

        enemy_pos = pygame.Vector2(screen.get_width(), screen.get_height()*random())
        def enemyDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "red", obj.position, 20)
        enemy_army.append(Unit("Enemy", enemy_pos, enemyDraw, 100, 10, 5, 5, "Melee", random() * 500))

    ## add new unit type tank, slow, high health, high attack, low speed, gains speed after killing enemy
    for i in range(5):
        # player on left side
        player_pos = pygame.Vector2(0, screen.get_height()*random())
        def playerDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "blue", obj.position, 30)
        player_army.append(Unit("Player", player_pos, playerDraw, 200, 20, 10, 3, "Tank", random() * 500))

        enemy_pos = pygame.Vector2(screen.get_width(), screen.get_height()*random())
        def enemyDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "red", obj.position, 30)
        enemy_army.append(Unit("Enemy", enemy_pos, enemyDraw, 200, 20, 10, 3, "Tank", random() * 500))

    ## add new unit type, rusher, high speed, low health, high attack, low defense, dies on contact
    for i in range(15):
        # player on left side
        player_pos = pygame.Vector2(0, screen.get_height()*random())
        def playerDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "blue", obj.position, 5)
        player_army.append(Unit("Player", player_pos, playerDraw, 50, 40, 2, 8, "Rusher", random() * 500))

        enemy_pos = pygame.Vector2(screen.get_width(), screen.get_height()*random())
        def enemyDraw(obj):
            if obj.visible: 
                pygame.draw.circle(screen, "red", obj.position, 5)
        enemy_army.append(Unit("Enemy", enemy_pos, enemyDraw, 50, 40, 2, 8, "Rusher", random() * 500))

    OBJECTS += player_army
    OBJECTS += enemy_army

# need to update army positions based on unit type and strategy
goalPos_left = pygame.Vector2(0, screen.get_height() / 2)
goalPos_right = pygame.Vector2(screen.get_width(), screen.get_height() / 2)

def update_game() -> None:
    """
    update game logic \n
    update unit positions \n
    move to closest enemy \n
    goal is other right side of screen, not random just right side of screen
    """
    global player_score, enemy_score
    ## need to stagger spawning of units, into random groups of 5 , could use choice till no more units left
    # decrement spawn time for each unit and spawn if 0 or less
    for unit in player_army:
        unit.spawnTime -= 1
        unit.visible = unit.spawnTime <= 0

    for unit in enemy_army:
        unit.spawnTime -= 1
        unit.visible = unit.spawnTime <= 0

    #TODO: pretty sure the player always wins because their move and attack calls are handled first    
    for unit in player_army: #TODO: combine all player_army loops into one loop
        if not unit.visible:
            continue
        unit.do_move_as_type(enemy_army,goalPos_right)

    
    for unit in enemy_army:
        if not unit.visible:
            continue
        unit.do_move_as_type(player_army,goalPos_left)

    # update unit attacks
    ## if enemy in range, attack, melee units kill on contact
    for player in player_army:
        if not player.visible:
            continue
        player.do_attack_as_type(enemy_army)

    for enemy in enemy_army:
        if not enemy.visible:
            continue
        enemy.do_attack_as_type(player_army)


    # remove dead units from army #TODO: this logic exists in do_attack_as_type. figure out the best way to handle it and do it only once
    for player in player_army:
        if player.health <= 0:
            player.die()
            player_army.remove(player)
            OBJECTS.remove(player)

    for enemy in enemy_army:
        if enemy.health <= 0:
            enemy.die()
            enemy_army.remove(enemy)
            OBJECTS.remove(enemy)
    
    # if reached goal , make unit not visible
    for unit in player_army:
        if unit.position.distance_to(goalPos_right) < 20 and unit.visible:
            player_score += 1
            # remove from army
            player_army.remove(unit)
            OBJECTS.remove(unit)


    for unit in enemy_army:
        if unit.position.distance_to(goalPos_left) < 20 and unit.visible:
            enemy_score += 1
            # remove from army
            enemy_army.remove(unit)
            OBJECTS.remove(unit)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                setup()
        # check for mouse click event
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if left mouse button clicked
            if event.button == 1:
                # set player position to mouse position
                player_pos = pygame.Vector2(event.pos)
                
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("green")

    update_game()

    # show army count on screen top left
    army_font = pygame.font.Font(None, 36)
    army_text = army_font.render(f"Player Army: {len(player_army)}", True, "black")
    screen.blit(army_text, (0, 0))

    army_text = army_font.render(f"Enemy Army: {len(enemy_army)}", True, "black")
    screen.blit(army_text, (0, 40))

    # show scores
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render(f"Player Score: {player_score}", True, "black")
    screen.blit(score_text, (0, 80))

    score_text = score_font.render(f"Enemy Score: {enemy_score}", True, "black")
    screen.blit(score_text, (0, 120))

    _ = [obj.draw(obj) for obj in OBJECTS]
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()