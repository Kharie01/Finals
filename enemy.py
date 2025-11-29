import pygame
from os.path import join

# Initialize Pygame
pygame.init()

# Must set display mode first for convert_alpha()
pygame.display.set_mode((1, 1))  # minimal hidden window just for image loading

# -----------------------------
# Load enemy images manually
# -----------------------------
# Each direction has 2 frames (can be same image if you don't have multiple frames yet)
GRUNT_UP    = [pygame.image.load(join("assets", "images", "enemies", "grunt.png")).convert_alpha()] * 2
GRUNT_DOWN  = [pygame.image.load(join("assets", "images", "enemies", "grunt.png")).convert_alpha()] * 2
GRUNT_LEFT  = [pygame.image.load(join("assets", "images", "enemies", "grunt.png")).convert_alpha()] * 2
GRUNT_RIGHT = [pygame.image.load(join("assets", "images", "enemies", "grunt.png")).convert_alpha()] * 2

FAST_UP     = [pygame.image.load(join("assets", "images", "enemies", "fast.png")).convert_alpha()] * 2
FAST_DOWN   = [pygame.image.load(join("assets", "images", "enemies", "fast.png")).convert_alpha()] * 2
FAST_LEFT   = [pygame.image.load(join("assets", "images", "enemies", "fast.png")).convert_alpha()] * 2
FAST_RIGHT  = [pygame.image.load(join("assets", "images", "enemies", "fast.png")).convert_alpha()] * 2

TANK_UP     = [pygame.image.load(join("assets", "images", "enemies", "tank.png")).convert_alpha()] * 2
TANK_DOWN   = [pygame.image.load(join("assets", "images", "enemies", "tank.png")).convert_alpha()] * 2
TANK_LEFT   = [pygame.image.load(join("assets", "images", "enemies", "tank.png")).convert_alpha()] * 2
TANK_RIGHT  = [pygame.image.load(join("assets", "images", "enemies", "tank.png")).convert_alpha()] * 2

FLYING_UP     = [pygame.image.load(join("assets", "images", "enemies", "flying.png")).convert_alpha()] * 2
FLYING_DOWN   = [pygame.image.load(join("assets", "images", "enemies", "flying.png")).convert_alpha()] * 2
FLYING_LEFT   = [pygame.image.load(join("assets", "images", "enemies", "flying.png")).convert_alpha()] * 2
FLYING_RIGHT  = [pygame.image.load(join("assets", "images", "enemies", "flying.png")).convert_alpha()] * 2

SWARM_UP     = [pygame.image.load(join("assets", "images", "enemies", "swarm.png")).convert_alpha()] * 2
SWARM_DOWN   = [pygame.image.load(join("assets", "images", "enemies", "swarm.png")).convert_alpha()] * 2
SWARM_LEFT   = [pygame.image.load(join("assets", "images", "enemies", "swarm.png")).convert_alpha()] * 2
SWARM_RIGHT  = [pygame.image.load(join("assets", "images", "enemies", "swarm.png")).convert_alpha()] * 2

# -----------------------------
# ENEMY TYPES with placeholder animations
# -----------------------------
ENEMY_TYPES = {
    "grunt": {
        "speed": 1.67,
        "hp": 60,
        "damage": 10,
        "flying": False,
        "anim": {
            "up": GRUNT_UP,
            "down": GRUNT_DOWN,
            "left": GRUNT_LEFT,
            "right": GRUNT_RIGHT
        }
    },
    "fast": {
        "speed": 3.00,
        "hp": 40,
        "damage": 5,
        "flying": False,
        "anim": {
            "up": FAST_UP,
            "down": FAST_DOWN,
            "left": FAST_LEFT,
            "right": FAST_RIGHT
        }
    },
    "tank": {
        "speed": 1.00,
        "hp": 250,
        "damage": 20,
        "flying": False,
        "anim": {
            "up": TANK_UP,
            "down": TANK_DOWN,
            "left": TANK_LEFT,
            "right": TANK_RIGHT
        }
    },
    "flying": {
        "speed": 2.43,
        "hp": 45,
        "damage": 8,
        "flying": True,
        "anim": {
            "up": FLYING_UP,
            "down": FLYING_DOWN,
            "left": FLYING_LEFT,
            "right": FLYING_RIGHT
        }
    },
    "swarm": {
        "speed": 1.95,
        "hp": 20,
        "damage": 3,
        "flying": False,
        "anim": {
            "up": SWARM_UP,
            "down": SWARM_DOWN,
            "left": SWARM_LEFT,
            "right": SWARM_RIGHT
        }
    },
}

