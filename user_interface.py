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
        
    def onMouseOver(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.name != "startscreen":
            if self.rect.collidepoint(mouse_pos):
                if not self.hovered:
                    self.hovered = True
                    scale_factor = 1.1
                    new_size = (int(self.base_size[0] * scale_factor), int(self.base_size[1] * scale_factor))
                    self.image = pygame.transform.smoothscale(self.base_image, new_size)
                    # keep the top-left position consistent
                    self.rect = self.image.get_rect(center=self.pos)
            else:
                if self.hovered:
                    self.hovered = False
                    self.image = self.base_image
                    self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.onMouseOver()