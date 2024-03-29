import pygame
import sys

from settings import *
from level import Level
from overworld import OverWorld
from ui import UI


class Game:
    """Класс игры"""

    def __init__(self):

        # Игровые атрибуты
        self.max_level = 0
        self.max_health = 100
        self.cor_health = 100
        self.coins = 0

        # Внешний мир
        self.overworld = OverWorld(0, self.max_level, screen, self.create_level)
        self.status = 'overworld'

        self.ui = UI(screen)

    def create_level(self, current_level):
        """Создание уровня"""

        self.level = Level(current_level, screen, self.create_overworld, self.change_coins)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = OverWorld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'

    def change_coins(self, amount):
        self.coins += amount

    def run(self):

        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.cor_health, self.max_health)
            self.ui.show_coins(self.coins)


pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('gray')
    game.run()

    pygame.display.update()
    clock.tick(60)
