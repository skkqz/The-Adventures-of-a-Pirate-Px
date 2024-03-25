import pygame
from support import import_folder


class Player(pygame.sprite.Sprite):
    """Класс игрока"""

    def __init__(self, pos, surface, crate_jum_particles):
        super().__init__()
        self.import_character_asserts()  # Импорт ассетов персонажа
        self.frame_index = 0  # Индекс текущего кадра анимации
        self.animation_speed = 0.15  # Скорость анимации
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)  # Прямоугольник, описывающий положение персонажа на экране

        # Частицы пыли
        self.import_dust_run_particles()  # Импорт ассетов частиц пыли
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface  # Поверхность для отображения
        self.crate_jum_particles = crate_jum_particles  # Функция для создания частиц при прыжке

        # Движение игрока
        self.speed = 5  # Скорость перемещения игрока
        self.direction = pygame.math.Vector2(0, 0)  # Направление движения игрока
        self.gravity = 0.8  # Гравитация
        self.jump_speed = -16  # Скорость прыжка

        # Статус игрока
        self.status = 'idle'  # Текущий статус игрока
        self.facing_right = True  # Направление взгляда игрока (вправо/влево)
        self.on_ground = False  # Находится ли игрок на земле
        self.on_ceiling = False  # Находится ли игрок под потолком
        self.on_left = False  # Находится ли игрок у левой стены
        self.on_right = False  # Находится ли игрок у правой стены

    def import_character_asserts(self):
        """Загрузка анимаций персонажа"""

        character_path = 'graphics/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

        # Загрузка анимаций персонажа
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self):
        """Импорт ассетов частиц пыли при беге"""

        self.dust_run_particles = import_folder('graphics/character/dust_particles/run')

    def animate(self):
        """Анимация персонажа"""

        animation = self.animations[self.status]  # Получаем анимацию из словаря анимаций по текущему статусу объекта

        self.frame_index += self.animation_speed  # Увеличиваем индекс кадра на скорость анимации

        # Если индекс кадра превысил количество кадров в анимации, возвращаемся к началу
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]   # Получаем изображение текущего кадра анимации

        # Если персонаж смотрит вправо, используем изображение без изменений
        if self.facing_right:
            self.image = image
        else:
            # Если персонаж смотрит влево, отражаем изображение по горизонтали
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

        # Обновление прямоугольника персонажа в зависимости от его положения на экране
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def run_dust_animate(self):
        """Анимация частиц пыли при беге"""

        if self.status == 'run' and self.on_ground:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index > len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def get_input(self):
        """Обработка пользовательского ввода"""

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()
            self.crate_jum_particles(self.rect.midbottom)

    def get_status(self):
        """Определение текущего статуса игрока"""

        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def apply_gravity(self):
        """Применение гравитации к игроку"""

        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        """Обработка прыжка"""

        self.direction.y = self.jump_speed

    def update(self):
        """Обновление состояния игрока"""

        self.get_input()  # Получение пользовательского ввода
        self.get_status()  # Определение текущего статуса игрока
        self.animate()  # Анимация игрока
        self.run_dust_animate()  # Анимация частиц пыли при беге
