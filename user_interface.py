from settings import *

class UserInterface(pygame.sprite.Sprite):
    def __init__(self, name, pos, surface, scale, group, game_width, game_height, hover_sfx = None):
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
        if self.name == "up":
            self.base_image = pygame.transform.rotate(self.base_image, 180)
        self.pos = pygame.math.Vector2(pos)

        self.target_pos = None
        self.move_speed = 6.0
        self.base_size = self.base_image.get_size()
        self.hovered = False

        self.hover_sfx = hover_sfx
        
        # Create a dimmed version
        self.image = self.base_image
        self.dimmed_image = self.make_dimmed_version(self.image, factor=0.5)
        self.is_dimmed = False

    def onMouseOver(self, game_mouse_pos):
        if self.name in ("cloud", "startscreen", "slider_music", "slider_sfx"):
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
        elif self.name == "play_back_btn":
            self.target_pos = pygame.math.Vector2(150, 60)
        elif self.name == "ui_play_btn":
            self.target_pos = pygame.math.Vector2(self.game_width // 2, self.game_height - 100)
        elif self.name == "map" or self.name == "play":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2 - 100)
        elif self.name == "upgrades" or self.name == "settings":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2)
        elif self.name == "back" or self.name == "exit":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 360, self.game_height // 2 + 100)
        elif self.name == "map_1":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 200, 325)
        elif self.name == "map_2":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 150, 325)
        elif self.name == "ui_display":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 300, 150)
        elif self.name == "ui_music":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 330, 470)
        elif self.name == "ui_sfx":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 355, 570)
        elif self.name == "slider_music":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 200, 470)
        elif self.name == "slider_sfx":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 200, 570)
        elif self.name == "resolution_dd":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 200, 150)
        elif self.name == "archer_tower":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 450, self.game_height // 2)
        elif self.name == "stone_tower":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 - 150, self.game_height // 2)
        elif self.name == "sling_shot_tower":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 150, self.game_height // 2)
        elif self.name == "bomb_tower":
            self.target_pos = pygame.math.Vector2(self.game_width // 2 + 450, self.game_height // 2)
        else:
            self.target_pos = None

    def move_away(self):
        # Animate back to off-screen positions
        if self.name == "logo":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 - 250)
        elif self.name == "ui_bg":
            self.target_pos = pygame.math.Vector2(-self.game_width, self.game_height // 2)
        elif self.name == "ui_back_btn" or self.name == "play_back_btn":
            self.target_pos = pygame.math.Vector2(-self.game_width + 60, 0 + 60)
        elif self.name == "ui_play_btn":
            self.target_pos = pygame.math.Vector2(-self.game_width, self.game_height - 200)
        elif self.name == "map" or self.name == "play":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 - 100)
        elif self.name == "upgrades" or self.name == "settings":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2)
        elif self.name == "back" or self.name == "exit":
            self.target_pos = pygame.math.Vector2(self.game_width + 360, self.game_height // 2 + 100)
        elif self.name == "map_1":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 - 150, 150)
        elif self.name == "map_2":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 150, 150)
        elif self.name == "ui_display":
            self.target_pos = pygame.math.Vector2(-self.game_width, 200)
        elif self.name == "ui_music":
            self.target_pos = pygame.math.Vector2(-self.game_width, 370)
        elif self.name == "ui_sfx":
            self.target_pos = pygame.math.Vector2(-self.game_width, 470)
        elif self.name == "slider_music":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 200, 370)
        elif self.name == "slider_sfx":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 200, 470)
        elif self.name == "resolution_dd":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 200, 200)
        elif self.name == "archer_tower":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 - 450, 150)
        elif self.name == "stone_tower":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 - 200, 150)
        elif self.name == "sling_shot_tower":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 50, 150)
        elif self.name == "bomb_tower":
            self.target_pos = pygame.math.Vector2(-self.game_width // 2 + 300, 150)
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
            if self.name == "startscreen":
                self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))
            else:
                self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

        self.move(dt)

#--------------------------------------------------------------
# Slider UI Element
#--------------------------------------------------------------
class SliderHandle(UserInterface):
    def __init__(
        self,
        name,
        pos,
        surface,
        scale,
        group,
        slider_ref,   # reference to parent Slider object
        game_width,
        game_height,
        hover_sfx
    ):
        super().__init__(name, pos, surface, scale, group, game_width, game_height, hover_sfx)
        self.slider = slider_ref
        self.dragging = False

    def handle_event(self, event, game_mouse_pos):
        gx, gy = game_mouse_pos

        # Only handle mouse events
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            return

        # CLICK
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint((gx, gy)):
                self.dragging = True

        # RELEASE
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        # DRAGGING
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.slider.update_value_from_mouse(gx)

    def update(self, dt, mouse_pos=None):
        # keep UI animation working
        super().update(dt, mouse_pos)

        # sync handle position to slider value every frame
        self.slider.update_handle_position()



# --------------------------------------------------------------
# Correct Dropdown System (Final - Fully Working)
# --------------------------------------------------------------

class Dropdown(UserInterface):
    def __init__(self, name, pos, surface, scale, group,
                game_width, game_height, hover_sfx=None):

        super().__init__(name, pos, surface, scale, group,
                        game_width, game_height, hover_sfx)

        self.ui_group = group
        self.options = []
        self.option_offsets = []
        self.open = False
        self.parent_group = group
        self.label_surface = surface  # initial label is the parent surface
        self.label_scale = scale

    # ----------------------------------------------------------
    # Add an option to the dropdown
    # ----------------------------------------------------------
    def add_option(self, name, surface, scale, offset_y=0, hover_sfx=None):
        option_x = self.pos.x
        option_y = self.pos.y + offset_y
        option = UserInterface(name, (option_x, option_y), surface, scale, self.ui_group, self.game_width, self.game_height, hover_sfx)
        self.options.append(option)
        self.option_offsets.append(offset_y)

        option.visible = False
        self.parent_group.remove(option)  # hide until opened

    # ----------------------------------------------------------
    # Change label displayed on the dropdown button
    # ----------------------------------------------------------
    def set_label(self, new_surface, new_scale = None):
        self.base_image = new_surface
        if new_scale:
            self.base_image = pygame.transform.scale(new_surface, new_scale)
            self.label_scale = new_scale
        self.image = self.base_image
        # update rect so it stays centered
        self.rect = self.image.get_rect(center=self.pos)

    # ----------------------------------------------------------
    # Toggle open/close
    # ----------------------------------------------------------
    def toggle(self):
        self.open = not self.open

        if self.open:
            for opt in self.options:
                opt.visible = True
                self.parent_group.add(opt)
                opt.move_to()
        else:
            for opt in self.options:
                opt.visible = False
                opt.move_away()
                self.parent_group.remove(opt)

    # ----------------------------------------------------------
    # Click handler - MUST be called before UI sprite loop
    # ----------------------------------------------------------
    def handle_click(self, game_pos):
        # If menu is closed → only the main button handles clicks
        if not self.open:
            if self.rect.collidepoint(game_pos):
                self.toggle()
                return None
            return None

        if self.open:
            for opt in self.options:
                if opt.visible and opt.rect.collidepoint(game_pos):
                    self.set_label(opt.base_image, opt.base_size)
                    value = opt.name
                    self.toggle()
                    return value

        # Click outside options → close menu
        self.toggle()
        return None

    # ----------------------------------------------------------
    # Update animations & hover (main button)
    # ----------------------------------------------------------
    def update(self, dt, game_mouse_pos=None):
        # First update parent itself
        super().update(dt, game_mouse_pos)

        if self.open:
            for i, option in enumerate(self.options):
                option.pos.x = self.pos.x
                option.pos.y = self.pos.y + (i + 1) * 80  # or whatever spacing you want
                option.rect.center = (round(option.pos.x), round(option.pos.y))



class DropdownOption(UserInterface):
    """
    An option inside the dropdown.
    Always updated by Dropdown, not by main loop.
    """
    def __init__(self, name, pos, surface, scale, group,
                 parent, game_width, game_height, hover_sfx):

        super().__init__(name, pos, surface, scale, group,
                         game_width, game_height, hover_sfx)

        self.parent = parent
        self.visible = False

    def update(self, dt, mouse_pos=None):
        if not self.visible:
            return
        super().update(dt, mouse_pos)

        self.onMouseOver()

