# sound.py
import pygame as pg
from utils.resource_path import resource_path

class Sound:
    def __init__(self, game):
        self.game = game
        pg.mixer.init()
        self.shotgun = pg.mixer.Sound(resource_path('resources', 'sounds', 'shotgun.wav'))
        self.npc_pain = pg.mixer.Sound(resource_path('resources', 'sounds', 'npc_pain.wav'))
        self.npc_death = pg.mixer.Sound(resource_path('resources', 'sounds', 'npc_death.wav'))
        self.npc_shot = pg.mixer.Sound(resource_path('resources', 'sounds', 'npc_attack.wav'))
        self.npc_shot.set_volume(0.2)
        self.player_pain = pg.mixer.Sound(resource_path('resources', 'sounds', 'player_pain.wav'))
        pg.mixer.music.load(resource_path('resources', 'sounds', 'doom_theme.wav'))
        pg.mixer.music.set_volume(0.3)
