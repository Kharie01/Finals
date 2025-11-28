import pygame

class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, idle_frames, building_frames, upgrade_frames,
                 damage=10, range_=100, fire_rate=1.0,
                 projectile_image=None, projectile_speed=300, size=(64, 64),money_system=None):

        super().__init__()

        # --- Images ---
        self.idle_frames = [pygame.transform.scale(img, size) for img in idle_frames]
        self.building_frames = [pygame.transform.scale(img, size) for img in building_frames]
        self.upgrade_frames = [pygame.transform.scale(img, size) for img in upgrade_frames]

        # --- Animation & State ---
        self.state = "building"  # building, idle, upgrading
        self.level = 0  # current upgrade level
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_rate = 0.2  # seconds per frame
        self.upgrade_timer = 0
        self.upgrade_duration = 0.5  # seconds for upgrade transition
        self.image = self.building_frames[0]

        # --- Position ---
        self.rect = self.image.get_rect(center=(int(pos[0]), int(pos[1])))

        # --- Tower Stats ---
        self.range = range_
        self.damage = damage
        self.fire_rate = fire_rate
        self.projectile_image = projectile_image
        self.projectile_speed = projectile_speed
        self.projectiles = pygame.sprite.Group()
        self.last_shot = 0

         # --- Money System ---
        self.money_system = money_system  # store reference

        # --- Selection & UI ---
        self.selected = False
        self.delete_button = None
        self.upgrade_button = None

    # -----------------------------
    # Update per frame
    # -----------------------------
    def update(self, dt, monsters=None, all_sprites=None):
        self._update_animation(dt)
        self._attack(monsters, all_sprites)
        self.projectiles.update(dt)

    # -----------------------------
    # Animation handler
    # -----------------------------
    def _update_animation(self, dt):
        self.frame_timer += dt

        if self.state == "building":
            if self.frame_timer >= self.frame_rate:
                self.frame_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.building_frames):
                    self.state = "idle"
                    self.current_frame = 0
                    self.image = self.idle_frames[0]
                else:
                    self.image = self.building_frames[self.current_frame]

        elif self.state == "upgrading":
            self.upgrade_timer += dt
            if self.level > 0:
                self.image = self.upgrade_frames[self.level - 1]  # show new level frame
            if self.upgrade_timer >= self.upgrade_duration:
                # Apply pending stats after animation
                if hasattr(self, "pending_stats"):
                    self.damage += self.pending_stats["damage"]
                    self.range += self.pending_stats["range"]
                    self.fire_rate += self.pending_stats["fire_rate"]
                    del self.pending_stats

                self.state = "idle"
                self.upgrade_timer = 0

        # Queue next upgrade if needed
        if hasattr(self, "upgrade_queued") and self.upgrade_queued:
            self.upgrade_queued = False
            self.upgrade()

        # Check if an upgrade was queued
        if hasattr(self, "upgrade_queued") and self.upgrade_queued:
            self.upgrade_queued = False
            self.upgrade()


        elif self.state == "idle":
            # Optional: loop idle frames if multiple
            if len(self.idle_frames) > 1 and self.frame_timer >= self.frame_rate:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                self.image = self.idle_frames[self.current_frame]

    # -----------------------------
    # Attack Logic
    # -----------------------------
    def _attack(self, monsters, all_sprites):
        if not monsters or self.state == "building":
            return

        target = self.get_target(monsters)
        if target:
            now = pygame.time.get_ticks()
            if now - self.last_shot >= 1000 / self.fire_rate:
                from projectile import Projectile
                proj = Projectile(
                    self.rect.center,
                    target,
                    self.damage,
                    self.projectile_image,
                    self.projectile_speed,
                    self.projectiles
                )
                if all_sprites:
                    all_sprites.add(proj)
                self.last_shot = now
    
    def on_monster_killed(self):
        if self.money_system:
            self.money_system.on_enemy_killed()

    def get_target(self, monsters):
        nearest = None
        min_dist_sq = self.range ** 2
        for m in monsters:
            dx = m.rect.centerx - self.rect.centerx
            dy = m.rect.centery - self.rect.centery
            dist_sq = dx * dx + dy * dy
            if dist_sq <= min_dist_sq:
                nearest = m
                min_dist_sq = dist_sq
        return nearest

    # -----------------------------
    # Upgrade Tower
    # -----------------------------
    def upgrade(self):
        if self.state != "upgrading" and self.level < len(self.upgrade_frames):
            self.level += 1
            self.state = "upgrading"
            self.upgrade_timer = 0
            self.current_frame = 0
            # Queue stats update after animation
            self.pending_stats = {"damage": 5, "range": 20, "fire_rate": 0.5}



    # -----------------------------
    # Selection & UI
    # -----------------------------
    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def draw_selection(self, surface):
        if not self.selected:
            self.delete_button = None
            self.upgrade_button = None
            return

        # Draw range circle
        cx, cy = self.rect.center
        overlay = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (0, 255, 0, 50), (self.range, self.range), self.range)
        pygame.draw.circle(surface, (0, 0, 255), (cx, cy), self.range, 2)
        surface.blit(overlay, (cx - self.range, cy - self.range))

        # Draw upgrade/delete buttons
        self.delete_button = pygame.Rect(self.rect.right + 10, self.rect.top, 50, 30)
        self.upgrade_button = pygame.Rect(self.rect.right + 10, self.rect.top + 40, 50, 30)
        pygame.draw.rect(surface, (255, 0, 0), self.delete_button)
        pygame.draw.rect(surface, (0, 255, 0), self.upgrade_button)
