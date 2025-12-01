import pygame

class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, idle_frames, building_frames, upgrade_frames,
                damage=10, range_=100, fire_rate=1.0,
                projectile_image=None, projectile_speed=300, size=(64, 64),
                money_system=None, tower_type=None,weapon_frames=None,sound_path=None):
                money_system=None, tower_type=None,sound_path=None, sfx_volume=1.0):

        super().__init__()
        MAX_LEVEL = 3
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
        self.weapon_animating = False

        # --- Apply permanent upgrades (global stat boosts) ---
        self.tower_type = tower_type

        if tower_type and hasattr(money_system, "game"):
            upgrades = money_system.game.permanent_upgrades.get(tower_type, {})

            self.damage *= upgrades.get("damage_mult", 1.0)
            self.range *= upgrades.get("range_mult", 1.0)
            self.fire_rate *= upgrades.get("fire_rate_mult", 1.0)
            self.projectile_speed *= upgrades.get("projectile_speed_mult", 1.0)

        # --- Money System ---
        self.money_system = money_system  # store reference

        # --- Selection & UI ---
        self.selected = False
        self.delete_button = None
        self.upgrade_button = None

        # --- Sound ---
        if sound_path:
            self.shoot_sound = pygame.mixer.Sound(sound_path)
            self.shoot_sound.set_volume(sfx_volume)
        else:
            self.shoot_sound = None

        self.weapon_frames = [pygame.transform.scale(img, size) for img in weapon_frames] \
            if weapon_frames else []
        
        self.weapon_frame = 0
        self.weapon_anim_time = 0
        self.weapon_anim_speed = 0.07  # speed of attack animation
        self.weapon_image = self.weapon_frames[0] if self.weapon_frames else None
        
        if self.weapon_frames:
            self.weapon_image = self.weapon_frames[0]
            self.weapon_rect = self.weapon_image.get_rect(center=self.rect.center)
        else:
            self.weapon_image = None
            self.weapon_rect = None

        self.shot_cooldown = 1.0 / self.fire_rate      # seconds per shot
        self.shot_timer = 0.0

        self.weapon_offset = (0, -10)  # adjust y to lift weapon above tower


    # -----------------------------
    # Update per frame
    # -----------------------------
    def update(self, dt, monsters=None, all_sprites=None):
        self._update_animation(dt)
        self._attack(monsters, all_sprites, dt)
        # advance projectile group
        self.projectiles.update(dt)

        # advance weapon animation if active
        # ONLY animate weapon if it's actually attacking
        if self.weapon_animating and self.weapon_frames:
            self.weapon_anim_time += dt
            if self.weapon_anim_time >= self.weapon_anim_speed:
                self.weapon_anim_time = 0
                self.weapon_frame += 1

                # If reached end of animation → stop animation
                if self.weapon_frame >= len(self.weapon_frames):
                    self.weapon_animating = False
                    self.weapon_frame = 0
                    self.weapon_image = self.weapon_frames[0]  # back to idle
                else:
                    # Change to next frame
                    base = self.weapon_frames[self.weapon_frame]
                    self.weapon_image = base

                # Recalculate weapon_rect
                ox, oy = self.weapon_offset
                self.weapon_rect = self.weapon_image.get_rect(
                    center=(self.rect.centerx + ox, self.rect.centery + oy)
        )

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
    def _attack(self, monsters, all_sprites, dt):

        # Do nothing if no enemies or tower still building
        if not monsters or self.state == "building":
            return

        # Get the closest or nearest target
        target = self.get_target(monsters)
        if not target:
            return

        # Rotate weapon TOWARD target (but do not animate)
        self.rotate_weapon_toward(target)

        # Handle cooldown timer
        self.shot_timer += dt

        # If not ready to shoot, exit
        if self.shot_timer < self.shot_cooldown:
            return

        # READY TO FIRE : reset cooldown
        self.shot_timer = 0

        # --- Trigger weapon animation ONLY when firing ---
        if self.weapon_frames:
            self.weapon_animating = True
            self.weapon_frame = 0
            self.weapon_anim_time = 0
            self.weapon_image = self.weapon_frames[0]

        # ---- FIRE PROJECTILE ----
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

        if self.shoot_sound:
            self.shoot_sound.play()

    def rotate_weapon_toward(self, target):
        if not self.weapon_frames or not self.weapon_image:
            return

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery

        # compute angle - choose sign that looks correct (may require invert)
        angle = -pygame.math.Vector2(dx, dy).angle_to((1, 0))

        base = self.weapon_frames[self.weapon_frame]
        rotated = pygame.transform.rotate(base, angle)
        self.weapon_image = rotated

        ox, oy = getattr(self, "weapon_offset", (0, -10))
        self.weapon_rect = self.weapon_image.get_rect(center=(self.rect.centerx + ox,
                                                              self.rect.centery + oy))

    def play_weapon_attack_animation(self):
        # restart animation; it will advance in update()
        self.weapon_frame = 0
        self.weapon_anim_time = 0.0
        if self.weapon_frames:
            self.weapon_image = self.weapon_frames[0]
            ox, oy = getattr(self, "weapon_offset", (0, -10))
            self.weapon_rect = self.weapon_image.get_rect(center=(self.rect.centerx + ox,
                                                                  self.rect.centery + oy))
    
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
        MAX_LEVEL = 3  
        # Prevent upgrades if max reached
        if self.level >= MAX_LEVEL:
            print("Tower already at max level!")
            return
        # Prevent upgrading while already upgrading
        if self.state == "upgrading":
            return
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
    
    def draw(self, surface):
        # draw tower base
        surface.blit(self.image, self.rect)

        # draw weapon above tower (if exists)
        if self.weapon_image and self.weapon_rect:
            surface.blit(self.weapon_image, self.weapon_rect)

        # optionally draw projectiles (if they are not automatically in all_sprites)
        for p in self.projectiles:
            try:
                surface.blit(p.image, p.rect)
            except Exception:
                pass

    def _set_image_preserve_center(self, new_image):
        """Set new self.image but keep the same center to avoid jumps."""
        try:
            prev_center = self.rect.center
        except Exception:
            prev_center = (0, 0)
        self.image = new_image
        self.rect = self.image.get_rect(center=prev_center)

        # Re-anchor weapon relative to the new rect center
        if self.weapon_image:
            ox, oy = getattr(self, "weapon_offset", (0, -10))
            self.weapon_rect = self.weapon_image.get_rect(center=(self.rect.centerx + ox,
                                                                  self.rect.centery + oy))


