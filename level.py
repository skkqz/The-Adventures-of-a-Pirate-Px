import pygame

from tiles import Tile, StaticTile, Crate, Coin, Palm, Potion, SelectionEffect
from enemy import Enemy
from settings import tile_size, screen_width, screen_height
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from decoration import Sky, Water, Cloud
from game_data import levels


class Level:
    """Класс уровня"""

    def __init__(self, current_level, surface, create_overworld, change_coins, change_health):
        # Настройка уровня
        self.display_surface = surface  # Установка поверхности для отображения
        # self.setup_level(level_data)  # Инициализация уровня
        self.world_shift = 0  # Инициализация сдвига мира
        self.current_x = None

        # Связь с overworld
        self.create_overworld = create_overworld
        self.current_level = current_level
        self.level_data = levels[self.current_level]
        self.new_max_level = self.level_data['unlock']

        # Пыль
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # Установка игрока
        player_layout = import_csv_layout(self.level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # Пользовательский интерфейс
        self.change_coins = change_coins

        # Установка местности
        terrain_layout = import_csv_layout(self.level_data['terrain'])
        self.terrain_sprites = self.create_title_group(terrain_layout, 'terrain')

        # Установка травы
        grass_layout = import_csv_layout(self.level_data['grass'])
        self.grass_sprites = self.create_title_group(grass_layout, 'grass')

        # Установка ящиков
        crate_layout = import_csv_layout(self.level_data['crates'])
        self.crate_sprites = self.create_title_group(crate_layout, 'crates')

        # Установка бутылок зелья
        if self.level_data.get('potions'):
            potion_layout = import_csv_layout(self.level_data['potions'])
            self.potion_sprites = self.create_title_group(potion_layout, 'potions')

        # Эффект поднятия
        self.selection_effect_sprite = pygame.sprite.Group()

        # Установка монет
        coin_layout = import_csv_layout(self.level_data['coins'])
        self.coin_sprites = self.create_title_group(coin_layout, 'coins')

        # Установка пальм переднего плана
        fg_palms_layout = import_csv_layout(self.level_data['fg_palms'])
        self.fg_palms_sprites = self.create_title_group(fg_palms_layout, 'fg_palms')

        # Установка пальм заднего фона
        bg_palms_layout = import_csv_layout(self.level_data['bg_palms'])
        self.bg_palms_sprites = self.create_title_group(bg_palms_layout, 'bg_palms')

        # Установка врагов
        enemy_layout = import_csv_layout(self.level_data['enemies'])
        self.enemy_sprites = self.create_title_group(enemy_layout, 'enemies')

        # Взрыв врагов
        self.explosion_sprite = pygame.sprite.Group()

        # Ограничение для врагов
        constraint_layout = import_csv_layout(self.level_data['constraints'])
        self.constraint_sprites = self.create_title_group(constraint_layout, 'constraints')

        # Задний фон
        self.sky = Sky(7)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 20, level_width)
        self.clouds = Cloud(400, level_width, 20)

    def create_title_group(self, layout, type_t):

        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):

                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type_t == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[(int(val))]
                        sprite = StaticTile((x, y), tile_size, tile_surface)
                    if type_t == 'grass':
                        grass_tile_list = import_cut_graphics('graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile((x, y), tile_size, tile_surface)
                    if type_t == 'crates':
                        sprite = Crate((x, y), tile_size)  # Создание ящика
                    if type_t == 'coins':
                        if val == '0':
                            sprite = Coin((x, y), tile_size, 'graphics/coins/gold/', 5)
                        elif val == '1':
                            sprite = Coin((x, y), tile_size, 'graphics/coins/silver/', 1)
                    if type_t == 'potions':
                        sprite = Potion((x, y), tile_size, 'graphics/potion/Red Potion')
                    if type_t == 'fg_palms':
                        if val == '1':
                            sprite = Palm((x, y), tile_size, 'graphics/terrain/palm_large', 72)
                        if val == '2':
                            sprite = Palm((x, y), tile_size, 'graphics/terrain/palm_small', 38)
                    if type_t == 'bg_palms':
                        sprite = Palm((x, y), tile_size, 'graphics/terrain/palm_bg', 64)
                    if type_t == 'enemies':
                        sprite = Enemy((x, y), tile_size, 'graphics/enemy/run')
                    if type_t == 'constraints':
                        sprite = Tile((x, y), tile_size)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health)
                    self.player.add(sprite)
                if val == '1':
                    hut_surface = pygame.image.load('graphics/character/hat.png')
                    sprite = StaticTile((x, y), tile_size, hut_surface)
                    self.goal.add(sprite)

    def create_jump_particles(self, pos):
        """Создание частиц при прыжке"""

        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)

        jump_particle_sprite = ParticleEffect(pos, 'jump')  # Создание частицы пыли при прыжке
        self.dust_sprite.add(jump_particle_sprite)  # Добавление частицы в группу

    def get_player_on_ground(self):
        """Проверка, находится ли игрок на земле"""

        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def crate_landing_dust(self):
        """Создание частиц пыли при приземлении"""

        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,
                                                'land')  # Создание частицы пыли при приземлении
            self.dust_sprite.add(fall_dust_particle)  # Добавление частицы в группу

    def setup_level(self, layout):
        """Установка уровня на основе предоставленных данных"""

        self.tiles = pygame.sprite.Group()  # Создание группы спрайтов для тайлов
        self.player = pygame.sprite.GroupSingle()  # Создание группы спрайтов для игрока

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size  # Вычисление координаты x
                y = row_index * tile_size  # Вычисление координаты y

                if cell == 'X':
                    tile = Tile((x, y), tile_size)  # Создание тайла
                    self.tiles.add(tile)  # Добавление тайла в группу
                if cell == 'P':
                    player_sprite = Player((x, y), self.display_surface, self.crate_jum_particles)  # Создание игрока
                    self.player.add(player_sprite)  # Добавление игрока в группу

    def scroll_x(self):
        """Прокрутка мира по горизонтали"""

        player = self.player.sprite  # Получение спрайта игрока из группы
        player_x = player.rect.centerx  # Получение координаты x центра игрока
        direction_x = player.direction.x  # Получение направления движения игрока по оси x

        if player_x < (screen_width / 4) and direction_x < 0:
            self.world_shift = 5  # Сдвиг мира вправо
            player.speed = 0
        elif player_x > (screen_width - (screen_width / 4)) and direction_x > 0:
            self.world_shift = -5  # Сдвиг мира влево
            player.speed = 0
        else:
            self.world_shift = 0  # Остановка сдвига мира
            player.speed = 5

    def horizontal_movement_collision(self):
        """Обработка столкновений по горизонтали"""

        player = self.player.sprite
        # Обновляем позицию игрока в соответствии с направлением движения и скоростью
        player.rect.x += (player.direction.x * player.speed)

        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()

        # Проверяем столкновения игрока с плитками
        for sprite in collidable_sprites:
            # Если произошло столкновение
            if sprite.rect.colliderect(player.rect):
                # Если игрок движется влево
                if player.direction.x < 0:
                    # Помещаем игрока вправо от крайней правой стороны плитки
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                # Если игрок движется вправо
                elif player.direction.x > 0:
                    # Помещаем игрока влево от крайней левой стороны плитки
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right < self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        """Обработка столкновений по вертикали"""

        player = self.player.sprite
        player.apply_gravity()  # Применяем гравитацию к игроку

        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:  # Если игрок движется вниз
                    player.rect.bottom = sprite.rect.top  # Помещаем игрока над плиткой
                    player.direction.y = 0  # Обнуляем скорость по вертикали
                    player.on_ground = True
                elif player.direction.y < 0:  # Если игрок движется вверх
                    player.rect.top = sprite.rect.bottom  # Помещаем игрока под плиткой
                    player.direction.y = 0  # Обнуляем скорость по вертикали
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.on_ground and player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def enemy_collision_reverse(self):
        """Проверка столкновений врага с препятствием"""

        for enemy in self.enemy_sprites.sprites():
            # Если противник сталкивается с препятствием, он разворачивается
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def check_death(self):

        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        """Проверка поднятия монеты"""
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        for coin in collided_coins:
            coin_effect = SelectionEffect((coin.rect.centerx - 10, coin.rect.centery - 5), tile_size,
                                          'graphics/coins/Coin Effect')
            if coin == 0:
                self.change_coins(coin.value)
            else:
                self.change_coins(coin.value)
            coin.kill()
            self.selection_effect_sprite.add(coin_effect)

    def check_potion_collisions(self):
        """Проверка поднятия банки зелья"""
        collided_potions = pygame.sprite.spritecollide(self.player.sprite, self.potion_sprites, True)
        for potion in collided_potions:
            if potion:
                potion_effect = SelectionEffect(potion.rect.center, tile_size, 'graphics/potion/Potion Effect')

                potion.kill()
                self.selection_effect_sprite.add(potion_effect)

    def check_enemy_collisions(self):
        """Проверка столкновений с врагом"""

        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom

                # Если игрок находится сверху врага и меньше центра, то враг умирает
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion', 0.50)
                    self.explosion_sprite.add(explosion_sprite)

                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def run(self):
        """Запуск игрового цикла"""

        # Небо
        self.sky.draw(self.display_surface)
        # self.sky.update(self.world_shift)

        # Фон облаков
        self.clouds.draw(self.display_surface, self.world_shift)

        # Пальмы заднего плана
        self.bg_palms_sprites.draw(self.display_surface)
        self.bg_palms_sprites.update(self.world_shift)

        # Земля
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)

        # Ящики
        self.crate_sprites.draw(self.display_surface)
        self.crate_sprites.update(self.world_shift)

        # Трава
        self.grass_sprites.draw(self.display_surface)
        self.grass_sprites.update(self.world_shift)

        # Монеты
        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)

        # Бутылки с зельем
        if self.level_data.get('potions'):
            self.check_potion_collisions()

            self.potion_sprites.draw(self.display_surface)
            self.potion_sprites.update(self.world_shift)

        # Анимация поднятия зелья
        self.selection_effect_sprite.draw(self.display_surface)
        self.selection_effect_sprite.update(self.world_shift)

        # Враги
        self.enemy_sprites.draw(self.display_surface)
        self.enemy_sprites.update(self.world_shift)
        self.explosion_sprite.draw(self.display_surface)
        self.explosion_sprite.update(self.world_shift)

        # Ограничение движения врагов
        # self.constraint_sprites.draw(self.display_surface) # Не нужно отрисовывать, чтобы не видно было плитку
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()

        # Пальмы передний план
        self.fg_palms_sprites.draw(self.display_surface)
        self.fg_palms_sprites.update(self.world_shift)

        # Частицы пыли
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # Игрок
        self.player.update()  # Обновление игрока
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.crate_landing_dust()
        self.player.draw(self.display_surface)  # Отображение игрока на экране
        self.scroll_x()

        # игровой спрайт
        self.goal.draw(self.display_surface)
        self.goal.update(self.world_shift)

        self.check_death()
        self.check_win()
        self.check_coin_collisions()
        self.check_enemy_collisions()

        # Фон воды
        self.water.draw(self.display_surface, self.world_shift)
