from settings import *
from enemy import ENEMY_TYPES
import time

class Monster(pygame.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, group, money_system=None):
        super().__init__(group)

        data = ENEMY_TYPES[enemy_type]

        # Stats
        self.speed = data["speed"]
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.damage = data["damage"]
        self.flying = data["flying"]

        # Get already-SCALED animations
        self.anim = data["anim"]

        self.anim_dir = "down"
        self.frame = 0
        self.frame_speed = 0.15

        # Waypoints
        self.waypoints = waypoints
        self.pos = pygame.Vector2(waypoints[0])
        self.target_waypoint = 1

        self.image = self.anim["down"][0]
        self.rect = self.image.get_rect(center=self.pos)

        # Effects
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.15

        self.original_image = self.image.copy()

        self.money_system = money_system

    # -----------------------------
    # MOVEMENT + ANIMATION DIRECTION
    # -----------------------------
    def move(self):
        if self.target_waypoint >= len(self.waypoints):
            return

        target = pygame.Vector2(self.waypoints[self.target_waypoint])
        travel = target - self.pos
        dist = travel.length()

        # Decide animation direction based on travel vector
        if abs(travel.x) > abs(travel.y):
            self.anim_dir = "right" if travel.x > 0 else "left"
        else:
            self.anim_dir = "down" if travel.y > 0 else "up"

        # Move toward waypoint
        if dist > 0:
            self.pos += travel.normalize() * min(dist, self.speed)
        else:
            self.pos = target
            self.target_waypoint += 1

        self.rect.center = self.pos

    # -----------------------------
    # WALKING ANIMATION + HIT FLASH
    # -----------------------------
    def animate(self):
        frames = self.anim[self.anim_dir]

        # Frame stepping
        self.frame += self.frame_speed
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

        # Hit flash overlay
        if self.is_hit:
            flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 120))
            temp = self.image.copy()
            temp.blit(flash, (0, 0))
            self.image = temp

        # Keep rect centered on new frame size
        self.rect = self.image.get_rect(center=self.pos)

    # -----------------------------
    # DAMAGE & DEATH
    # -----------------------------
    def take_damage(self, amt):
        self.hp -= amt
        if self.hp <= 0:
            self.die()
            return

        self.is_hit = True
        self.hit_timer = time.time()

    def die(self):
        if self.money_system:
            self.money_system.on_enemy_killed()
        self.kill()

    # -----------------------------
    # HP BAR
    # -----------------------------
    def draw_hp(self, surf):
        w, h = 28, 5
        x = self.rect.centerx - w // 2
        y = self.rect.top - 8

        pygame.draw.rect(surf, (255, 0, 0), (x, y, w, h))
        pygame.draw.rect(surf, (0, 255, 0), (x, y, int(w * self.hp / self.max_hp), h))
        pygame.draw.rect(surf, (0, 0, 0), (x, y, w, h), 1)

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(self, dt=None):
        # remove hit effect
        if self.is_hit and (time.time() - self.hit_timer) >= self.hit_duration:
            self.is_hit = False

        self.move()
        self.animate()
