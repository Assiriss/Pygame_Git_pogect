import os
import random
import sys
import pygame
import pygame_menu
import pygame


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
    intro_text = ['Создатели проэкта:',
                  "Толмачев Никита",
                  "Зайцев Максим",
                  "Дружиннин дмитрий"]

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



running = True
start_screen()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

    pygame.display.flip()
pygame.quit()