import pygame
from map import Map
from characters.Kiana.kiana import Kiana
from characters.Kiana.skillset import KianaBaseAttack, KianaSkillE
from characters.Mei.mei import Mei
from characters.Mei.skillset import MeiBaseAttack, MeiSkillE
from enemies.spider import Spider
from enemies.witch import Witch
from enemies.boss import Boss
from events.events import Events
from interface.interface import Interface
import random
import time


def character_choice(group, fps):
    name = input("Выберите персонажа. (Mei, Kiana): ")
    while True:
        if name == "Mei":
            return Mei(group, fps=fps), name
        elif name == "Kiana":
            return Kiana(group, fps=fps), name
        else:
            name = input("Такого персонажа не существует. Выберите одного из предложенных. (Mei, Kiana): ")


def phases(all_events: Events, camera_pos, current_time, borders, spiders, witches, bosses):
    if current_time <= 60:
        if len(spiders) < 50:
            spawn_chance = random.randint(1, 1000)
            if spawn_chance > 990:
                all_events.spawn_enemies(
                    enemy=Spider, max_enemies=1,
                    camera_pos=camera_pos, available_range=(borders[:2], borders[2:]))

    if 60 < current_time <= 120:
        if len(spiders) < 100:
            spawn_chance = random.randint(1, 1000)
            if spawn_chance > 980:
                all_events.spawn_enemies(
                    enemy=Spider, max_enemies=2,
                    camera_pos=camera_pos, available_range=(borders[:2], borders[2:]))

    if 120 < current_time <= 180:
        if len(spiders) < 60:
            spawn_chance = random.randint(1, 1000)
            if spawn_chance > 675:
                all_events.spawn_enemies(
                    enemy=Spider, max_enemies=5,
                    camera_pos=camera_pos, available_range=(borders[:2], borders[2:]))

    if 180 < current_time <= 240:
        if len(witches) < 30:
            spawn_chance = random.randint(1, 1000)
            if spawn_chance > 990:
                all_events.spawn_enemies(
                    enemy=Witch, max_enemies=2,
                    camera_pos=camera_pos, available_range=(borders[:2], borders[2:]))

    if 240 < current_time <= 300:
        if len(bosses) < 1:
            spawn_chance = random.randint(1, 1000)
            if spawn_chance > 990:
                all_events.spawn_enemies(
                    enemy=Boss, max_enemies=1,
                    camera_pos=camera_pos, available_range=(borders[:2], borders[2:]))



def main():
    pygame.init()
    # pygame.mixer.init()
    # pygame.mixer.music.load('Audio/background_music_2.mp3')
    # pygame.mixer.music.set_volume(1)
    # pygame.mixer.music.play(-1)

    size = 1400, 800
    fps = 100

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("honkai impact 4th")

    character_sprites = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    visible_enemies = pygame.sprite.Group()
    spider_sprites = pygame.sprite.Group()
    witch_sprites = pygame.sprite.Group()
    boss_sprites = pygame.sprite.Group()
    skill_sprites = pygame.sprite.Group()

    # character, character_name = character_choice(group=character_sprites, fps=fps)
    character, character_name = Mei(character_sprites, fps=fps), "Mei"

    main_map = Map(fps, character)
    main_map_data = main_map.map_data
    main_map_flightless_data = main_map.flightless_map
    tile_size = main_map.TILE_SIZE
    right_border = 6 * tile_size + tile_size // 2
    left_border = (len(main_map_data[0]) - 7) * tile_size - tile_size // 2
    upper_border = 3 * tile_size + tile_size // 2
    lower_border = (len(main_map_data) - 4) * tile_size - tile_size // 2
    interface = Interface(character)

    events = Events(fps=fps, flightless_data=main_map_flightless_data, player=character,
                    spider_sprites=spider_sprites, witch_sprites=witch_sprites, boss_sprites=boss_sprites)

    clock = pygame.time.Clock()
    skill_clock = 0
    skill = True
    seconds_to_shoot = 0
    fire = False
    mei_skill_duration = False
    mei_skill_time = 0
    running = True
    while running:
        player_pos = (main_map.player_x, main_map.player_y)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                fire = True
            if event.type == pygame.MOUSEBUTTONUP:
                fire = False
                seconds_to_shoot = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and skill:
                    if character_name == "Kiana":
                        KianaSkillE(skill_sprites, fps=fps, player=character)
                    elif character_name == "Mei":
                        character.HP -= 5
                        character.base_atk_damage += 15
                        mei_skill = MeiSkillE(player=character, map=main_map, enemy=visible_enemies)
                        mei_skill_duration = True
                    interface.skill_start = True
                    skill = False
                    skill_clock = time.time()

        if fire:
            if character_name == "Kiana":
                if seconds_to_shoot == fps // 10:
                    seconds_to_shoot = 0
                    x, y = size[0] // 2, size[1] // 2
                    KianaBaseAttack(bullet_sprites, x=x, y=y, fps=fps, map_data=main_map_data, player_pos=player_pos,
                                    player=character)
                else:
                    seconds_to_shoot += 1

            elif character_name == "Mei":
                if seconds_to_shoot == 50:
                    seconds_to_shoot = 0
                    MeiBaseAttack(bullet_sprites, fps=fps, player=character)
                else:
                    seconds_to_shoot += 1

        if time.time() - skill_clock >= character.skill_recharge and not skill:
            character.base_atk_damage -= 15
            skill = True

        if mei_skill_duration:
            if mei_skill_time == 20:
                mei_skill_duration = False
                mei_skill_time = 0
            else:
                mei_skill.dash()
                mei_skill_time += 1


        screen.fill(0)
        main_map.update(screen)
        all_change = main_map.change
        camera_pos = (main_map.player_x - size[0] // 2, main_map.player_y - size[1] // 2)
        visible_enemies = pygame.sprite.Group()

        interface.timer(screen)

        phases(all_events=events, camera_pos=camera_pos, current_time=interface.current_time,
               borders=(right_border, left_border, upper_border, lower_border),
               spiders=spider_sprites, witches=witch_sprites, bosses=boss_sprites)

        spider_sprites.update(change=all_change, camera_pos=camera_pos, visible_sprites=visible_enemies)
        witch_sprites.update(change=all_change, player=character, visible_sprites=visible_enemies)
        boss_sprites.update(change=all_change, player=character, visible_sprites=visible_enemies)
        visible_enemies.draw(screen)

        character_sprites.update(visible_sprites=visible_enemies)
        character_sprites.draw(screen)

        bullet_sprites.update(change=all_change, camera_pos=camera_pos, enemies_group=visible_enemies)
        bullet_sprites.draw(screen)

        skill_sprites.update(enemies_group=visible_enemies)
        skill_sprites.draw(screen)

        interface.draw_interface(screen)

        pygame.display.flip()
        clock.tick(fps)

        if character.HP <= 0:
            print("Вас убили!")
            running = False

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
