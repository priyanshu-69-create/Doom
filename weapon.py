# weapon.py
from sprite_object import *
from collections import deque
from utils.resource_path import resource_path
import pygame as pg


class Weapon(AnimatedSprite):
    def __init__(self, game, path=None, scale=0.4, animation_time=90):
        # default weapons folder or file
        if path is None:
            path = resource_path('resources', 'sprites', 'weapons')

        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)

        # scale each frame to weapon scale (use int sizes)
        self.images = deque(
            [pg.transform.smoothscale(img,
                                      (int(img.get_width() * scale), int(img.get_height() * scale)))
             for img in self.images]
        )

        if not self.images:
            # fallback to the currently loaded image as single frame
            self.images = deque([pg.transform.smoothscale(self.image,
                                                         (int(self.image.get_width() * scale),
                                                          int(self.image.get_height() * scale)))])

        # initial weapon position (centered horizontally, bottom vertically)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2,
                           HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        # Use the same pitch_factor as object_render for consistent movement
        pitch_factor = 80
        pitch_px = int(self.game.player.pitch * pitch_factor)
        # When player looks up (pitch positive), weapon should move up: subtract pitch_px
        pos = (self.weapon_pos[0], self.weapon_pos[1] - pitch_px)
        self.game.screen.blit(self.images[0], pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()
