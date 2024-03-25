import pygame
import sys

from settings import *
from level import Level
from game_data import level_0
from overworld import OverWorld


class Game:
    """Класс игры"""

    def __init__(self):
        self.max_level = 3
        self.overworld = OverWorld(2, self.max_level, screen)

    def run(self):
        self.overworld.run()


pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_0, screen)
game = Game()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('gray')
    game.run()
    # level.run()

    pygame.display.update()
    clock.tick(60)
