from settings import *

ENEMY_TYPES = {
    "grunt":  {"size": (48, 48), "anim": None, "speed": 0.8, "hp": 60, "damage": 10, "flying": False},
    "fast":   {"size": (40, 40), "anim": None, "speed": 1.2, "hp": 40, "damage": 5,  "flying": False},
    "tank":   {"size": (75, 75), "anim": None, "speed": 0.6, "hp": 500,"damage": 35, "flying": False}, #75 max size for tank, will not register if more
    "flying": {"size": (60, 60), "anim": None, "speed": 1.0, "hp": 45, "damage": 10, "flying": True},
    "swarm":  {"size": (32, 32), "anim": None, "speed": 1.3, "hp": 5,  "damage": 5,  "flying": False},
}

def load_animation(path, size=None):
    frames = []
    for i in range(10):
        file = join(path, f"frame_{i}.png")
        if not os.path.exists(file):
            break
        img = pygame.image.load(file).convert_alpha()

        if size:
            img = pygame.transform.smoothscale(img, size)

        frames.append(img)

    return frames

# -----------------------------
# Load enemy images manually
# -----------------------------
def anim_folder(enemy, direction):
    return resource_path(f"assets/images/enemies/{enemy}/{direction}")

# -----------------------------
# ENEMY TYPES with placeholder animations
# -----------------------------
def load_enemy_animations():
    animations = {}

    for name, data in ENEMY_TYPES.items():
        size = data["size"]

        animations[name] = {
            "up":    load_animation(anim_folder(name, "up"), size),
            "down":  load_animation(anim_folder(name, "down"), size),
            "left":  load_animation(anim_folder(name, "left"), size),
            "right": load_animation(anim_folder(name, "right"), size),
        }

    return animations
