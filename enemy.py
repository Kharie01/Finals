import pygame
from os.path import join

# Initialize Pygame
pygame.init()

# Must set display mode first for convert_alpha()
pygame.display.set_mode((1, 1)) # minimal hidden window just for image loading


def load_animation(path, size=None):
    frames = []
    for i in range(10):  # supports frame_0.png to frame_9.png
        file = join(path, f"frame_{i}.png")
        try:
            img = pygame.image.load(file).convert_alpha()

            # SCALE IF NEEDED
            if size:
                img = pygame.transform.smoothscale(img, size)

            frames.append(img)
        except:
            break
    return frames if frames else [pygame.Surface((1,1))]  # fallback
# -----------------------------
# Load enemy images manually
# -----------------------------
def anim_folder(enemy, direction):
    return join("assets", "images", "enemies", enemy, direction)

# Load animations
GRUNT_UP    = load_animation(anim_folder("grunt", "up"))
GRUNT_DOWN  = load_animation(anim_folder("grunt", "down"))
GRUNT_LEFT  = load_animation(anim_folder("grunt", "left"))
GRUNT_RIGHT = load_animation(anim_folder("grunt", "right"))

FAST_UP     = load_animation(anim_folder("fast", "up"))
FAST_DOWN   = load_animation(anim_folder("fast", "down"))
FAST_LEFT   = load_animation(anim_folder("fast", "left"))
FAST_RIGHT  = load_animation(anim_folder("fast", "right"))

TANK_UP     = load_animation(anim_folder("tank", "up"))
TANK_DOWN   = load_animation(anim_folder("tank", "down"))
TANK_LEFT   = load_animation(anim_folder("tank", "left"))
TANK_RIGHT  = load_animation(anim_folder("tank", "right"))

FLYING_UP     = load_animation(anim_folder("flying", "up"))
FLYING_DOWN   = load_animation(anim_folder("flying", "down"))
FLYING_LEFT   = load_animation(anim_folder("flying", "left"))
FLYING_RIGHT  = load_animation(anim_folder("flying", "right"))

SWARM_UP     = load_animation(anim_folder("swarm", "up"))
SWARM_DOWN   = load_animation(anim_folder("swarm", "down"))
SWARM_LEFT   = load_animation(anim_folder("swarm", "left"))
SWARM_RIGHT  = load_animation(anim_folder("swarm", "right"))

# -----------------------------
# ENEMY TYPES with placeholder animations
# -----------------------------
ENEMY_TYPES = {
    "grunt": {
        "speed": 1.67,
        "hp": 60,
        "damage": 10,
        "flying": False,
        "size": (48, 48),   # ⬅ custom resize
        "anim": None        # will be auto-filled below
    },
    "fast": {
        "speed": 3.00,
        "hp": 40,
        "damage": 5,
        "flying": False,
        "size": (40, 40),
        "anim": None
    },
    "tank": {
        "speed": 1.00,
        "hp": 300,
        "damage": 30,
        "flying": False,
        "size": (90, 90),
        "anim": None
    },
    "flying": {
        "speed": 2.43,
        "hp": 45,
        "damage": 8,
        "flying": True,
        "size": (60, 60),
        "anim": None
    },
    "swarm": {
        "speed": 1.95,
        "hp": 20,
        "damage": 3,
        "flying": False,
        "size": (32, 32),
        "anim": None
    },
}

# Load enemy animations based on each enemy's size
for enemy_name, data in ENEMY_TYPES.items():
    size = data.get("size", None)

    data["anim"] = {
        "up":    load_animation(anim_folder(enemy_name, "up"), size=size),
        "down":  load_animation(anim_folder(enemy_name, "down"), size=size),
        "left":  load_animation(anim_folder(enemy_name, "left"), size=size),
        "right": load_animation(anim_folder(enemy_name, "right"), size=size)
    }

