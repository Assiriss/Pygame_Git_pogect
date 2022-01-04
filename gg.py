import os

import pygame

pygame.init()
size = width, height = 500, 500
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
        self.damage = 10
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
        self.playerx = 0
        self.playery = 0
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
                    newenem = Enemy(zi, i, load_image('mar.png'))
                    if map[i][zi] == 'd':
                        newenem.obozn = 'd'
                        newenem.allhealth = 100
                        newenem.health = newenem.health
                        newenem.range = 0
                        newenem.damage = 0
                        newenem.defend = 0
                    self.enemies[(zi, i)] = newenem
                    self.boardshow[i][zi] = 'e'
                    g.append('e')
                else:
                    g.append(map[i][zi])
                    if map[i][zi] == '@':
                        self.playerx = zi
                        self.playery = i
                        self.boardshow[i][zi] = '@'
                        self.hero.pos = (i, zi)
                        for i1 in range(self.hero.range * -1, self.hero.range + 1):
                            if 0 <= i1 + i <= self.height - 1:
                                for j in range(-1, 2):
                                    if 0 <= j + zi <= self.width - 1:
                                        if self.boardshow[i1 + i][j + zi] != '@' and self.boardshow[i1 + i][j + zi] != 'e':
                                            self.boardshow[i1 + i][j + zi] = 'b'
                                        elif self.boardshow[i1 + i][j + zi] == 'e':
                                            self.boardshow = 'e1'



            self.board.append(g)
        self.butgosize = 40
        self.butgoactive = False
        self.butgoused = False
        self.butgocord = 160
        self.butweapsize = (60, 20)
        self.butweap1active = False
        self.butweapused = False
        self.butweap1cord = 250
        self.butweap2cord = 130
        self.butweap2active = False
        self.butnextsize = 40
        self.butnextactive = False
        self.butnextcord = 180
        self.healthbar = 100
        self.healthused = 100
        self.energybar = 100
        self.energyused = 100
        self.interheight = 80

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
                if self.butweap1active and (self.boardshow[j // self.cell_size][i // self.cell_size] == 'e1' or
                                            self.boardshow[j // self.cell_size][i // self.cell_size] == 'e12'):
                    pygame.draw.rect(screen, (153, 0, 0),  (i + self.left, j + self.top, self.cell_size, self.cell_size))
                if self.boardshow[j // self.cell_size][i // self.cell_size] == 'e2' or \
                        self.boardshow[j // self.cell_size][i // self.cell_size] == 'e12':
                    pygame.draw.rect(screen, (255, 102, 0), (i + self.left, j + self.top, self.cell_size, self.cell_size))
                    health = self.enemies[(i // self.cell_size, j // self.cell_size)].health
                    alhealth = self.enemies[(i // self.cell_size, j // self.cell_size)].allhealth
                    pygame.draw.rect(screen, (0, 0, 0), (15, 15, alhealth * 2, 30))
                    pygame.draw.rect(screen, (255, 0, 0), (15, 15, health * 2, 30))
                if self.boardshow[j // self.cell_size][i // self.cell_size] == '1' or self.boardshow[j // self.cell_size][i // self.cell_size] == 'bl' and not self.butgoactive:
                    pygame.draw.rect(screen, (255, 215, 0),
                                     (i + self.left, j + self.top, self.cell_size, self.cell_size))
                if self.board[j // self.cell_size][i // self.cell_size] == '@':
                    pygame.draw.circle(screen, (255, 0, 255), (i + self.left + self.cell_size // 2, j + self.top +
                                                               self.cell_size // 2), 25)
                if self.board[j // self.cell_size][i // self.cell_size] != '@' and self.board[j // self.cell_size][i // self.cell_size] != '.':
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
            pygame.draw.rect(screen, (255, 0, 0), (self.left + self.butweap1cord, self.height * self.cell_size + self.top +
                                                   25, 200, 50))
        else:
            pygame.draw.rect(screen, (255, 255, 0),
                             (self.left + self.butweap1cord, self.height * self.cell_size + self.top +
                              25, 200, 50))

    def get_cell(self, mouse_pos):
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
            self.butnextactive = True
            cell_coords = [self.playerx, self.playery]
            for i in range(self.height):
                for j in range(self.width):
                    if self.boardshow[i][j] == 'e':
                        pass
                    elif self.boardshow[i][j] == 'e1' or self.boardshow[i][j] == 'e12':
                        self.boardshow[i][j] = 'e'
                    else:
                        self.boardshow[i][j] = '0'
                    if self.board[i][j] != 'e' and self.board[i][j] != '@':
                        self.board[i][j] = '.'
            self.boardshow[self.playery][self.playerx] = 'b'
            self.boardshow[cell_coords[1]][cell_coords[0]] = '@'
            self.board[self.playery][self.playerx] = '.'
            self.board[cell_coords[1]][cell_coords[0]] = '@'
            for i1 in range(self.hero.range * -1, self.hero.range + 1):
                if 0 <= i1 + cell_coords[1] <= self.height - 1:
                    for j in range(-1, 2):
                        if 0 <= j + cell_coords[0] <= self.width - 1:
                            if self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] != '@' and \
                                    self.boardshow[i1 + cell_coords[1]][j + cell_coords[0]] != 'e':
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
            elif self.butweap1active and (self.boardshow[cell_coords[1]][cell_coords[0]] == 'e1' or
                                       self.boardshow[cell_coords[1]][cell_coords[0]] == 'e12'):
                self.enemies[(cell_coords[0], cell_coords[1])].health -= self.hero.damage
                print('ouch', self.enemies[(cell_coords[0], cell_coords[1])].health)
                self.butweap1active = False
                if self.enemies[(cell_coords[0], cell_coords[1])].health <= 0:
                    del self.enemies[(cell_coords[0], cell_coords[1])]
                    self.boardshow[cell_coords[1]][cell_coords[0]] = '0'
                    self.board[cell_coords[1]][cell_coords[0]] = '.'
                self.get_cell((self.left + 11, self.height * self.cell_size + self.top + 66))

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
            else:
                pass



def load_level(filename):
    fullfilename = os.path.join('data', filename)
    with open(fullfilename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


pygame.init()
size = wigth, height = 800, 500
screen = pygame.display.set_mode(size)
board = Gameboard(10, 3, load_level('test.txt'))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
        board.get_seen(pygame.mouse.get_pos())
    screen.fill((0, 0, 0))
    board.render(screen)
    pygame.display.flip()
