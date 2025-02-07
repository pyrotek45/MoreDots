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

class GameObject:
    def __init__(self, name, position, drawFunc) -> None:
        self.name = name
        self.position = position
        self.draw = drawFunc

####
# init game objects
goalPos = pygame.Vector2(screen.get_width()*random(), screen.get_height()*random())
goalDraw = lambda obj: pygame.draw.circle(screen, "green", obj.position, 80)
OBJECTS.append(GameObject("Goal", goalPos, goalDraw))

####

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

player_army = []
enemy_army = []

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
    OBJECTS = []

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

def update_game() -> None:
    global player_score, enemy_score
    # update game logic
    # update unit positions
    # move to closest enemy
    # goal is other right side of screen, not random just right side of screen

    ## need to stagger spawning of units, into random groups of 5 , could use choice till no more units left
    # decrement spawn time for each unit and spawn if 0 or less
    for unit in player_army:
        unit.spawnTime -= 1
        unit.visible = unit.spawnTime <= 0

    for unit in enemy_army:
        unit.spawnTime -= 1
        unit.visible = unit.spawnTime <= 0



    goalPos = pygame.Vector2(screen.get_width(), screen.get_height() / 2)
    for unit in player_army:
        if not unit.visible:
            continue
        match unit.unitType:
            case "Melee":
                # find closest enemy within vision range, otherwise move to goal
                for enemy in enemy_army:
                    if unit.position.distance_to(enemy.position) < unit.vision:
                        unit.move(enemy.position)
                        break
                else:
                    unit.move(goalPos)
            case "Tank":
                # will attack closest enemy within vision range if their damage is higher than their health
                for enemy in enemy_army:
                    if unit.position.distance_to(enemy.position) < unit.vision:
                        if enemy.attack_power < unit.health:
                            unit.move(enemy.position)
                        else:
                            unit.move(goalPos)
                        break
                else:
                    unit.move(goalPos)
            case "Rusher":
                # move to closest enemy within vision range
                for enemy in enemy_army:
                    if unit.position.distance_to(enemy.position) < unit.vision:
                        unit.move(enemy.position)
                        break
                else:
                    unit.move(goalPos)

    goalPos = pygame.Vector2(0, screen.get_height() / 2)
    for unit in enemy_army:
        if not unit.visible:
            continue
        match unit.unitType:
            case "Melee":
                # find closest enemy within vision range
                for player in player_army:
                    if unit.position.distance_to(player.position) < unit.vision:
                        unit.move(player.position)
                        break
                else:
                    unit.move(goalPos)
            case "Tank":
                # will attack closest enemy within vision range if their damage is higher than their health
                for player in player_army:
                    if unit.position.distance_to(player.position) < unit.vision:
                        if player.attack_power < unit.health:
                            unit.move(player.position)
                        else:
                            unit.move(goalPos)
                        break
                else:
                    unit.move(goalPos)
            case "Rusher":
                # move to closest enemy within vision range
                for player in player_army:
                    if unit.position.distance_to(player.position) < unit.vision:
                        unit.move(player.position)
                        break
                else:
                    unit.move(goalPos)

    # update unit attacks
    ## if enemy in range, attack, melee units kill on contact
    for player in player_army:
        if not player.visible:
            continue
        match player.unitType:
            case "Melee":
                for enemy in enemy_army:
                    if player.position.distance_to(enemy.position) < 20:
                        player.attack(enemy)
                        enemy.take_damage(player.attack_power)
                        if enemy.health <= 0:
                            enemy.die()
                            enemy_army.remove(enemy)
                            # remove from OBJECTS
                            OBJECTS.remove(enemy)
            case "Tank":
                for enemy in enemy_army:
                    if player.position.distance_to(enemy.position) < 20:
                        player.attack(enemy)
                        enemy.take_damage(player.attack_power)
                        if enemy.health <= 0:
                            enemy.die()
                            enemy_army.remove(enemy)
                            # remove from OBJECTS
                            OBJECTS.remove(enemy)
            case "Rusher":
                for enemy in enemy_army:
                    if player.position.distance_to(enemy.position) < 5:
                        player.attack(enemy)
                        enemy.take_damage(player.attack_power)
                        if enemy.health <= 0:
                            enemy.die()
                            enemy_army.remove(enemy)
                            # remove from OBJECTS
                            OBJECTS.remove(enemy) 

    for enemy in enemy_army:
        if not enemy.visible:
            continue
        match enemy.unitType:
            case "Melee":
                for player in player_army:
                    if enemy.position.distance_to(player.position) < 20:
                        enemy.attack(player)
                        player.take_damage(enemy.attack_power)
                        if player.health <= 0:
                            player.die()
                            player_army.remove(player)
                            # remove from OBJECTS
                            OBJECTS.remove(player)
            case "Tank":
                for player in player_army:
                    if enemy.position.distance_to(player.position) < 20:
                        enemy.attack(player)
                        player.take_damage(enemy.attack_power)
                        if player.health <= 0:
                            player.die()
                            player_army.remove(player)
                            # remove from OBJECTS
                            OBJECTS.remove(player)
            case "Rusher":
                for player in player_army:
                    if enemy.position.distance_to(player.position) < 5:
                        enemy.attack(player)
                        player.take_damage(enemy.attack_power)
                        if player.health <= 0:
                            player.die()
                            player_army.remove(player)
                            # remove from OBJECTS
                            OBJECTS.remove(player)


    # remove dead units from army
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
    goalPos = pygame.Vector2(screen.get_width(), screen.get_height() / 2)
    for unit in player_army:
        if unit.position.distance_to(goalPos) < 20 and unit.visible:
            player_score += 1
            # remove from army
            player_army.remove(unit)
            OBJECTS.remove(unit)

    goalPos = pygame.Vector2(0, screen.get_height() / 2)
    for unit in enemy_army:
        if unit.position.distance_to(goalPos) < 20 and unit.visible:
            enemy_score += 1
            # remove from army
            enemy_army.remove(unit)
            OBJECTS.remove(unit)

    # update unit strategies
    pass


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