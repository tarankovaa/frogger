import os
import sys

import pygame

FPS = 30
WIDTH, HEIGHT = 448, 512

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
        return int(f.read())


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
            elif event.type == pygame.KEYDOWN:
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
float_group = pygame.sprite.Group()
frog_homes_group = pygame.sprite.Group()


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


class Frog(pygame.sprite.Sprite):

    def __init__(self):
        super(Frog, self).__init__(all_sprites)

        frames = cut_sheet(load_image('frog_anim.png'), 8, 1)
        self.frames = {'u': frames[:2],
                       'l': frames[2:4],
                       'd': frames[4:6],
                       'r': frames[6:]}
        self.frames_death = cut_sheet(load_image('death_anim.png'), 7, 1)
        self.cur_frame = 0
        self.cur_frame_death = 0
        self.dest = 'u'
        self.image = self.frames[self.dest][self.cur_frame]
        self.rect = self.image.get_rect()
        self.start_x = WIDTH // 2
        self.start_y = HEIGHT - 64
        self.rect = self.rect.move(self.start_x, self.start_y)
        self.collide = False
        self.pos_x = self.start_x
        self.pos_y = self.start_y
        self.death_delay = 0
        self.move_delay = 1
        self.moving = False

    def move(self, scancode):
        if not self.collide and not self.moving:
            if scancode == 79:
                if not self.rect.x + 32 >= WIDTH:
                    self.dest = 'r'
                    self.rect.x += 16
                    self.pos_x = self.rect.x
                    self.cur_frame = 1
                    self.image = self.frames[self.dest][self.cur_frame]
                    self.moving = True
            elif scancode == 80:
                if not self.rect.x - 32 < 0:
                    self.dest = 'l'
                    self.rect.x -= 16
                    self.pos_x = self.rect.x
                    self.cur_frame = 1
                    self.image = self.frames[self.dest][self.cur_frame]
                    self.moving = True
            elif scancode == 81:
                if not self.rect.y + 32 > HEIGHT - 64:
                    self.dest = 'd'
                    self.rect.y += 16
                    self.cur_frame = 1
                    self.image = self.frames[self.dest][self.cur_frame]
                    self.moving = True
            else:
                self.dest = 'u'
                self.rect.y -= 16
                self.cur_frame = 1
                self.image = self.frames[self.dest][self.cur_frame]
                self.moving = True

    def update(self):
        if self.collide:
            if self.moving:
                self.moving = False
                self.move_delay = 1
            if self.death_delay > 0:
                self.death_delay -= 1
            else:
                if self.cur_frame_death == len(self.frames_death):
                    self.collide = False
                    self.cur_frame_death = 0
                    self.restart()
                else:
                    self.image = self.frames_death[self.cur_frame_death]
                    self.cur_frame_death += 1
                    self.death_delay = 5
        else:
            if self.moving:
                if self.move_delay > 0:
                    self.move_delay -= 1
                else:
                    self.cur_frame = 0
                    self.image = self.frames[self.dest][self.cur_frame]
                    if self.dest == 'u':
                        self.rect.y -= 16
                    elif self.dest == 'd':
                        self.rect.y += 16
                    elif self.dest == 'l':
                        self.rect.x -= 16
                        self.pos_x = self.rect.x
                    elif self.dest == 'r':
                        self.rect.x += 16
                        self.pos_x = self.rect.x
                    self.move_delay = 1
                    self.moving = False
            if pygame.sprite.spritecollideany(self, cars_group, pygame.sprite.collide_mask):
                self.collide = True
            elif sprite := pygame.sprite.spritecollideany(self, float_group,
                                                          pygame.sprite.collide_mask):
                self.pos_x += sprite.speed
                self.rect.x = self.pos_x
            elif sprite := pygame.sprite.spritecollideany(self, frog_homes_group):
                if sprite.cur_state == 'empty':
                    sprite.change_state('reached')
                    self.restart()
                else:
                    self.collide = True
            if 96 <= self.rect.y < 256:
                if not pygame.sprite.spritecollideany(self, float_group,
                                                      pygame.sprite.collide_mask):
                    self.collide = True
                if self.rect.x + 32 > WIDTH or self.rect.x < 0:
                    self.collide = True
            elif self.rect.y < 96:
                if not pygame.sprite.spritecollideany(self, frog_homes_group):
                    self.collide = True

    def restart(self):
        self.rect.x = self.start_x
        self.pos_x = self.rect.x
        self.rect.y = self.start_y
        self.dest = 'u'
        self.cur_frame = 0
        self.image = self.frames[self.dest][self.cur_frame]


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
        self.add(float_group)


class AnimatedWrappingSprite(WrappingSprite):

    def __init__(self, sheet, columns, rows, x, y, speed):
        super(AnimatedWrappingSprite, self).__init__(sheet, x, y, speed)

        self.frames = cut_sheet(self.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.delay = 15

    def update(self):
        super(AnimatedWrappingSprite, self).update()

        self.delay -= 1
        if self.delay == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.delay = 15


class Turtles(AnimatedWrappingSprite):
    TYPE_1 = 'turtles1.png'
    TYPE_2 = 'turtles2.png'

    def __init__(self, type_, x, y, speed):
        super(Turtles, self).__init__(type_, 1, 3, x, y, speed)
        self.add(float_group)


class DivingTurtles(AnimatedWrappingSprite):
    TYPE_1 = 'diving-turtles1.png'
    TYPE_2 = 'diving-turtles2.png'

    def __init__(self, type_, x, y, speed):
        super(DivingTurtles, self).__init__(type_, 3, 3, x, y, speed)
        self.add(float_group)


class FrogHome(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super(FrogHome, self).__init__(all_sprites, frog_homes_group)
        states = cut_sheet(load_image('home-states.png'), 3, 1)
        self.states = {'empty': states[0],
                       'reached': states[1],
                       'completed': states[2]}
        self.cur_state = 'empty'
        self.image = self.states[self.cur_state]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def change_state(self, state):
        self.cur_state = state
        self.image = self.states[self.cur_state]


def game_screen():
    bg = load_image('level-background.png')

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
    Log(Log.TYPE_2, 352, 160, 2.5)

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

    frog = Frog()

    font = pygame.font.Font('data/Frogger-Regular.ttf', 16)
    highscore = load_highscore()
    score = 0
    max_y = HEIGHT - 64
    reached_homes = 0
    delay = 90
    completed = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.scancode in range(79, 83):
                    frog.move(event.scancode)

        if frog.rect.y == max_y - 32:
            score += 10
            max_y -= 32
        if len(list(filter(lambda x: x.cur_state == 'reached', frog_homes_group))) > reached_homes:
            reached_homes += 1
            score += 50
            max_y = HEIGHT - 64
        if reached_homes == 5:
            if delay == 90:
                score += 1000
                completed += 1
                for frog_home in frog_homes_group:
                    frog_home.change_state('completed')
                frog.kill()
            delay -= 1
            if delay == 0:
                for frog_home in frog_homes_group:
                    frog_home.change_state('empty')
                delay = 90
                reached_homes = 0
                frog = Frog()

        if score > 99999:
            score = 99999
        if score > highscore:
            highscore = score

        screen.blit(bg, (0, 0))
        all_sprites.draw(screen)
        screen.blit(font.render('1-UP', False, pygame.Color('#c3c3d9')), (64, 0))
        screen.blit(font.render('%(score)05d' % {'score': score}, False,
                                pygame.Color('#e00000')), (48, 16))
        screen.blit(font.render('HI-SCORE', False, pygame.Color('#c3c3d9')), (160, 0))
        screen.blit(font.render('%(highscore)05d' % {'highscore': highscore}, False,
                                pygame.Color('#e00000')), (176, 16))
        for i in range(completed):
            x = WIDTH - 32 - i * 16
            screen.blit(load_image('completed.png'), (x, HEIGHT - 32))

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
