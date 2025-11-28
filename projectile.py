import pygame

PROJECTILE_SIZE = (10, 10)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, target, damage, image=None, speed=300, groups=None):
        super().__init__(groups)
        self.pos = pygame.Vector2(pos)
        self.target = target
        self.damage = damage
        self.speed = speed

        # Image
        if image is None:
            # Default simple circle projectile
            self.image = pygame.Surface(PROJECTILE_SIZE, pygame.SRCALPHA)
            pygame.draw.circle(
                self.image,
                (255, 0, 0),
                (PROJECTILE_SIZE[0] // 2, PROJECTILE_SIZE[1] // 2),
                PROJECTILE_SIZE[0] // 2
            )
        else:
            # Always scale custom projectile images
            self.image = pygame.transform.scale(image.copy(), PROJECTILE_SIZE)

        self.rect = self.image.get_rect(center=self.pos)


    def update(self, dt):
        if not self.target or not self.target.alive():
            self.kill()
            return

        # Compute direction toward target
        direction = pygame.Vector2(self.target.rect.center) - self.pos
        distance = direction.length()
        if distance <= self.speed * dt:
            # Hit target
            if hasattr(self.target, "take_damage"):
                self.target.take_damage(self.damage)
            self.kill()
        else:
            direction.normalize_ip()
            self.pos += direction * self.speed * dt
            self.rect.center = self.pos
