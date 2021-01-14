import os
import sys

import pygame


DATA_DIR = 'data'
IMAGES_DIR = 'data/images'

FPS = 50
WIDTH, HEIGHT = 500, 500

TIME_OUT_EVENT = pygame.USEREVENT + 1


pygame.init()
pygame.display.set_caption('Frogger')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join(IMAGES_DIR, name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_highscore():
    with open(os.path.join(DATA_DIR, 'highscore.txt'), 'r',
              encoding='utf8') as f:
        return f.read()


def save_highscore(score):
    with open(os.path.join(DATA_DIR, 'highscore.txt'), 'w',
              encoding='utf8') as f:
        f.write(score)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                game_screen()
        pygame.display.flip()
        clock.tick(FPS)


def main_menu_screen():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


class Frog(pygame.sprite.Sprite):
    pass


class Car(pygame.sprite.Sprite):

    images = []


class Log(pygame.sprite.Sprite):
    pass


class Alligator(pygame.sprite.Sprite):
    pass


class Turtles(pygame.sprite.Sprite):
    pass


class DivingTurtle(pygame.sprite.Sprite):
    pass


class Snake(pygame.sprite.Sprite):
    pass


class Otter(pygame.sprite.Sprite):
    pass


class FemaleFrog(pygame.sprite.Sprite):
    pass


class FrogHome(pygame.sprite.Sprite):
    pass


class Insect(pygame.sprite.Sprite):
    pass


class LurkingAlligator(pygame.sprite.Sprite):
    pass


def game_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_screen()
        pygame.display.flip()
        clock.tick(FPS)


def main():
    start_screen()


if __name__ == '__main__':
    main()
