from settings import *
from user_interface import UserInterface, SliderHandle

class Slider:
    def __init__(self, name, pos, bar_surface, bar_scale,
                handle_surface, handle_scale, ui_group,
                min_value=0.0, max_value=1.0, default_value=0.5,
                game_width=None, game_height=None, hover_sfx=None):

        self.name = name
        self.game_width = game_width
        self.game_height = game_height
        self.dragging = False

        # BAR (inherits move_to/move_away animations)
        self.bar = UserInterface(
            name=name,
            pos=pos,
            surface=bar_surface,
            scale=bar_scale,
            group=ui_group,
            game_width=game_width,
            game_height=game_height,
            hover_sfx=hover_sfx
        )

        # Store bar width
        self.bar_width = self.bar.rect.width
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value

        self.handle = SliderHandle(
            name=f"{name}_handle",
            pos=pos,
            surface=handle_surface,
            scale=handle_scale,
            group=ui_group,
            slider_ref=self,
            game_width=game_width,
            game_height=game_height,
            hover_sfx=hover_sfx
        )

        # Finalize initial handle position
        self.update_handle_position()

    def set_value(self, value: float):
        """Set slider value externally (e.g., from loaded settings)."""
        self.value = max(self.min_value, min(self.max_value, value))
        self.update_handle_position()

    # ----------------------------------------------------
    # POSITION <-> VALUE MAPPING
    # ----------------------------------------------------
    def update_value_from_mouse(self, mouse_x):
        left = self.bar.pos.x - self.bar_width / 2
        right = self.bar.pos.x + self.bar_width / 2

        t = (mouse_x - left) / (right - left)
        t = max(0.0, min(1.0, t))

        self.value = self.min_value + t * (self.max_value - self.min_value)
        self.update_handle_position()

    def update_handle_position(self):
        t = (self.value - self.min_value) / (self.max_value - self.min_value)
        x = self.bar.pos.x - self.bar_width / 2 + t * self.bar_width

        self.handle.pos.x = x
        self.handle.pos.y = self.bar.pos.y
        self.handle.rect.center = (round(x), round(self.bar.pos.y))

    # ----------------------------------------------------
    # EXTERNAL API USED BY main.py
    # ----------------------------------------------------
    def handle_event(self, event, game_mouse_pos):
        self.handle.handle_event(event, game_mouse_pos)

    def update(self, dt, mouse_pos):
        self.bar.update(dt, mouse_pos)
        self.handle.update(dt, mouse_pos)

    def get_value(self):
        return self.value

    def draw(self, surface):
        # bar is auto-drawn by ui_sprites
        surface.blit(self.handle.image, self.handle.rect)
