from settings import *

class AllSprite(pygame.sprite.Group):
    def __init__(self, game_width, game_height):
        super().__init__()
        self.display = None        # will be assigned by Game
        self.offset = pygame.Vector2()
        
        # store internal resolution
        self.game_width = game_width
        self.game_height = game_height
    
    def set_target_surface(self, surface):
        self.display = surface

    def draw(self):
        for sprite in self:
            self.display.blit(sprite.image, sprite.rect.topleft)

class Sprites(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

class Objects(pygame.sprite.Sprite):
    def __init__(self, pos, surface, scale, rotation ,groups):
        super().__init__(groups)
        self.rotation = rotation
        self.image = surface
        #self.image = pygame.transform.rotozoom(self.image, self.rotation * -1, 1)
        self.image = pygame.transform.smoothscale(self.image, scale)
        self.rect = self.image.get_rect(topleft = pos)
