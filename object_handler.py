# object_handler.py
from sprite_object import *
from npc import *
from random import choices, randrange
from utils.resource_path import resource_path
import pygame as pg
import sys

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        # resource base folders (kept for reference; use resource_path when needed)
        self.npc_sprite_path = resource_path('resources', 'sprites', 'npc')
        self.static_sprite_path = resource_path('resources', 'sprites', 'static_sprites')
        self.anim_sprite_path = resource_path('resources', 'sprites', 'animated_sprites')

        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        # spawn settings
        self.enemies = 20  # npc count
        # ensure order: Soldier, Caco, Cyber
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        # weights: higher -> more frequent
        self.weights = [70, 20, 10]

        # small region where we don't spawn (player start area)
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}

        # spawn NPCs
        self.spawn_npc()

        # sprite map examples (kept mostly as-is, but use resource_path for any explicit paths)
        add_sprite(AnimatedSprite(game))
        add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        # animated lights using proper resource_path
        add_sprite(AnimatedSprite(game, path=resource_path('resources','sprites','animated_sprites','red_light','red.png'), pos=(14.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=resource_path('resources','sprites','animated_sprites','red_light','red_2.png'), pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=resource_path('resources','sprites','animated_sprites','red_light','red_3.png'), pos=(12.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=resource_path('resources','sprites','animated_sprites','red_light','red_4.png'), pos=(9.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 12.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

    def spawn_npc(self):
        """Spawn `self.enemies` NPCs using weighted random choices.
           Logs all spawns and prints summary.
        """
        spawned = []
        for i in range(self.enemies):
            try:
                npc_cls = choices(self.npc_types, weights=self.weights, k=1)[0]
                # pick random free cell
                x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                # avoid walls and restricted area
                attempt = 0
                while ((x, y) in self.game.map.world_map) or ((x, y) in self.restricted_area):
                    x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                    attempt += 1
                    if attempt > 200:  # fallback to safe cell near player if map is dense
                        x, y = int(self.game.player.x) + 2, int(self.game.player.y) + 2
                        break
                npc_obj = npc_cls(self.game, pos=(x + 0.5, y + 0.5))
                self.add_npc(npc_obj)
                spawned.append(type(npc_obj).__name__)
                # small debug print for each NPC
                print(f"[SPAWN] {type(npc_obj).__name__} at {(x, y)}")
            except Exception as e:
                # if an NPC fails to spawn (e.g. resource load error), report and continue
                print(f"[SPAWN ERROR] failed to spawn npc: {e}", file=sys.stderr)
                continue

        # summary counts
        from collections import Counter
        counts = Counter(spawned)
        print("[SPAWN SUMMARY] ", dict(counts))

    def force_spawn(self, type_name, pos):
        """Force spawn an NPC by class name for testing.
           type_name: 'SoldierNPC' | 'CacoDemonNPC' | 'CyberDemonNPC'
           pos: tuple (x,y) in map grid coords (ints)
        """
        cls_map = {c.__name__: c for c in self.npc_types}
        if type_name not in cls_map:
            print("[force_spawn] Unknown type:", type_name)
            return None
        cls = cls_map[type_name]
        x, y = pos
        npc_obj = cls(self.game, pos=(x + 0.5, y + 0.5))
        self.add_npc(npc_obj)
        print(f"[FORCE SPAWN] {type_name} at {pos}")
        return npc_obj

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
