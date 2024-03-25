import pygame
from tiles import AnimatedTile
from random import randint


class Enemy(AnimatedTile):
    """Класс врага"""

    def __init__(self, pos, size, path):
        super().__init__(pos, size, path)
        self.rect.y += size - self.image.get_size()[1]  # Подогнать размер изображение, чтобы враг стоял на земле

        self.speed = 2  # Скорость врага

    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()
