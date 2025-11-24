import pygame

class Tower(pygame.sprite.Sprite):
    """Tower class with drag/drop, upgrade, delete, and attack logic."""

    def __init__(self, pos, image=None, tower_type="basic"):
        super().__init__()
        self.type = tower_type
        self.level = 1
        self.pos = pygame.Vector2(pos)
        self.image = image if image else pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=self.pos)

        # Tower stats
        self.range = 100
        self.damage = 10
        self.attack_speed = 1  # attacks per second
        self.last_attack_time = 0

        # Buttons (for UI)
        self.delete_button = pygame.Rect(0,0,0,0)
        self.upgrade_button = pygame.Rect(0,0,0,0)
        self.selected = False

    # -------------------------------
    # Drag & drop
    # -------------------------------
    def start_drag(self, mouse_pos):
        self.pos = pygame.Vector2(mouse_pos)
        self.rect.center = self.pos

    # -------------------------------
    # Selection
    # -------------------------------
    def select(self):
        self.selected = True
        self.update_buttons()

    def deselect(self):
        self.selected = False
        self.delete_button = None
        self.upgrade_button = None

    # -------------------------------
    # Buttons
    # -------------------------------
    def update_buttons(self):
        if self.selected:
            self.delete_button = pygame.Rect(self.rect.right + 10, self.rect.top, 50, 30)
            self.upgrade_button = pygame.Rect(self.rect.right + 10, self.rect.top + 40, 50, 30)
        else:
            self.delete_button = None
            self.upgrade_button = None

    def handle_button_click(self, mouse_pos):
        if self.selected:
            if self.delete_button and self.delete_button.collidepoint(mouse_pos):
                return "delete"
            if self.upgrade_button and self.upgrade_button.collidepoint(mouse_pos):
                self.upgrade()
                return "upgrade"
        return None

    # -------------------------------
    # Upgrade
    # -------------------------------
    def upgrade(self):
        self.level += 1
        self.damage += 5
        self.range += 10
        self.attack_speed += 0.1
        self.image.fill((0, 0, 255))  # simple visual upgrade

    # -------------------------------
    # Attack logic placeholder
    # -------------------------------
    def attack(self, monsters, current_time):
        if current_time - self.last_attack_time >= 1 / self.attack_speed:
            for monster in monsters:
                if self.rect.center.distance_to(monster.rect.center) <= self.range:
                    monster.take_damage(self.damage)
                    self.last_attack_time = current_time
                    break

    # -------------------------------
    # Update
    # -------------------------------
    def update(self, dt):
        self.rect.center = self.pos

    # -------------------------------
    # Draw UI buttons
    # -------------------------------
    def draw_buttons(self, surface):
        if self.selected:
            pygame.draw.rect(surface, (255, 0, 0), self.delete_button)
            pygame.draw.rect(surface, (0, 255, 0), self.upgrade_button)
