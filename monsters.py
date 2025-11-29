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
        self.damage = data.get("damage", 10)
        self.flying = data.get("flying", False)

        # Animation
        self.anim = data["anim"]
        self.anim_dir = "down"
        self.frame = 0
        self.frame_speed = 0.12

        # Waypoints & position
        self.waypoints = waypoints
        self.pos = pygame.Vector2(waypoints[0])
        self.target_waypoint = 1

        # Starting image
        self.image = self.anim["down"][0]
        self.rect = self.image.get_rect(center=self.pos)

        # Hit effect
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.15

        # Store original image for flashing
        self.original_image = self.image.copy()

        # Reference to money system
        self.money_system = money_system

    # Movement
    def move(self):
        if self.target_waypoint >= len(self.waypoints):
            return  # Reached the end

        target = pygame.Vector2(self.waypoints[self.target_waypoint])
        travel = target - self.pos
        dist = travel.length()

        # Set animation direction
        if abs(travel.x) > abs(travel.y):
            self.anim_dir = "right" if travel.x > 0 else "left"
        else:
            self.anim_dir = "down" if travel.y > 0 else "up"

        # Move
        if dist > 0:
            self.pos += travel.normalize() * min(dist, self.speed)
        else:
            self.pos = target
            self.target_waypoint += 1

        self.rect.center = self.pos

    # Animation
    def animate(self):
        frames = self.anim[self.anim_dir]
        self.frame += self.frame_speed
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

        # Apply hit flash
        if self.is_hit:
            # Tint red
            red_image = self.image.copy()
            red_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 120))  # semi-transparent red
            red_image.blit(red_overlay, (0, 0))
            self.image = red_image

        self.rect = self.image.get_rect(center=self.pos)

    # Take damage with hit flash
    def take_damage(self, amt):
        self.hp -= amt
        if self.hp <= 0:
            self.die()
            return

        # Trigger hit flash
        self.is_hit = True
        self.hit_timer = time.time()

    # Monster death
    def die(self):
        if self.money_system:
            self.money_system.on_enemy_killed()  # give money!
        self.kill()

    # Draw small HP bar
    def draw_hp(self, surf):
        w, h = 28, 5
        x = self.rect.centerx - w // 2
        y = self.rect.top - 8

        # Red background
        pygame.draw.rect(surf, (255,0,0), (x, y, w, h))
        # Green current HP
        pygame.draw.rect(surf, (0,255,0), (x, y, int(w * self.hp / self.max_hp), h))
        # Optional: black border
        pygame.draw.rect(surf, (0,0,0), (x, y, w, h), 1)

    def update(self, dt=None):
        # Remove hit effect after duration
        if self.is_hit and (time.time() - self.hit_timer) >= self.hit_duration:
            self.is_hit = False

        self.move()
        self.animate()

