# main.py
import sys
import pygame as pg

from settings import *
from map import Map
from player import Player
from raycasting import RayCasting
from object_render import ObjectRenderer
from object_handler import ObjectHandler
from weapon import Weapon
from sound import Sound
from pathfinding import PathFinding

# optional: helper for nicer error messages
try:
    from utils.resource_path import resource_path
    import os
except Exception:
    resource_path = None
    os = None


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        # Initialize game subsystems with guarded startup
        try:
            self.new_game()
        except Exception as e:
            print("Failed to initialize game subsystems.")
            print("Error:", type(e).__name__, e)
            if resource_path:
                print("Looking for resources at:", resource_path('resources'))
                print("resources exists?:", os.path.isdir(resource_path('resources')))
            print("Exiting.")
            pg.quit()
            sys.exit(1)

    def new_game(self):
        # Create lightweight parts first
        self.map = Map(self)
        self.player = Player(self)

        # ObjectRenderer loads textures — create early so we fail-fast on missing assets
        try:
            self.object_renderer = ObjectRenderer(self)
        except Exception as e:
            # re-raise with a clearer message so outer try/except can show path
            print("Error while creating ObjectRenderer (likely missing texture files).")
            raise

        # Raycasting depends on object_renderer.wall_textures
        self.raycasting = RayCasting(self)

        # Remaining systems
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)

        # Play music if loaded (some environments may disable audio)
        try:
            pg.mixer.music.play(-1)
        except Exception:
            pass

    def update(self):
        # core update order
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()

        pg.display.flip()
        # avoid zero delta_time; keep it in ms
        self.delta_time = max(1, self.clock.tick(FPS))
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        # object_renderer handles background + sprites; weapon drawn on top
        self.object_renderer.draw()
        self.weapon.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
