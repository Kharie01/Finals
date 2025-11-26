from settings import *

class UserInterface(pygame.sprite.Sprite):
    def __init__(self, name, pos, surface, scale, group, game_width=1280, game_height=704):
        super().__init__(group)
        self.name = name
        self.game_width = game_width
        self.game_height = game_height
        
        self.base_image = pygame.transform.scale(surface, scale)
        self.image = self.base_image

        if self.name != "startscreen":
            self.rect = self.image.get_rect(center = pos)
        else:
            self.rect = self.image.get_rect(topleft = pos)
        

        self.pos = pygame.math.Vector2(pos)

        self.target_pos = None
        self.move_speed = 6.0
        self.base_size = self.base_image.get_size()
        self.hovered = False

        try:
            self.hover_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'mouse-hover.wav'))
        except Exception:
            self.hover_sfx = None
        
        # Create a dimmed version
        self.image = self.base_image
        self.dimmed_image = self.make_dimmed_version(self.image, factor=0.5)
        self.is_dimmed = False

    def onMouseOver(self, game_mouse_pos):
        """Hover detection using GAME coordinates (never screen coords)."""
        if self.name in ("cloud", "startscreen"):
            return

        if self.rect.collidepoint(game_mouse_pos):
            if not self.hovered and not self.is_dimmed:
                self.hovered = True
                scale_factor = 1.1
                new_size = (
                    int(self.base_size[0] * scale_factor),
                    int(self.base_size[1] * scale_factor)
                )
                self.image = pygame.transform.smoothscale(self.base_image, new_size)
                self.rect = self.image.get_rect(center=self.pos)

                if self.hover_sfx:
                    try:
                        self.hover_sfx.play()
                    except:
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

    def move_to(self):
        if self.name == "logo":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2 - 250)
        elif self.name == "ui_bg":
            self.target_pos = pygame.math.Vector2(self.game_width // 2, self.game_height // 2)
        elif self.name == "ui_back_btn":
            self.target_pos = pygame.math.Vector2(150, 100)
        elif self.name == "ui_play_btn":
            self.target_pos = pygame.math.Vector2(self.game_width // 2, self.game_height - 100)
        elif self.name == "map":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2 - 100)
        elif self.name == "upgrades":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2)
        elif self.name == "back":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2 + 100)
        elif self.name == "map_1":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 200, 325)
        else:
            self.target_pos = None

    def move_away(self):
        # Animate back to off-screen positions
        if self.name == "logo":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 - 250)
        elif self.name == "ui_bg":
            self.target_pos = pygame.math.Vector2(-self.game_width, self.game_height // 2)
        elif self.name == "ui_back_btn":
            self.target_pos = pygame.math.Vector2(-self.game_width + 60, 0 + 60)
        elif self.name == "ui_play_btn":
            self.target_pos = pygame.math.Vector2(-self.game_width, self.game_height - 200)
        elif self.name == "map":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 - 100)
        elif self.name == "upgrades":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2)
        elif self.name == "back":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 + 100)
        elif self.name == "map_1":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 - 150, 0 + 150)
        else:
            self.target_pos = None

    def set_dimmed(self, state: bool):
        if state and not self.is_dimmed:
            self.image = self.dimmed_image
            self.is_dimmed = True
        elif not state and self.is_dimmed:
            self.image = self.base_image
            self.is_dimmed = False

    def make_dimmed_version(self, image, factor=0.5):
        dimmed = image.copy()

        # Multiply RGB channels by the dim factor
        darken = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        rgb = int(255 * factor)         # factor: 1.0 = normal, 0.5 = dimmer
        darken.fill((rgb, rgb, rgb, 255))

        dimmed.blit(darken, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def set_opacity(self, alpha):
        """Set the opacity of the image (0-255, where 255 is fully opaque)"""
        self.base_image.set_alpha(alpha)
        self.image = self.base_image

    def update(self, dt, game_mouse_pos = None):
        if game_mouse_pos is not None:
            self.onMouseOver(game_mouse_pos)

        if self.target_pos is not None:
            to_target = self.target_pos - self.pos
            if to_target.length() <= 0.5:
                self.pos = self.target_pos
                self.target_pos = None
            else:
                step = to_target * min(1.0, self.move_speed * dt)
                self.pos += step
            if self.name in ("ui_bg", "ui_back_btn", "ui_play_btn"):
                self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
            elif self.name == "startscreen":
                self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))
            else:
                self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

        self.move(dt)