from settings import *

class UserInterface(pygame.sprite.Sprite):
    def __init__(self, name, pos, surface, scale, group):
        super().__init__(group)
        self.name = name
        # store the base (scaled) image and position so we can toggle hover without compounding
        self.base_image = pygame.transform.scale(surface, scale)
        self.image = self.base_image

        if self.name != "startscreen":
            self.rect = self.image.get_rect(center = pos)
        else:
            self.rect = self.image.get_rect(topleft = pos)
        
        self.pos = pos
        self.base_size = self.base_image.get_size()
        self.hovered = False

        try:
            self.hover_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'mouse-hover.wav'))
        except Exception:
            self.hover_sfx = None
        
    def onMouseOver(self, mouse_pos=None):
        # mouse_pos should be in game-surface coordinates. If not provided, use screen coords.
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        if self.name != "cloud" and self.name != "startscreen":
            if self.rect.collidepoint(mouse_pos):
                if not self.hovered:
                    self.hovered = True
                    scale_factor = 1.1
                    new_size = (int(self.base_size[0] * scale_factor), int(self.base_size[1] * scale_factor))
                    self.image = pygame.transform.smoothscale(self.base_image, new_size)
                    # keep the position consistent (center for buttons)
                    self.rect = self.image.get_rect(center=self.pos)
                    if self.hover_sfx:
                        try:
                            self.hover_sfx.play()
                        except Exception:
                            pass
            else:
                if self.hovered:
                    self.hovered = False
                    self.image = self.base_image
                    self.rect = self.image.get_rect(center=self.pos)

    def move(self, dt):
        if self.name == "cloud":
            self.rect.x += randint(75, 200) * dt
            if self.rect.left > 1280:  # If cloud moves off screen, reset to left
                self.rect.right = 0

    def update(self, dt):
        self.onMouseOver()
        self.move(dt)