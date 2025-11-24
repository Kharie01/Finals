import pygame

class CastleBox(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, group, image):
        super().__init__(group)

        self.image = pygame.transform.scale(image, (width, height))
        x, y = pos
        y += height // 100
        self.rect = self.image.get_rect(topleft=(x, y))

        #10Default: NO HP unless activated
        self.has_hp = False
        self.max_hp = 100
        self.hp = 100

        # Enable HP only for the specific image
        if "image-removebg-preview (23)" in getattr(image, "__dict__", {}):
            self.has_hp = True

    def take_damage(self, amount):
        if self.has_hp:
            self.hp = max(0, self.hp - amount)

    def draw_health(self, surface):
        if not self.has_hp:
            return   # Do NOT draw HP for other castles

        bar_width = self.rect.width
        bar_height = 10

        fill = (self.hp / self.max_hp) * bar_width
        bar_x = self.rect.x
        bar_y = self.rect.y - 15

        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, fill, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
