import pygame
import os


class Map:
    def __init__(self, fps):
        self.TILE_SIZE = 128
        self.change = [0, 0]
        self.fps = fps
        with open("maps/map_number_1") as file:  # Открытие файла заготовленного скелета карты
            player_pos = list(map(int, file.readline().split()))
            print(player_pos)
            self.map_data = list(map(lambda x: list(map(int, x.split())), file.readlines()))
            self.player_x = player_pos[0] * self.TILE_SIZE
            self.player_y = player_pos[1] * self.TILE_SIZE

        self.all_tiles = pygame.sprite.Group()
        self.flightless_map = []  # Создание маршрутной карты для нелетающих противников
        self.flightless_sprite_group = pygame.sprite.Group()  # Создание группы спрайтов, не доступных для нелетающих противников

        for y in range(len(self.map_data)):
            row = []
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] in [0, 4]:
                    row.append(1)
                else:
                    row.append(0)
            self.flightless_map.append(row)

        self.tiles = self.load_tiles()

    # Загрузка спрайтов тайлов карты
    def load_tiles(self):
        tiles = {
            0: pygame.image.load(os.path.join("images/tiles", "grass.png")),
            1: pygame.image.load(os.path.join("images/tiles", "wall.png")),
            2: pygame.image.load(os.path.join("images/tiles", "water.png")),
            3: pygame.image.load(os.path.join("images/tiles", "lava.png")),
            4: pygame.image.load(os.path.join("images/tiles", "earth.png"))
        }
        for key in tiles:
            tile_sprite = pygame.sprite.Sprite()
            tile_sprite.image = pygame.transform.scale(tiles[key], (self.TILE_SIZE, self.TILE_SIZE))
            tile_sprite.rect = tile_sprite.image.get_rect()
            tiles[key] = tile_sprite
        return tiles

    # Отрисовка карты
    def draw_map(self, screen, camera_x, camera_y):
        self.all_tiles = pygame.sprite.Group()
        self.flightless_sprite_group = pygame.sprite.Group()
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                screen_x = x * self.TILE_SIZE - camera_x
                screen_y = y * self.TILE_SIZE - camera_y

                if -self.TILE_SIZE < screen_x < screen.get_width() and -self.TILE_SIZE < screen_y < screen.get_height():
                    current_tile = self.tiles[tile]
                    current_tile.rect.x, current_tile.rect.y = screen_x, screen_y
                    self.all_tiles.add(current_tile)

                    if tile in [1, 2, 3]:
                        self.flightless_sprite_group.add(current_tile)

                    self.all_tiles.draw(screen)

    def update(self, screen):
        self.change = [0, 0]
        speed = 300 // self.fps
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Движение Вверх
            pos1, pos2 = (self.player_y - 30 - speed, self.player_x - 10), (
                self.player_y - 30 - speed, self.player_x + 10)
            if self.step_condition(pos1, pos2):
                self.player_y -= speed
                self.change[1] -= speed

        if keys[pygame.K_s]:  # Движение Вниз
            pos1, pos2 = (self.player_y + 35 + speed, self.player_x - 10), (
                self.player_y + 35 + speed, self.player_x + 10)
            if self.step_condition(pos1, pos2):
                self.player_y += speed
                self.change[1] += speed

        if keys[pygame.K_a]:  # Движение Влево
            pos1, pos2 = (self.player_y - 30, self.player_x - 10 - speed), (
                self.player_y + 35, self.player_x - 10 - speed)
            if self.step_condition(pos1, pos2):
                self.player_x -= speed
                self.change[0] -= speed

        if keys[pygame.K_d]:  # Движение Вправо
            pos1, pos2 = (self.player_y - 30, self.player_x + 10 + speed), (
                self.player_y + 35, self.player_x + 10 + speed)
            if self.step_condition(pos1, pos2):
                self.player_x += speed
                self.change[0] += speed

        camera_x = self.player_x - screen.get_width() // 2
        camera_y = self.player_y - screen.get_height() // 2
        self.draw_map(screen, camera_x, camera_y)

    def step_condition(self, pos1, pos2):
        for i in (pos1, pos2):
            player_in_tiles_cor = (i[0] // self.TILE_SIZE, i[1] // self.TILE_SIZE)
            if self.map_data[player_in_tiles_cor[0]][player_in_tiles_cor[1]] not in [0, 4]:
                return False
        return True
