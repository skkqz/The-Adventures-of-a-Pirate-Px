import pygame
from os import walk
from csv import reader
from settings import tile_size


def import_folder(path, scale=None):

    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image  # Полный путь к изображению
            image_surf = pygame.image.load(full_path).convert_alpha()
            if scale:
                image_surf = pygame.transform.scale(image_surf, (int(image_surf.get_width() * scale),
                                                                 int(image_surf.get_height()) * scale))
            surface_list.append(image_surf)

    return surface_list


def import_csv_layout(path):

    terrain_map = []
    with open(path) as maps:
        level = reader(maps, delimiter=',')

        for row in level:
            terrain_map.append(list(row))

    return terrain_map


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    title_num_x = int(surface.get_size()[0] / tile_size)
    title_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    for row in range(title_num_y):
        for col in range(title_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles
