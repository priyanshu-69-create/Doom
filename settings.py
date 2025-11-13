# settings.py
import math

# ------------------- GAME WINDOW SETTINGS -------------------
RES = WIDTH, HEIGHT = 1600, 900
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

# Frame rate
FPS = 60

# ------------------- PLAYER SETTINGS -------------------
PLAYER_POS = (1.5, 5)              # Player start position on map
PLAYER_ANGLE = 0                   # Initial viewing angle
PLAYER_SPEED = 0.004               # Movement speed
PLAYER_ROT_SPEED = 0.002           # Rotation speed
PLAYER_SIZE_SCALE = 60             # Used for collision box size
PLAYER_MAX_HEALTH = 300            # Player total health
PLAYER_DAMAGE_RESISTANCE = 0.20    # Player resists 20% of incoming damage

# ------------------- MOUSE SETTINGS -------------------
MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - 100

# ------------------- FIELD OF VIEW & RAYCASTING -------------------
FOV = math.pi / 3                     # Field of view (60 degrees)
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20                        # Maximum visible raycasting distance

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# ------------------- COLORS -------------------
FLOOR_COLOR = (30, 30, 30)
SKY_COLOR = (0, 0, 0)

# ------------------- TEXTURES -------------------
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# ------------------- SOUND / MUSIC SETTINGS -------------------
SOUND_VOLUME = 0.3

# ------------------- DEBUG -------------------
DEBUG_MODE = False
