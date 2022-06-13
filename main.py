import pygame
import os
import random

PATH = 'assets'
#creating necessary variables

pygame.font.init()
pygame.mixer.init()

background_music = pygame.mixer.Sound(os.path.join(PATH, 'background1.wav'))
hit_sound = pygame.mixer.Sound(os.path.join(PATH, 'Hit.mp3'))
shoot_sound = pygame.mixer.Sound(os.path.join(PATH, 'Shoot.mp3'))

WIDTH, HEIGHT = 900, 1400
SS_WIDTH, SS_HEIGHT = 82,60

FPS = 144

velocity = 10
laser_velocity = -10
enemy_laser_vel = 6
enemy_velocity = 2
charge_bar = 5

RED = (255,0,0)
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

redship = pygame.image.load(os.path.join(PATH, 'pixel_ship_red_small.png'))
greenship = pygame.image.load(os.path.join(PATH, 'pixel_ship_green_small.png'))
blueship = pygame.image.load(os.path.join(PATH, 'pixel_ship_blue_small.png'))

background = pygame.image.load(os.path.join(PATH, 'background-black.png'))
background_cast = pygame.transform.scale(background, (WIDTH,HEIGHT))

#Laser class
class Laser():
    def __init__(self, x, y, laser_img):
        self.x = x
        self.y = y
        self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(self.laser_img)

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
        offset_x = obj.x - self.x
        offset_y = obj.y - self.y
        return self.mask.overlap(obj.mask, (offset_x, offset_y)) != None

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
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y - 40, self.laser_img)
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
        self.mask = pygame.mask.from_surface(self.ship_img)

    #moves the laser, same are superclass method but checks for collisions between player lasers and enemy ships
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.out_of_bounds(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:    
                    if laser.collision(obj):
                        hit_sound.play()
                        objs.remove(obj)
                        self.lasers.remove(laser)

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
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y + self.get_height() + 10, self.laser_img)
            self.lasers.append(laser)
            self.cd = 1

#moves the ship
def handle_movement(pressed, ship):
    if pressed[pygame.K_LEFT] and ship.x - velocity > 0:
        ship.x -= velocity
    if pressed[pygame.K_RIGHT] and ship.x + velocity + SS_WIDTH < WIDTH:
        ship.x += velocity

#clock to tick for FPS
clock = pygame.time.Clock()

#main game loop
def main():

    background_music.play()
    run = True
    lost = False

    ship = Player(450-SS_WIDTH//2, 1200, RED)

    lives = 10
    level = 0
    level_size = 10

    def update_screen():
        screen.blit(background_cast, (0,0))
    
        #obtaining fonts
        font = pygame.font.SysFont('calibri', 50)
        lost_font = pygame.font.SysFont('calibri', 70)

        #creating indicators for lives and level
        lives_indicator = font.render(f"Lives: {lives}", 1, WHITE)
        level_indicator = font.render(f"Level: {level}", 1, WHITE)

        #shows current level and number of lives
        screen.blit(lives_indicator, (10,10))
        screen.blit(level_indicator, (WIDTH - level_indicator.get_width() - 10, 10))

        #draws enemies onto the screen
        for enemy in enemy_list:
            enemy.draw(screen)

        ship.draw(screen)

        pygame.draw.rect(screen, RED, ENDZONE)

        if lost:
            label = lost_font.render('YOU LOST', 1, WHITE)
            screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))

        pygame.display.update()

    while run:

        clock.tick(144)

        if lives < 1 or ship.health < 1:
            lost = True

        if len(enemy_list) == 0:
            level += 1
            level_size += 5
            for i in range(level_size):
                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(-2000, -100), random.choice(["red","blue","green"]))
                enemy_list.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ship.shoot()

                if event.key == pygame.K_z and charge_bar == 5:
                    shoot_sound.play()
                    beam = pygame.Rect(SS.x + SS_WIDTH//2, 0, 5, SS.y)
                    beam_list.append(beam)
        
        for enemy in enemy_list:
            enemy.move(enemy_velocity)
            enemy.move_lasers(enemy_laser_vel, ship)

            if random.randrange(0, 144 * 8) == 1:
                enemy.shoot()

            if (enemy.y > HEIGHT - 25):
                enemy_list.remove(enemy)
                lives -= 1

        ship.move_lasers(laser_velocity, enemy_list)
        
        keys_pressed = pygame.key.get_pressed()
        handle_movement(keys_pressed, ship)
        update_screen()

if __name__ == "__main__":
    main()
