import pygame
import sys
import os
import math
import time
from enemies.spider import Spider


class Boss(pygame.sprite.Sprite):
    def __init__(self, *group, map_data, player, x, y, summons, difficult):
        super().__init__(*group)
        self.summons_group = summons
        self.frames = [self.load_image(f"boss.png")]
        self.map_data = map_data
        self.player = player
        self.difficult = difficult
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (180, 180))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.pos = [x, y]
        self.movement_type = 'vector'
        self.vector_time = 2
        self.circle_time = 0
        self.delta_time = time.time()
        self.dx = self.dy = self.dist = None
        self.speed = 850 if difficult == "Easy" else 1000
        self.clock = 0
        self.max_HP = 12_000 if difficult == "Easy" else 20_000
        self.HP = self.max_HP
        self.damage = 3 if difficult == 'Easy' else 4

        self.dashes = 0
        self.circle_step = 0

    def vector_move(self, change, dx, dy, dist, dt):
        try:
            dx, dy = (dx / dist * self.speed * dt), (dy / dist * self.speed * dt)

            self.pos[0] += dx - change[0]
            self.pos[1] += dy - change[1]

            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]

        except ZeroDivisionError:
            pass

    def circle_move(self, x, y):
        self.rect.centerx = x - 400 * math.cos(math.radians(75 + (self.circle_step // 100)))
        self.rect.centery = y - 400 * math.sin(math.radians(75 + (self.circle_step // 100)))

    def update(self, change, player, visible_sprites, screen, dt):
        info = pygame.display.Info()
        self.Boss_HP_bar(screen)
        if self.movement_type == 'vector':
            if self.vector_time > 0.7:
                self.dx, self.dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
                self.dist = math.hypot(self.dx, self.dy)
                self.delta_time = time.time()

                if self.dashes <= 7:
                    self.dashes += 1

            self.vector_move(change, self.dx, self.dy, self.dist, dt)

            if self.dashes > 7:
                self.movement_type = 'circle'
                self.delta_time = time.time()
            self.vector_time = time.time() - self.delta_time


        elif self.movement_type == 'circle':
            self.circle_step += 270
            self.circle_move(self.player.rect.centerx, self.player.rect.centery)

            self.dx, self.dy = player.rect.centerx - self.rect.x, player.rect.centery - self.rect.y
            self.dist = math.hypot(self.dx, self.dy)

            if self.circle_time > 2:
                self.movement_type = 'vector'
                self.dashes = 0
                self.delta_time = time.time()

                Spider(self.summons_group, map_data=self.map_data,
                                  player=self.player, x=self.rect.centerx, y=self.rect.centery, difficult=self.difficult)

            self.circle_time = time.time() - self.delta_time


        if -60 < self.rect.centerx < info.current_w * 1.1 and -60 < self.rect.centery < info.current_h * 1.1:
            visible_sprites.add(self)
            self.clock += dt
            if self.clock >= 1/20:
                self.clock = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.image = pygame.transform.scale(self.image, (180, 180))

                angle = math.degrees(math.atan2(-self.dx, self.dy))
                self.image = pygame.transform.rotate(self.image, -angle)

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('images/enemies/boss', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)

        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def Boss_HP_bar(self, screen):
        info = pygame.display.Info()
        HP_bar = pygame.Surface((250, 30))
        HP_bar.fill("Blue")

        non_hp_bar = self.max_HP - self.HP
        k = self.max_HP // 250
        pygame.draw.rect(HP_bar, (0, 0, 0), ((self.HP // k, 0), (non_hp_bar // k + 10, 30)))

        font = pygame.font.Font(None, 30)
        text = font.render(f"{str(self.HP)} / {self.max_HP}", 1, (255, 255, 255))
        HP_bar.blit(text, (70, 5))

        screen.blit(HP_bar, (info.current_w / 2 + 420, 10))
