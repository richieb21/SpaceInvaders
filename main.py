import pygame
import os

PATH = 'assets'
#creating necessary variables

pygame.font.init()
pygame.mixer.init()

background_music = pygame.mixer.Sound(os.path.join(PATH, 'background1.wav'))

WIDTH, HEIGHT = 900, 1400

SS_WIDTH, SS_HEIGHT = 82,60
velocity = 5
bullet_velocity = 10
charge_bar = 5

RED = (255,0,0)

bullet_list = []

ENDZONE = pygame.Rect(0,1375,WIDTH,25)

pygame.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Space Invaders - Richard Bai")

spaceship_image = pygame.image.load(os.path.join(PATH, 'spaceship_red.png'))
spaceship = pygame.transform.rotate(pygame.transform.scale(spaceship_image, (SS_WIDTH,SS_HEIGHT)), 180)

background = pygame.image.load(os.path.join(PATH, 'background-black.png'))
background_cast = pygame.transform.scale(background, (WIDTH,HEIGHT))

def update_screen(ship, bullet_list):
    screen.blit(background_cast, (0,0))
    screen.blit(spaceship, (ship.x,ship.y))

    pygame.draw.rect(screen, RED, ENDZONE)

    for bullet in bullet_list:
        pygame.draw.rect(screen, RED, bullet)

    pygame.display.update()

clock = pygame.time.Clock()

def handle_movement(pressed, ship):
    if pressed[pygame.K_LEFT] and ship.x - velocity > 0:
        ship.x -= velocity
    if pressed[pygame.K_RIGHT] and ship.x + velocity + SS_WIDTH < WIDTH:
        ship.x += velocity

def handle_bullets(bullet_list):
    for b in bullet_list:
        b.y -= bullet_velocity

        if b.y < 0:
            bullet_list.remove(b)


def main():

    background_music.play()
    run = True

    SS = pygame.Rect(450 - SS_WIDTH//2, 1200, SS_WIDTH, SS_HEIGHT)

    while run:

        clock.tick(144)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(SS.x + SS_WIDTH//2, SS.y, 5, 10)
                    bullet_list.append(bullet)


        
        keys_pressed = pygame.key.get_pressed()
        handle_movement(keys_pressed, SS)
        handle_bullets(bullet_list)
        update_screen(SS, bullet_list)

if __name__ == "__main__":
    main()
