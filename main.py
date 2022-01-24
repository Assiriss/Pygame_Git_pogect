import pygame
import os
import sys
import sqlite3
import time

pygame.init()
size = width, height = 800, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as error:
        print(f'при загрузке изображения {name} произошла ошибка: {error}')
        raise SystemExit(error)
    if color_key:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    return image
FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():

    pygame.mixer.Channel(1).play(pygame.mixer.Sound('заставка звук.mp3'))

    intro_text = ['Создатели проэкта:',
                  "Толмачев Никита",
                  "Зайцев Максим"]

    fon = pygame.transform.scale(load_image('fonn.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    font2 = pygame.font.Font(None, 20)
    font3 = pygame.font.Font(None, 30)
    text_coord_y = 400
    text_coord_x = 660

    text = font.render("ARCADIUM", True, (100, 255, 100))
    screen.blit(text, (310, 50))
    text2 = font3.render("PRESS ENTER TO START", True, (100, 100, 100))
    screen.blit(text2, (285, 230))
    for line in intro_text:
        string_rendered = font2.render(line, 1, pygame.Color('white'))
        text_coord_y += 20
        screen.blit(string_rendered, (text_coord_x, text_coord_y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

pygame.init()



def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as error:
        print(f'при загрузке изображения {name} произошла ошибка: {error}')
        raise SystemExit(error)
    if color_key:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    return image

player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

# tile_images = {
#     'wall': load_image('box.png'),
#     'empty': load_image('grass.png')
# }
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, x, y, message, action=None):
        mouse = pygame.mouse.get_pos()
        if x < mouse[0] < x + self.width:
            if y < mouse[1] < y + self.height:
                pygame.draw.rect(screen, (23, 204, 58), (x, y, self.width, self.height))


        pygame.draw.rect(screen, (13, 162, 50), (x, y, self.width, self.height))
        font = pygame.font.Font(None, 50)
        text = font.render("message", True, (100, 255, 100))
        screen.blit(text, (50, 50))








class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for j in range(0, self.height * self.cell_size, self.cell_size):
            for i in range(0, self.width * self.cell_size, self.cell_size):
                pygame.draw.rect(screen, (255, 255, 255),
                                 (i + self.left, j + self.top, self.cell_size, self.cell_size), 1)

    def get_cell(self, mouse_pos):
        if mouse_pos[0] in range(self.left, self.width * self.cell_size + self.left) and \
                mouse_pos[1] in range(self.top, self.height * self.cell_size + self.top):
            return (mouse_pos[0] - self.left) // self.cell_size, (mouse_pos[1] - self.top) // self.cell_size
        else:
            return None

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_click(self, mouse_pos):
        self.on_click(self.get_cell(mouse_pos))



class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = pos_x, pos_y
        self.health = 100
        self.allhealth = 100
        self.range = 1
        self.damage = 100
        self.defend = 2


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, enemy_image):
        super().__init__(player_group, all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = pos_x, pos_y
        self.health = 100
        self.allhealth = 100
        self.range = 0
        self.damage = 0
        self.defend = 0
        self.obozn = 'd'


class Gameboard(Board):
    def __init__(self, width, height, map):
        super().__init__(width, height)
        self.hero = Player(0, 0)
        self.kolenemies = 0
        self.playerx = 0
        self.playery = 0
        self.weap2range = 2
        self.weap2mana = 10
        self.playercords = []
        self.left = 25
        self.top = 120
        self.cell_size = 75
        self.board = []
        self.boardshow = [['0'] * width for _ in range(height)]
        self.enemies = dict()

        for i in range(len(map)):
            g = []
            for zi in range(len(map[i])):
                if map[i][zi] != '@' and map[i][zi] != '.':
                    self.kolenemies += 1
                    newenem = Enemy(zi, i, load_image('mar.png'))
                    if map[i][zi] == 'd':
                        newenem.obozn = 'd'
                        newenem.allhealth = 100
                        newenem.health = newenem.health
                        newenem.range = 1
                        newenem.damage = 1
                        newenem.defend = 1
                    self.enemies[(zi, i)] = newenem
                    self.boardshow[i][zi] = 'e'
                    g.append('e')
                else:
                    g.append(map[i][zi])
                    if map[i][zi] == '@':
                        self.playerx = zi
                        self.playery = i
                        self.boardshow[i][zi] = '@'
                        self.hero.pos = (zi, i)
                        for i1 in range(self.hero.range * -1, self.hero.range + 1):
                            if 0 <= i1 + i <= self.height - 1:
                                for jk in range(-1, 2):
                                    if 0 <= jk + zi <= self.width - 1:
                                        if self.boardshow[i1 + i][jk + zi] == '@':
                                            self.boardshow[i1 + i][jk + zi] = 'b'
                                        elif self.boardshow[i1 + i][jk + zi] == 'e' or self.boardshow[i1 + i][jk + zi]\
                                                == 'e2':
                                            self.boardshow = 'e1'
                                        else:
                                            self.boardshow[i1 + i][jk + zi] = 'b'

            self.board.append(g)

        for i in range(self.height):
            for j in range(self.width):
                if self.boardshow[i][j] == 'e1' or self.boardshow[i][j] == 'e12':
                    if abs(self.playery - i) > self.hero.range or abs(self.playerx - j) > self.hero.range:
                        self.boardshow[i][j] = 'e'
                if self.boardshow[i][j] == 'e' or self.boardshow[i][j] == 'e2':
                    if abs(self.playery - i) <= self.weap2range and abs(self.playerx - j) <= self.weap2range:
                        self.boardshow[i][j] = 'e3'
                    if abs(self.playery - i) <= self.hero.range and abs(self.playerx - j) <= self.hero.range:
                        self.boardshow[i][j] = 'e1'
        self.butgosize = 40
        self.butgoactive = False
        self.butgoused = False
        self.butgocord = 160
        self.butweapsize = (60, 20)
        self.butweap1active = False
        self.butweapused = False
        self.butweap1cord = 250
        self.butweap2cord = 500
        self.butweap2active = False

        self.butnextsize = 40
        self.butnextactive = False
        self.butnextcord = 180
        self.healthbar = 100
        self.healthused = 100
        self.energybar = 100
        self.energyused = 100
        self.interheight = 80
        self.smalll = 5
        self.bigg = 5
        self.money = 600



    def render(self, screen):
        pygame.draw.rect(screen, (247, 232, 170), (self.left, self.top, self.width * self.cell_size,
                                                  self.height * self.cell_size))

        for j in range(0, self.height * self.cell_size, self.cell_size):
            for i in range(0, self.width * self.cell_size, self.cell_size):

                if self.butgoactive and (self.boardshow[j // self.cell_size][i // self.cell_size] == 'b' or \
                        self.boardshow[j // self.cell_size][i // self.cell_size] == '@'):
                    pygame.draw.rect(screen, (0, 128, 128),
                                     (i + self.left, j + self.top, self.cell_size, self.cell_size))
                if self.butgoactive and self.boardshow[j // self.cell_size][i // self.cell_size] == 'bl':
                    pygame.draw.rect(screen, (0, 0, 255),
                                     (i + self.left, j + self.top, self.cell_size, self.cell_size))
                if self.butweap2active and (self.boardshow[j // self.cell_size][i // self.cell_size] == 'e1' or
                                            self.boardshow[j // self.cell_size][i // self.cell_size] == 'e12' or
                self.boardshow[j // self.cell_size][i // self.cell_size] == 'e32' or
                                            self.boardshow[j // self.cell_size][i // self.cell_size] == 'e3'):
                    pygame.draw.rect(screen, (153, 0, 0), (i + self.left, j + self.top, self.cell_size,
                                                           self.cell_size))
                if self.butweap1active and (self.boardshow[j // self.cell_size][i // self.cell_size] == 'e1' or
                                            self.boardshow[j // self.cell_size][i // self.cell_size] == 'e12'):
                    pygame.draw.rect(screen, (153, 0, 0),  (i + self.left, j + self.top, self.cell_size,
                                                            self.cell_size))
                if self.boardshow[j // self.cell_size][i // self.cell_size] == 'e2' or \
                        self.boardshow[j // self.cell_size][i // self.cell_size] == 'e12' or \
                        self.boardshow[j // self.cell_size][i // self.cell_size] == 'e32':
                    pygame.draw.rect(screen, (255, 102, 0), (i + self.left, j + self.top, self.cell_size,
                                                             self.cell_size))
                    health = self.enemies[(i // self.cell_size, j // self.cell_size)].health
                    alhealth = self.enemies[(i // self.cell_size, j // self.cell_size)].allhealth
                    pygame.draw.rect(screen, (255, 255, 255), (15, 15, alhealth * 2, 30))
                    pygame.draw.rect(screen, (255, 0, 0), (15, 15, health * 2, 30))
                if self.boardshow[j // self.cell_size][i // self.cell_size] == '1' or \
                        self.boardshow[j // self.cell_size][i // self.cell_size] == 'bl' and not self.butgoactive:
                    pygame.draw.rect(screen, (255, 215, 0),
                                     (i + self.left, j + self.top, self.cell_size, self.cell_size))
                if self.board[j // self.cell_size][i // self.cell_size] == '@':
                    pygame.draw.circle(screen, (255, 0, 255), (i + self.left + self.cell_size // 2, j + self.top +
                                                               self.cell_size // 2), 25)
                if self.board[j // self.cell_size][i // self.cell_size] != '@' and\
                        self.board[j // self.cell_size][i // self.cell_size] != '.':
                    pygame.draw.circle(screen, (0, 255, 255), (i + self.left + self.cell_size // 2, j + self.top +
                                                               self.cell_size // 2), 25)


                pygame.draw.rect(screen, (255, 255, 255),
                                 (i + self.left, j + self.top, self.cell_size, self.cell_size), 1)
        pygame.draw.rect(screen, (170, 147, 10), (self.left, self.top, self.width * self.cell_size,
                                                   self.height*self.cell_size), 3)
        pygame.draw.rect(screen, (92, 51, 23), (self.left, self.height * self.cell_size + self.top + 10,
                                                self.width * self.cell_size, self.interheight))
        pygame.draw.rect(screen, (128, 128, 128), (self.left + 10, self.height * self.cell_size + self.top + 25,
                                                   self.hero.allhealth, 10))
        pygame.draw.rect(screen, (255, 0, 0), (self.left + 10, self.height * self.cell_size + self.top + 25,
                                                   self.hero.health, 10))
        pygame.draw.rect(screen, (128, 128, 128), (self.left + 10, self.height * self.cell_size + self.top + 45,
                                                   self.energybar, 10))
        pygame.draw.rect(screen, (0, 255, 255), (self.left + 10, self.height * self.cell_size + self.top + 45,
                                                   self.energyused, 10))
        if not self.butgoactive:
            pygame.draw.rect(screen, (255, 0, 0), (self.left + self.butgocord, self.height * self.cell_size + self.top +
                                                   25, 50, 50))
        else:
            pygame.draw.rect(screen, (255, 255, 0),
                             (self.left + self.butgocord, self.height * self.cell_size + self.top + 25, 50, 50))
        if not self.butnextactive:
            pygame.draw.rect(screen, (255, 0, 0), ((self.left + 10, self.height * self.cell_size + self.top + 65,
                                                   self.healthbar, 10)))
        else:
            pygame.draw.rect(screen, (255, 255, 0), ((self.left + 10, self.height * self.cell_size + self.top + 65,
                                                    self.healthbar, 10)))
        if not self.butweap1active:
            pygame.draw.rect(screen, (255, 0, 0), (self.left + self.butweap1cord, self.height * self.cell_size +
                                                   self.top +
                                                   25, 200, 50))

        else:
            pygame.draw.rect(screen, (255, 255, 0),
                             (self.left + self.butweap1cord, self.height * self.cell_size + self.top +
                              25, 200, 50))
        if not self.butweap2active:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.left + self.butweap2cord, self.height * self.cell_size + self.top +
                              25, 200, 50))
        else:
            pygame.draw.rect(screen, (255, 255, 0),
                             (self.left + self.butweap2cord, self.height * self.cell_size + self.top +
                              25, 200, 50))

        pygame.draw.rect(screen, (190, 190, 190), (500, 20, 60, 60))
        pygame.draw.rect(screen, (190, 190, 190), (570, 20, 60, 60))
        font = pygame.font.Font(None, 20)

        string_rendered2 = font.render('Doxicide', 1, pygame.Color('white'))
        string_rendered1 = font.render('Artensia', 1, pygame.Color('white'))
        screen.blit(string_rendered1, (502, 80))
        screen.blit(string_rendered2, (572, 80))

        zel1 = pygame.transform.scale(load_image('small.jpg'), (60, 60))
        zel1.set_colorkey((0, 0, 0))
        screen.blit(zel1, (500, 20))
        zel2 = pygame.transform.scale(load_image('big.jpg'), (60, 60))
        zel2.set_colorkey((0, 0, 0))
        screen.blit(zel2, (570, 20))
        kol_vo_zel1 = font.render(str(self.bigg), 1, pygame.Color('white'))
        screen.blit(kol_vo_zel1, (597, 68))
        kol_vo_zel2 = font.render(str((self.smalll)), 1, pygame.Color('white'))
        screen.blit(kol_vo_zel2, (527, 68))
        if is_inventory == True:
            pygame.draw.rect(screen, (220, 225, 227), (28, 10, 350, 100))
            font1 = pygame.font.Font(None, 30)
            font2 = pygame.font.Font(None, 20)
            kol_vo_money = font1.render(f'{self.money}$', 1, pygame.Color('black'))
            text_small = font2.render('Artensia', 1, pygame.Color('black'))
            text_big = font2.render('Doxicide', 1, pygame.Color('black'))
            screen.blit(kol_vo_money, (30, 15))
            screen.blit(text_small, (98, 52))
            screen.blit(text_big, (203, 52))
        if is_inventory == True:
            zel_invent1 = pygame.transform.scale(load_image('small.jpg'), (35, 35))
            zel_invent2 = pygame.transform.scale(load_image('big.jpg'), (35, 35))
            zel_invent1.set_colorkey((0, 0, 0))
            zel_invent2.set_colorkey((0, 0, 0))
            screen.blit(zel_invent1, (107, 14))
            screen.blit(zel_invent2, (213, 14))
            plus = pygame.transform.scale(load_image('+.png'), (20, 20))
            plus.set_colorkey((255, 255, 255))
            screen.blit(plus, (175, 32))
            screen.blit(plus, (175, 78))



    def get_cell(self, mouse_pos):
        print(mouse_pos[0], mouse_pos[1])
        if mouse_pos[0] in range(self.left, self.width * self.cell_size + self.left) and \
                mouse_pos[1] in range(self.top, self.height * self.cell_size + self.top):
            return (mouse_pos[0] - self.left) // self.cell_size, (mouse_pos[1] - self.top) // self.cell_size
        elif mouse_pos[0] in range(self.left + self.butgocord,
                                   self.left + self.butgocord + 50) and mouse_pos[1] in range(
            self.height * self.cell_size + self.top + 25, self.height * self.cell_size + self.top + 25 + 50):
            self.butnextactive = False
            if self.butgoactive:
                self.butgoactive = False
            else:
                self.butgoactive = True

            return None
        elif mouse_pos[0] in range(
                self.left + 10,
                                   self.left + self.healthbar + 10) and mouse_pos[1] in range(
            self.height * self.cell_size + self.top + 65, self.height * self.cell_size + self.top + 65 + 10):
            self.butgoactive = False
            self.butweap1active = False
            self.butweap2active = False
            if self.butnextactive:
                self.butnextactive = False
            else:
                self.butnextactive = True
            if self.butnextactive:
                neenemies = self.enemies.copy()
                self.enemies.clear()
                for elem in neenemies:
                    evildude = neenemies[elem]
                    sp = []
                    pos_x = evildude.pos[0]
                    pos_y = evildude.pos[1]
                    kol = evildude.range
                    prx = pos_x
                    pry = pos_y
                    sp22 = []
                    while (pos_x, pos_y) != (self.playerx, self.playery) and kol > 0:

                        prx = pos_x
                        pry = pos_y
                        if pos_x != self.playerx:
                            pos_x += (self.playerx - pos_x) // abs(self.playerx - pos_x)
                        if pos_y != self.playery:
                            pos_y += (self.playery - pos_y) // abs(self.playery - pos_y)
                        kol -= 1
                        sp22.append((pos_x, pos_y))
                        print(sp22)
                    ishenear = True
                    for i in range(len(sp22) - 1, -1, -1):
                        pos_x = sp22[i][0]
                        pos_y = sp22[i][1]
                        if self.board[pos_y][pos_x] == '@' or self.board[pos_y][pos_x] in ['e', 'e1', 'e32', 'e12', 'e3']:
                            print(evildude.pos[0], evildude.pos[1])
                        else:
                            print(evildude.pos[0], evildude.pos[1])
                            self.boardshow[evildude.pos[1]][evildude.pos[0]] = '0'
                            self.board[evildude.pos[1]][evildude.pos[0]] = '.'
                            evildude.pos = (pos_x, pos_y)
                            print(pos_x, pos_y)
                            self.enemies[(pos_x, pos_y)] = evildude
                            self.board[pos_y][pos_x] = 'e'
                            self.boardshow[pos_y][pos_x] = 'e'
                            ishenear = False
                            break
                    if ishenear:
                        self.hero.health -= evildude.damage
                        self.enemies[(evildude.pos[0], evildude.pos[1])] = evildude
                print(self.enemies)
                cell_coords = [self.playerx, self.playery]
                for i in range(self.height):
                    for j in range(self.width):
                        if self.boardshow[i][j] == 'e':
                            pass
                        elif self.boardshow[i][j] == 'e1' or self.boardshow[i][j] == 'e12' or self.boardshow[i][j] == 'e3' or self.boardshow[i][j] == 'e32':
                            self.boardshow[i][j] = 'e'
                        else:
                            self.boardshow[i][j] = '0'
                        if self.board[i][j] != 'e' and self.board[i][j] != '@':
                            self.board[i][j] = '.'
                self.boardshow[self.playery][self.playerx] = 'b'
                self.boardshow[cell_coords[1]][cell_coords[0]] = '@'
                self.board[self.playery][self.playerx] = '.'
                self.board[cell_coords[1]][cell_coords[0]] = '@'
                for i in range(len(self.boardshow)):
                    for j in range(len(self.boardshow[i])):
                        if self.boardshow[i][j] == 'e' or self.boardshow[i][j] == 'e2':
                            if abs(self.playery - i) <= self.weap2range and abs(self.playerx - j) <= self.weap2range:
                                self.boardshow[i][j] = 'e3'
                            if abs(self.playery - i) <= self.hero.range and abs(self.playerx - j) <= self.hero.range:
                                self.boardshow[i][j] = 'e1'
                for i1 in range(self.hero.range * -1, self.hero.range + 1):
                    if 0 <= i1 + cell_coords[1] <= self.height - 1:
                        for j in range(-1, 2):
                            if 0 <= j + cell_coords[0] <= self.width - 1:
                                if self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] != '@' and \
                                        self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] not in ['e', 'e1', 'e12', 'e3', 'e32']:
                                    self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] = 'b'
                                if self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] == 'e':
                                    self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] = 'e1'
                                if self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] == 'e2':
                                    self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] = 'e12'


        elif mouse_pos[0] in range(self.left + self.butweap1cord, self.left + self.butweap1cord + 200) and mouse_pos[1]\
                in range(self.height * self.cell_size + self.top + 25, self.height * self.cell_size + self.top + 75):
            self.butgoactive = False
            self.butnextactive = False
            if self.butweap1active:
                self.butweap1active = False
            else:
                self.butweap1active = True
            for i in range(len(self.boardshow)):
                for j in range(len(self.boardshow[i])):
                    print(self.boardshow[i][j], end='')
                print()

        elif mouse_pos[0] in range(
                self.left + self.butweap2cord,
                                   self.left + self.butweap2cord + 200) and mouse_pos[1] in range(
            self.height * self.cell_size + self.top +
                              25, self.height * self.cell_size + self.top + 75):
            self.butweap1active = False
            self.butgoactive = False
            self.butnextactive = False
            if self.butweap2active:
                self.butweap2active = False
            else:
                self.butweap2active = True
            for i in range(len(self.boardshow)):
                for j in range(len(self.boardshow[i])):
                    print(self.boardshow[i][j], end='')
                print()

        elif mouse_pos[0] in range(500, 561) and mouse_pos[1] in range(20, 81):
            font = pygame.font.Font(None, 20)
            string_rendered_small = font.render(f'{self.smalll}', 1, pygame.Color('white'))
            screen.blit(string_rendered_small, (500, 78))
            if self.smalll > 0:
                if sound == True:
                    pygame.mixer.music.load('зелье.mp3')
                    pygame.mixer.music.play(0)
                self.smalll -= 1
                if self.hero.health < 100:
                    if self.hero.health < 75:
                        self.hero.health += 25
                    else:
                        self.hero.health = 100
            else:
                pygame.mixer.music.load('зелье.mp3')
                pygame.mixer.music.play(0)

        elif mouse_pos[0] in range(570, 631) and mouse_pos[1] in range(20, 81):

            font = pygame.font.Font(None, 20)
            string_rendered_big = font.render(str(), 1, pygame.Color('white'))
            screen.blit(string_rendered_big, (578, 78))
            if self.bigg > 0:
                if sound == True:
                    pygame.mixer.music.load('большое зелье.mp3')
                    pygame.mixer.music.play(0)
                self.bigg -= 1
                if self.hero.health < 100:
                    if self.hero.health < 50:
                        self.hero.health += 50
                    else:
                        self.hero.health = 100
            else:
                pygame.mixer.music.load('зелье.mp3')
                pygame.mixer.music.play(0)

        elif is_inventory == True and mouse_pos[0] in range(175, 192) and mouse_pos[1] in range(35, 50):
            if sound == True:
                pygame.mixer.music.load('покупка.mp3')
                pygame.mixer.music.play(0)
            if self.money > 3:
                self.money -= 3
                self.smalll += 1

        elif is_inventory == True and mouse_pos[0] in range(175, 192) and mouse_pos[1] in range(82, 96):
            if sound == True:
                pygame.mixer.music.load('покупка.mp3')
                pygame.mixer.music.play(0)
            if self.money > 5:
                self.money -= 5
                self.bigg += 1



    def on_click(self, cell_coords):
        print(cell_coords)

        if cell_coords is not None:
            print(self.boardshow[cell_coords[1]][cell_coords[0]])
            if self.butgoactive and self.boardshow[cell_coords[1]][cell_coords[0]] == 'bl':
                self.boardshow[self.playery][self.playerx] = 'b'
                self.boardshow[cell_coords[1]][cell_coords[0]] = '@'
                self.board[self.playery][self.playerx] = '.'
                self.board[cell_coords[1]][cell_coords[0]] = '@'
                self.butgoactive = False
                self.playerx = cell_coords[0]
                self.playery = cell_coords[1]
                self.hero.pos = (self.playerx, self.playery)
                print(self.hero.pos)
                for i in range(self.height):
                    for j in range(self.width):
                        if self.boardshow[i][j] == 'e1' or self.boardshow[i][j] == 'e12' or \
                                self.boardshow[i][j] == 'e3' or self.boardshow[i][j] == 'e32':
                            self.boardshow[i][j] = 'e'

                        if self.boardshow[i][j] == 'e' or self.boardshow[i][j] == 'e2':
                            if abs(self.playery - i) <= self.weap2range and abs(self.playerx - j) <= self.weap2range:
                                self.boardshow[i][j] = 'e3'
                            if abs(self.playery - i) <= self.hero.range and abs(self.playerx - j) <= self.hero.range:
                                self.boardshow[i][j] = 'e1'
                for i in range(len(self.boardshow)):
                    for j in range(len(self.boardshow[i])):
                        print(self.boardshow[i][j], end='')
                    print()
            elif self.butweap1active and (self.boardshow[cell_coords[1]][cell_coords[0]] == 'e1' or
                                       self.boardshow[cell_coords[1]][cell_coords[0]] == 'e12'):
                self.enemies[(cell_coords[0], cell_coords[1])].health -= self.hero.damage
                print('ouch', self.enemies[(cell_coords[0], cell_coords[1])].health)
                self.butweap1active = False
                if self.enemies[(cell_coords[0], cell_coords[1])].health <= 0:
                    del self.enemies[(cell_coords[0], cell_coords[1])]
                    self.kolenemies -= 1
                    self.boardshow[cell_coords[1]][cell_coords[0]] = '0'
                    self.board[cell_coords[1]][cell_coords[0]] = '.'
                self.get_cell((self.left + 11, self.height * self.cell_size + self.top + 66))

            elif self.butweap2active and (self.boardshow[cell_coords[1]][cell_coords[0]] == 'e1' or
                                       self.boardshow[cell_coords[1]][cell_coords[0]] == 'e12' or
                                          self.boardshow[cell_coords[1]][cell_coords[0]] == 'e3' or
                                          self.boardshow[cell_coords[1]][cell_coords[0]] == 'e32') and self.energyused \
                    >= self.weap2mana:
                self.enemies[(cell_coords[0], cell_coords[1])].health -= self.hero.damage
                print('ouch', self.enemies[(cell_coords[0], cell_coords[1])].health)
                self.butweap2active = False
                if self.enemies[(cell_coords[0], cell_coords[1])].health <= 0:
                    del self.enemies[(cell_coords[0], cell_coords[1])]
                    self.kolenemies -= 1
                    self.boardshow[cell_coords[1]][cell_coords[0]] = '0'
                    self.board[cell_coords[1]][cell_coords[0]] = '.'
                self.get_cell((self.left + 11, self.height * self.cell_size + self.top + 66))
                self.energyused -= self.weap2mana

    def get_seen(self, mouse_pos):
        for i in range(self.height):
            for j in range(self.width):
                if self.boardshow[i][j] == '1':
                    self.boardshow[i][j] = '0'
                elif self.boardshow[i][j] == 'bl':
                    self.boardshow[i][j] = 'b'
                elif self.boardshow[i][j] == 'e2':
                    self.boardshow[i][j] = 'e'
                elif self.boardshow[i][j] == 'e12':
                    self.boardshow[i][j] = 'e1'
                elif self.boardshow[i][j] == 'e32':
                    self.boardshow[i][j] = 'e3'

        if mouse_pos[0] in range(self.left, self.width * self.cell_size + self.left) and \
                mouse_pos[1] in range(self.top, self.height * self.cell_size + self.top):
            sp = [(mouse_pos[0] - self.left) // self.cell_size, (mouse_pos[1] - self.top) // self.cell_size]
            if self.boardshow[sp[1]][sp[0]] == 'b':
                self.boardshow[sp[1]][sp[0]] = 'bl'
            elif self.boardshow[sp[1]][sp[0]] == '0':
                self.boardshow[sp[1]][sp[0]] = '1'
            elif self.boardshow[sp[1]][sp[0]] == 'e':
                self.boardshow[sp[1]][sp[0]] = 'e2'
            elif self.boardshow[sp[1]][sp[0]] == 'e1':
                self.boardshow[sp[1]][sp[0]] = 'e12'
            elif self.boardshow[sp[1]][sp[0]] == 'e3':
                self.boardshow[sp[1]][sp[0]] = 'e32'






def load_level(filename):
    fullfilename = os.path.join('data', filename)
    with open(fullfilename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))




start_screen()
pygame.mixer.Channel(1).stop()
pygame.init()
size = wigth, height = 800, 500
screen = pygame.display.set_mode(size)
mapsource = 0
with open('data//gameinfo.txt', encoding='utf-8') as file:
    sp = file.readlines()
    mapsource = int(sp[0][0])
cn = sqlite3.connect('database.db')
cur = cn.cursor()
records = cur.execute(f'''SELECT * FROM levels''').fetchall()
levels = dict()
for elem in records:
    levels[elem[0]] = elem
board = Gameboard(10, 3, load_level(levels[mapsource][1]))
is_inventory = False
running = True
sound = True
sek = time.time()
a = 0
sound_gl = True

while running:
    for event in pygame.event.get():
        if sound_gl == True and a == 0:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound('главная музыка.mp3'))
            a = 1
        elif sound_gl == False:
            pygame.mixer.Channel(0).stop()
            a = 0
        keys = pygame.key.get_pressed()
        button = Button(50, 50)
        button.draw(50, 50, 'wow')
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
        if keys[pygame.K_UP]:
            if is_inventory == False:
                is_inventory = True
            else:
                is_inventory = False
        if keys[pygame.K_DOWN]:
            if sound == True:
                sound = False
            else:
                sound = True
        if keys[pygame.K_HOME]:
            if sound_gl == True:
                sound_gl = False
            else:
                sound_gl = True
        board.get_seen(pygame.mouse.get_pos())
        if board.kolenemies <= 0:

            print(True)
            if mapsource == len(levels):
                running = False
            else:
                mapsource += 1
                board = Gameboard(10, 3, load_level((levels[mapsource][1])))

    screen.fill((160, 160, 160))
    board.render(screen)
    pygame.display.flip()

