# npc.py
import math
import pygame as pg
from random import randint, random
from sprite_object import AnimatedSprite
from utils.resource_path import resource_path
from settings import HALF_WIDTH, MAX_DEPTH


class NPC(AnimatedSprite):
    def __init__(self, game, path=None, pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180,
                 sprite_folder='soldier'):
        """
        sprite_folder: the folder name under resources/sprites/npc/ to load animations from.
                       e.g. 'soldier', 'cyber_demon', 'caco_demon'
        """
        self.game = game
        self.sprite_folder = sprite_folder

        # default sprite path (walk frame from the chosen folder)
        if path is None:
            path = resource_path('resources', 'sprites', 'npc', self.sprite_folder, 'walk', 'walk1.png')

        # initialize AnimatedSprite (base)
        super().__init__(game, path, pos, scale, shift, animation_time)

        # load animation frames from the chosen sprite folder
        base = ['resources', 'sprites', 'npc', self.sprite_folder]
        self.attack_images = self.get_images(resource_path(*base, 'attack'))
        self.death_images = self.get_images(resource_path(*base, 'death'))
        self.idle_images = self.get_images(resource_path(*base, 'idle'))
        self.pain_images = self.get_images(resource_path(*base, 'pain'))
        self.walk_images = self.get_images(resource_path(*base, 'walk'))

        # default stats (can be overridden by subclasses)
        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            try:
                self.game.sound.npc_shot.play()
            except pg.error:
                pass
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                try:
                    self.game.sound.npc_pain.play()
                except pg.error:
                    pass
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            try:
                self.game.sound.npc_death.play()
            except pg.error:
                pass

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()

            elif self.ray_cast_value:
                self.player_search_trigger = True

                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()

            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
                         (100 * self.x, 100 * self.y), 2)


class SoldierNPC(NPC):
    def __init__(self, game, path=None, pos=(10.5, 5.5),
                 scale=0.5, shift=0.38, animation_time=160):
        # tell base to load 'soldier' sprite set
        super().__init__(game, path, pos, scale, shift, animation_time, sprite_folder='soldier')

        # small and low damage
        self.attack_dist = 4
        self.speed = 0.035
        self.size = 18
        self.health = 90
        self.attack_damage = 8
        self.accuracy = 0.12


class CyberDemonNPC(NPC):
    def __init__(self, game, path=None, pos=(11.5, 6.0),
                 scale=0.85, shift=0.04, animation_time=210):
        # tell base to load 'cyber_demon' sprite set
        super().__init__(game, path, pos, scale, shift, animation_time, sprite_folder='cyber_demon')

        # medium size and medium damage
        self.attack_dist = 6
        self.speed = 0.045
        self.size = 26
        self.health = 250
        self.attack_damage = 14
        self.accuracy = 0.22


class CacoDemonNPC(NPC):
    def __init__(self, game, path=None, pos=(10.5, 6.5),
                 scale=1.05, shift=0.27, animation_time=200):
        # tell base to load 'caco_demon' sprite set
        super().__init__(game, path, pos, scale, shift, animation_time, sprite_folder='caco_demon')

        # big and fast but lower health (dies easier)
        self.attack_dist = 1.5
        self.speed = 0.065
        self.size = 36
        self.health = 120
        self.attack_damage = 20
        self.accuracy = 0.18
