import pygame
from support import import_folder


class Tile(pygame.sprite.Sprite):
    """ Класс плитки"""

    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift  # Прокрутка мира


class StaticTile(Tile):
    """Класс статической плитки"""

    def __init__(self, pos, size, surface):
        super().__init__(pos, size)

        self.image = surface


class Crate(StaticTile):
    """Класс ящика"""

    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.image.load('graphics/terrain/crate.png').convert_alpha())  # Так как плитка одна, она загружается внутри класса
        offset_y = pos[1] + size  # Корректировка размера так как ящик не 64 на 64 пикселя
        self.rect = self.image.get_rect(bottomleft=(pos[0], offset_y))  # Корректировка изображения


class AnimatedTile(Tile):
    """Класс анимации плитки"""

    def __init__(self, pos, size, path):
        super().__init__(pos, size)

        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.10

        if self.frame_index > len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift


class Coin(AnimatedTile):
    """Класс монеты"""

    def __init__(self, pos, size, path, value):
        super().__init__(pos, size, path)
        center_x = pos[0] + int(size // 2)
        center_y = pos[1] + int(size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.value = value


class Palm(AnimatedTile):
    """Класс пальмы"""

    def __init__(self, pos, size, path, offset):
        super().__init__(pos, size, path)
        center_y = pos[1] - offset
        self.rect.topleft = (pos[0], center_y)


class Potion(AnimatedTile):
    """Класс зелья"""

    def __init__(self, pos, size, path):
        super().__init__(pos, size, path)
        self.frames = import_folder(path, 2.5)
        self.rect = self.image.get_rect(center=(pos[0] + int(size // 2), pos[1] + 20))


class SelectionEffect(AnimatedTile):

    def __init__(self, pos, size, path):
        super().__init__(pos, size, path)

    def animate(self):
        self.frame_index += 0.10

        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


class Heart(AnimatedTile):
    """Класс Сердце"""

    def __init__(self, pos, size, path):
        super().__init__(pos, size, path)
        self.frames = import_folder(path, 1.3)
        self.rect = self.image.get_rect(center=(pos[0] + int(size // 2), pos[1] + 20))
