import pygame


class CastleBox(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, group, image, game):
        super().__init__(group)

        self.game = game

        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1] + height // 100))

        # HP defaults
        self.has_hp = False
        self.max_hp = 100
        self.hp = 100

    def take_damage(self, amount):
        if not self.has_hp:
            return
        
        old_hp = self.hp
        self.hp = max(0, self.hp - amount)
        print("TAKE_DAMAGE CALLED - has_hp:", self.has_hp, "old_hp:", old_hp, "new_hp:", self.hp)

        # Assign HUD castle
        try:
            self.game.main_castle = self
        except:
            pass

        # GAME OVER TRIGGER — MUST CHECK BOTH CONDITIONS
        if old_hp > 0 and self.hp == 0:
            try:
                self.game.trigger_game_over()
            except Exception as e:
                print("Error", e)

    def draw_health(self, surface):
        if not self.has_hp:
            return

        # Draw only the health bar above the castle
        bar_width = self.rect.width
        bar_height = 10
        fill = (self.hp / self.max_hp) * bar_width

        x = self.rect.x
        y = self.rect.y - 15

        pygame.draw.rect(surface, (255, 0, 0), (x, y, fill, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)

        
