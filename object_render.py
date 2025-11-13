# object_render.py
import pygame as pg
from settings import *
from utils.resource_path import resource_path


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture(resource_path('resources', 'textures', 'sky.png'), (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture(resource_path('resources', 'textures', 'blood_screen.png'), RES)
        self.digit_size = 90
        # digits 0..10 (adjust if your project only has 0..9)
        self.digit_images = [self.get_texture(resource_path('resources', 'textures', 'digits', f'{i}.png'),
                                             (self.digit_size, self.digit_size))
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture(resource_path('resources', 'textures', 'gameover.jpg'), RES)
        self.win_image = self.get_texture(resource_path('resources', 'textures', 'win.png'), RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        # optional extra digit slot
        self.screen.blit(self.digits.get('10', self.digit_images[0]), ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        """
        Draw sky with horizontal parallax and small vertical pitch shift.
        pitch_factor determines how many pixels full pitch (1.0) moves the camera.
        """
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH

        # tuned to avoid collapsing layout
        pitch_factor = 80
        pitch_px = int(self.game.player.pitch * pitch_factor)

        # draw sky images horizontally tiled; vertical shift is -pitch_px so positive pitch moves sky down visually
        self.screen.blit(self.sky_image, (-self.sky_offset, -pitch_px))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, -pitch_px))

        # compute horizon (y pixel) and draw floor from horizon to bottom
        horizon_y = HALF_HEIGHT + pitch_px
        # clamp horizon inside screen sensible bounds
        horizon_y = max(-HEIGHT, min(HEIGHT * 2, horizon_y))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, horizon_y, WIDTH, HEIGHT - horizon_y))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture(resource_path('resources', 'textures', '1.png')),
            2: self.get_texture(resource_path('resources', 'textures', '2.png')),
            3: self.get_texture(resource_path('resources', 'textures', '3.png')),
            4: self.get_texture(resource_path('resources', 'textures', '4.png')),
            5: self.get_texture(resource_path('resources', 'textures', '5.png')),
        }
