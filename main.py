import pygame
import os
import random

#relative path to access files
PATH = 'assets'

pygame.font.init()
pygame.mixer.init()

#creating necessary variables
background_music = pygame.mixer.Sound(os.path.join(PATH, 'background1.wav'))
hit_sound = pygame.mixer.Sound(os.path.join(PATH, 'Hit.mp3'))
shoot_sound = pygame.mixer.Sound(os.path.join(PATH, 'Shoot.mp3'))

background_music.play()

WIDTH, HEIGHT = 900, 1400
SS_WIDTH, SS_HEIGHT = 82,60

FPS = 144

velocity = 10
laser_velocity = -10
piercing_laser_vel = -20
enemy_laser_vel = 6
enemy_velocity = 2
charge_bar = 5

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)

bullet_list = []
beam_list = []
enemy_list = []

ENDZONE = pygame.Rect(0,1375,WIDTH,25)

pygame.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Space Invaders - Richard Bai")

#loading in and scaling all image sprites necessary
spaceship_image = pygame.image.load(os.path.join(PATH, 'spaceship_red.png'))
spaceship = pygame.transform.rotate(pygame.transform.scale(spaceship_image, (SS_WIDTH,SS_HEIGHT)), 180)

red_laser_img = pygame.transform.scale(pygame.image.load(os.path.join(PATH, 'pixel_laser_red.png')), (80,80))
blue_laser_img = pygame.transform.scale(pygame.image.load(os.path.join(PATH, 'pixel_laser_blue.png')), (80,80))
yellow_laser_img = pygame.transform.scale(pygame.image.load(os.path.join(PATH, 'pixel_laser_yellow.png')), (80,80))
green_laser_img = pygame.transform.scale(pygame.image.load(os.path.join(PATH, 'pixel_laser_green.png')), (80,80))

piercing_laser_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join(PATH, 'rocket.png')), (80,80)), 90)

redship = pygame.image.load(os.path.join(PATH, 'pixel_ship_red_small.png'))
greenship = pygame.image.load(os.path.join(PATH, 'pixel_ship_green_small.png'))
blueship = pygame.image.load(os.path.join(PATH, 'pixel_ship_blue_small.png'))

background = pygame.image.load(os.path.join(PATH, 'background-black.png'))
background_cast = pygame.transform.scale(background, (WIDTH,HEIGHT))

#Laser class
class Laser():
    def __init__(self, x, y, laser_img, p):
        self.x = x
        self.y = y
        if p:
            self.laser_img = piercing_laser_img
        if not(p):
            self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(self.laser_img)
        self.piercing = p

    #draws the laser onto the screen
    def draw(self, window):
        window.blit(self.laser_img, (self.x, self.y))
    
    #moves laser
    def move(self, vel):
        self.y += vel

    #deletes laser if it is out of bounds
    def out_of_bounds(self, height):
        return not(self.y <= height and self.y >= 0)
    
    #detects a collision between a laser and an object, returns true if there is a collision and returns false otherwise
    def collision(self, obj):
        return collide(self,obj)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#basic ship class to act as a super class to player and enemy ships
class SHIP:

    #cooldown (running 144 FPS so we can fire 16 times/sec)
    COOLDOWN = 9

    #constructor and defining all necessary attributes
    def __init__(self, x, y, color, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cd = 0

    #resets cooldown if the ships cooldown attribute is greater than the cooldown treshhold, otherwise increments the cooldown attribute
    def cooldown(self):
        if self.cd >= self.COOLDOWN:
            self.cd = 0
        elif self.cd > 0:
            self.cd += 1

    #if we have no cooldown on our shot, we play the sound, create a laser, increment our cooldown and then append the laser to our list of lasers
    def shoot(self):
        if self.cd == 0:
            shoot_sound.play()
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y - 40, self.laser_img, False)
            self.lasers.append(laser)
            self.cd = 1

    #draws the ship and any lasers onto the screen
    def draw(self, window):
        window.blit(self.ship_img,(self.x, self.y))
        for laser in self.lasers:
            laser.draw(screen)

    #moves the lasers, calls the cooldown function then moves each laser and then checks for collisions/out of bounds
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.out_of_bounds(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj) and type(obj) != Enemy:
                hit_sound.play()
                obj.health -= 10
                self.lasers.remove(laser)

    #accessor for width
    def get_width(self):
        return self.ship_img.get_width()

    #accessor for height
    def get_height(self):
        return self.ship_img.get_height()

#Player class with inherited attributes
class Player(SHIP):
    def __init__(self, x, y, health = 100):
        super().__init__(x,y,health)
        self.ship_img = spaceship
        self.laser_img = yellow_laser_img
        self.charge = 0
        self.score = 0
        self.mask = pygame.mask.from_surface(self.ship_img)

    #moves the laser, same are superclass method but checks for collisions between player lasers and enemy ships
    def move_lasers(self, vel, piercing_vel, objs):
        self.cooldown()
        for laser in self.lasers:
            if laser.piercing:
                laser.move(piercing_vel)
            elif not(laser.piercing):
                laser.move(vel)

            if laser.out_of_bounds(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:    
                    if laser.collision(obj):
                        hit_sound.play()
                        self.score += 10
                        objs.remove(obj)
                        self.charge += 1
                        if laser.piercing:
                            continue
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def shoot_p_laser(self):
        shoot_sound.play()
        piercing_laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y - 40, yellow_laser_img, True)
        self.lasers.append(piercing_laser)
        self.charge -= 5

    def healthbar(self, window):
        
        pygame.draw.rect(window, RED, (self.x, self.y + self.get_height() + 10, self.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.get_height() + 10, self.get_width() * (self.health/100), 10))

    def chargebar(self, window):
        
        pygame.draw.rect(window, WHITE, (self.x, self.y + self.get_height() + 30, self.get_width(), 10))
        if self.charge <= 5:
            pygame.draw.rect(window, BLUE, (self.x, self.y + self.get_height() + 30, self.get_width() * (self.charge/5), 10))
        else:
            pygame.draw.rect(window, BLUE, (self.x, self.y + self.get_height() + 30, self.get_width(), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        self.chargebar(window)

#enemy ship class
class Enemy(SHIP):

    #map to make classifying different types of enemy ships easier
    enemy_class = {
        "red" : (redship, red_laser_img),
        "green" : (greenship, green_laser_img),
        "blue" : (blueship, blue_laser_img)
    }

    #constructor
    def __init__(self, x, y, color, health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.enemy_class[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    #moves the ship
    def move(self, velocity):
        self.y += velocity

    #shoots a laser but appends it from the relative position of an enemy ship
    def shoot(self):
        if self.cd == 0:
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y + self.get_height() + 10, self.laser_img, False)
            self.lasers.append(laser)
            self.cd = 1

#moves the ship
def handle_movement(pressed, ship):
    if pressed[pygame.K_LEFT] and ship.x - velocity > 0:
        ship.x -= velocity
    if pressed[pygame.K_RIGHT] and ship.x + velocity + SS_WIDTH < WIDTH:
        ship.x += velocity

#returns 
def level_namer(num):
    if num == 1 or num == 0:
        return "Moonlight"
    elif num == 2:
        return "Shooting Stars"
    elif num == 3:
        return "Nebula"
    elif num == 4:
        return "Vortex"
    else:
        return "Endless Calamity"

#reads and returns the highscore stored in the text file
def readHighScore():
    #opens highscore file and reads it. Returns the value to be used later.
    scoreFile = open ("highscore.txt", "r")
    highScoreStr = scoreFile.readline()
    if highScoreStr == "":
        highScore = 0
    else:
        highScore = int(highScoreStr)        
    scoreFile.close()    
    return highScore

#writing highscore, takes the current score and writes it as the highscore if it is higher than intial highscore.
def writeHighScore(score):
    scoreFile = open ("highscore.txt", "w")
    scoreFile.truncate()
    scoreFile.write(str(score))
    scoreFile.close() 

#clock to tick for FPS
clock = pygame.time.Clock()

#main game loop
def main(l, l_size):

    run = True
    lost = False


    #defining the player object
    ship = Player(450-SS_WIDTH//2, 1200, RED)
    ship.score = 0

    pygame.display.update()

    #main game attributes
    level = l
    level_size = l_size

    #method to update the screen 144 times in a second
    def update_screen():
        screen.blit(background_cast, (0,0))
    
        #obtaining fonts
        font = pygame.font.SysFont('calibri', 50)
        lost_font = pygame.font.SysFont('calibri', 70)

        name = level_namer(level)

        #creating indicators for lives and level
        score_indicator = font.render(f"Score: {int(ship.score)}", 1, WHITE)
        level_indicator = font.render(f"Level: {level}", 1, WHITE)
        level_name = font.render(f"{name}", 1, WHITE)

        #shows current level and number of lives
        screen.blit(score_indicator, (10,10))
        screen.blit(level_indicator, (WIDTH - level_indicator.get_width() - 10, 10))
        screen.blit(level_name, (WIDTH//2 - level_name.get_width()//2, 10))

        #draws enemies onto the screen
        for enemy in enemy_list:
            enemy.draw(screen)

        ship.draw(screen)

        pygame.draw.rect(screen, RED, ENDZONE)

        #if the game is lost, check if its a highscore and record in the highscore.txt file. Also display the YOU LOST message before queuing the game again.
        if lost:
            label = lost_font.render('YOU LOST', 1, WHITE)
            screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))
            pygame.display.update()
            
            if ship.score > readHighScore():
                writeHighScore(ship.score)

            pygame.time.delay(5000)

            pygame.quit()

        pygame.display.update()

    while run:

        clock.tick(144)

        if ship.health < 1:
            lost = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ship.shoot()

                if event.key == pygame.K_z and ship.charge >= 5:
                    ship.shoot_p_laser()

        #moves the enemy, moves enemy lasers, randomly generates a shot and also detects whether or not the enemy has collided with "home base"
        for enemy in enemy_list:
            enemy.move(enemy_velocity)
            enemy.move_lasers(enemy_laser_vel, ship)

            if random.randrange(0, 144 * 6) == 1:
                enemy.shoot()

            if collide(enemy, ship):
                hit_sound.play()
                enemy_list.remove(enemy)
                ship.health -= 10

            if (enemy.y > HEIGHT - 25):
                enemy_list.remove(enemy)
                ship.health -= 5

        #moves the lasers of the player ship
        ship.move_lasers(laser_velocity, piercing_laser_vel, enemy_list)
        
        #movement handling and redrawing the main game window
        keys_pressed = pygame.key.get_pressed()
        handle_movement(keys_pressed, ship)

        if len(enemy_list) == 0 and not(lost):
            level += 1
            ship.score *= 2
            level_size *= 2

            for i in range(int(level_size)):
                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(-2000, -100), random.choice(["red","blue","green"]))
                enemy_list.append(enemy)

        update_screen()
 
def main_menu():
    title_font = pygame.font.SysFont('calibri', 80)

    #cleaning up the game screen

    run = True
    while run:
        screen.blit(background_cast, (0,0))
        title_label = title_font.render("Press the mouse to begin", 1, WHITE)
        screen.blit(title_label, (WIDTH//2 - title_label.get_width()//2, 500))

        highscore = title_font.render(f"Highscore: {readHighScore()}", 1, WHITE)
        screen.blit(highscore, (WIDTH//2 - highscore.get_width()//2, 700))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main(0,2.5)

    pygame.quit()

main_menu()