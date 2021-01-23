import os
import sys

import pygame

FPS = 30
WIDTH, HEIGHT = 448, 512

DELAY = 500

pygame.init()
pygame.display.set_caption('Frogger')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', 'images', name)
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
    with open(os.path.join('data', 'highscore.txt'), 'r',
              encoding='utf8') as f:
        return f.read()


def save_highscore(score):
    with open(os.path.join('data', 'highscore.txt'), 'w',
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


all_sprites = pygame.sprite.Group()
cars_group = pygame.sprite.Group()
logs_group = pygame.sprite.Group()
turtles_group = pygame.sprite.Group()
frog_homes_group = pygame.sprite.Group()


class Frog(pygame.sprite.Sprite):
    pass


class WrappingSprite(pygame.sprite.Sprite):

    def __init__(self, image, x, y, speed):
        super(WrappingSprite, self).__init__(all_sprites)

        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.pos_x = x
        self.speed = speed

    def update(self):
        self.pos_x += self.speed
        self.rect.x = self.pos_x
        if self.rect.x > WIDTH + 32 and self.speed > 0:
            self.pos_x = 0 - self.rect.width
            self.rect.x = self.pos_x
        elif self.rect.x < 0 - self.rect.width:
            self.pos_x = WIDTH + 32
            self.rect.x = self.pos_x


class Car(WrappingSprite):
    TYPE_1 = 'car1.png'
    TYPE_2 = 'car2.png'
    TYPE_3 = 'car3.png'
    TYPE_4 = 'car4.png'
    TYPE_5 = 'car5.png'

    def __init__(self, type_, x, y, speed):
        super(Car, self).__init__(type_, x, y, speed)
        self.add(cars_group)


class Log(WrappingSprite):
    TYPE_1 = 'log1.png'
    TYPE_2 = 'log2.png'
    TYPE_3 = 'log3.png'

    def __init__(self, type_, x, y, speed):
        super(Log, self).__init__(type_, x, y, speed)
        self.add(logs_group)


def cut_sheet(sheet, columns, rows):
    frames = []
    rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.width * i, rect.height * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)))
    return frames


class AnimatedWrappingSprite(WrappingSprite):

    def __init__(self, sheet, columns, rows, x, y, speed, delay):
        super(AnimatedWrappingSprite, self).__init__(sheet, x, y, speed)

        self.frames = []
        self.cut_sheet(self.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.delay = delay
        self.timer = self.delay

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        super(AnimatedWrappingSprite, self).update()

        self.timer -= clock.get_time()
        if self.timer < 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.timer = self.delay


class Turtles(AnimatedWrappingSprite):
    TYPE_1 = 'turtles1.png'
    TYPE_2 = 'turtles2.png'

    def __init__(self, type_, x, y, speed):
        super(Turtles, self).__init__(type_, 1, 3, x, y, speed, DELAY)
        self.add(turtles_group)


class DivingTurtles(AnimatedWrappingSprite):
    TYPE_1 = 'diving-turtles1.png'
    TYPE_2 = 'diving-turtles2.png'

    def __init__(self, type_, x, y, speed):
        super(DivingTurtles, self).__init__(type_, 3, 3, x, y, speed, DELAY)
        self.add(turtles_group)


class FrogHome(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super(FrogHome, self).__init__(all_sprites, frog_homes_group)
        states = cut_sheet(load_image('home-states.png'), 3, 1)
        self.states = {'empty': states[0],
                       'reached': states[1],
                       'completed': states[2]}
        self.image = self.states['empty']
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def change_state(self, state):
        self.image = self.states[state]


Car(Car.TYPE_1, 160, 416, -0.75)
Car(Car.TYPE_1, 304, 416, -0.75)
Car(Car.TYPE_1, 448, 416, -0.75)

Car(Car.TYPE_2, 192, 384, 1)
Car(Car.TYPE_2, 320, 384, 1)
Car(Car.TYPE_2, 448, 384, 1)

Car(Car.TYPE_3, 192, 352, -1.25)
Car(Car.TYPE_3, 320, 352, -1.25)
Car(Car.TYPE_3, 448, 352, -1.25)

Car(Car.TYPE_4, 460, 320, 1.5)
Car(Car.TYPE_5, 240, 288, -1.75)
Car(Car.TYPE_5, 416, 288, -1.75)

DivingTurtles(DivingTurtles.TYPE_1, 0, 224, -1.75)
Turtles(Turtles.TYPE_1, 144, 224, -1.75)
Turtles(Turtles.TYPE_1, 288, 224, -1.75)
Turtles(Turtles.TYPE_1, 432, 224, -1.75)

Log(Log.TYPE_1, 64, 192, 0.75)
Log(Log.TYPE_1, 240, 192, 0.75)
Log(Log.TYPE_1, 416, 192, 0.75)

Log(Log.TYPE_2, 32, 160, 2.5)
Log(Log.TYPE_2, 256, 160, 2.5)
Log(Log.TYPE_2, 480, 160, 2.5)

DivingTurtles(DivingTurtles.TYPE_2, 80, 128, -1.75)
Turtles(Turtles.TYPE_2, 208, 128, -1.75)
Turtles(Turtles.TYPE_2, 336, 128, -1.75)
Turtles(Turtles.TYPE_2, 464, 128, -1.75)

Log(Log.TYPE_3, 0, 96, 1.5)
Log(Log.TYPE_3, 208, 96, 1.5)
Log(Log.TYPE_3, 416, 96, 1.5)

FrogHome(16, 64)
FrogHome(112, 64)
FrogHome(208, 64)
FrogHome(304, 64)
FrogHome(400, 64)


def game_screen():
    bg = load_image('level-background.png')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        screen.blit(bg, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
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


if __name__ == '__main__':
    game_screen()
