# sprite_object.py
import os
import math
import pygame as pg
from collections import deque
from utils.resource_path import resource_path
from settings import *
from typing import Deque


class SpriteObject:
    def __init__(self, game, path=None,
                 pos=(10.5, 3.5), scale=0.7, shift=0.27):
        self.game = game
        self.player = game.player
        self.x, self.y = pos

        # default sprite file (static sprite fallback)
        if path is None:
            path = resource_path('resources', 'sprites', 'static_sprites', 'candlebra.png')

        # If user passed a directory, pick the first image file inside
        if os.path.isdir(path):
            files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            # find first image-like file
            img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not img_files:
                raise FileNotFoundError(f"No image files found in directory: {path}")
            path = os.path.join(path, img_files[0])

        # load image
        try:
            self.image = pg.image.load(path).convert_alpha()
        except Exception as e:
            raise FileNotFoundError(f"Failed to load sprite image '{path}': {e}")

        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 0, 0, 1, 1
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        image = pg.transform.scale(self.image, (int(proj_width), int(proj_height)))

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = (self.screen_x - self.sprite_half_width, HALF_HEIGHT - proj_height // 2 + height_shift)

        # append depth-sorted object (norm_dist used to sort later)
        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle
        # normalize to -pi..pi
        if delta > math.pi:
            delta -= math.tau
        if delta < -math.pi:
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        self.dist = math.hypot(dx, dy)
        # distance corrected for fisheye
        self.norm_dist = self.dist * math.cos(delta)
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()


class AnimatedSprite(SpriteObject):
    def __init__(self, game, path=None,
                 pos=(11.5, 3.5), scale=0.8, shift=0.16, animation_time=120):
        # default to a folder of animated sprites
        if path is None:
            path = resource_path('resources', 'sprites', 'animated_sprites', 'green_light')

        # If path is a directory, pick the first file inside to be the base image
        if os.path.isdir(path):
            files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not img_files:
                raise FileNotFoundError(f"No image files found in directory: {path}")
            first_image = os.path.join(path, img_files[0])
            super().__init__(game, path=first_image, pos=pos, scale=scale, shift=shift)
            self.path = path
        else:
            # path is a file: load that file as base image and determine directory for frames
            super().__init__(game, path=path, pos=pos, scale=scale, shift=shift)
            self.path = os.path.dirname(path)

        self.animation_time = animation_time
        self.images: Deque[pg.Surface] = self.get_images(self.path)
        # if images deque is empty, try to ensure there is at least one frame (self.image is already set)
        if not self.images:
            # put the loaded base image as a single-frame animation
            dq = deque()
            dq.append(self.image)
            self.images = dq
            print(f"[AnimatedSprite] No frames found in '{self.path}', using base image as single frame.")

        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False
        # store image also for scaling in weapons etc.
        self.image = self.images[0]

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animation_trigger and images:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        """
        Load images from `path` (a directory). Returns a deque of pygame Surfaces.
        Robust behaviors:
          - If `path` is not a dir -> returns empty deque.
          - If `path` is empty, tries common subfolders like 'walk', 'idle', 'attack'.
          - If still empty, tries to fall back to soldier walk frames.
          - Prints helpful debug lines so you can see what was found.
        """
        images = deque()

        # quick guard
        if not os.path.isdir(path):
            # not a directory (caller may have passed a file); return empty deque
            return images

        # collect valid image files (sorted for deterministic order)
        try:
            files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        except Exception as e:
            print(f"[get_images] Failed to list directory '{path}': {e}")
            return images

        if files:
            for file_name in files:
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path):
                    try:
                        img = pg.image.load(file_path).convert_alpha()
                        images.append(img)
                    except Exception as e:
                        print(f"[get_images] failed to load image {file_path}: {e}")
            if images:
                print(f"[get_images] Loaded {len(images)} frames from: {path}")
                return images

        # If nothing loaded, try common subfolders (walk, idle, attack, pain, death)
        common_subs = ['walk', 'idle', 'attack', 'pain', 'death', 'anim']
        for sub in common_subs:
            subpath = os.path.join(path, sub)
            if os.path.isdir(subpath):
                try:
                    subfiles = sorted([f for f in os.listdir(subpath) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                except Exception:
                    subfiles = []
                if subfiles:
                    for file_name in subfiles:
                        file_path = os.path.join(subpath, file_name)
                        try:
                            img = pg.image.load(file_path).convert_alpha()
                            images.append(img)
                        except Exception as e:
                            print(f"[get_images] failed to load image {file_path}: {e}")
                    if images:
                        print(f"[get_images] Loaded {len(images)} frames from subfolder: {subpath}")
                        return images

        # Fallback: try soldier walk frames (common fallback in this project)
        try:
            soldier_walk = resource_path('resources', 'sprites', 'npc', 'soldier', 'walk')
            if os.path.isdir(soldier_walk):
                fallback_files = sorted([f for f in os.listdir(soldier_walk) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                for file_name in fallback_files:
                    file_path = os.path.join(soldier_walk, file_name)
                    try:
                        img = pg.image.load(file_path).convert_alpha()
                        images.append(img)
                    except Exception:
                        continue
                if images:
                    print(f"[get_images] WARNING: '{path}' had no frames, used soldier fallback ({len(images)} frames).")
                    return images
        except Exception:
            pass

        # final: nothing found
        print(f"[get_images] WARNING: no image frames found for path: {path}")
        return images
