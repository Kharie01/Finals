import os
# Must be set BEFORE pygame.init()
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
import pygame
from pytmx.util_pygame import load_pygame
from os.path import join
from random import randint, uniform
import math
import json
import sys

TILE_SIZE = 32

def resource_path(relative_path):
    # For PyInstaller compatibility (bundles assets into temp folder)
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".fortress_frontline")
os.makedirs(SAVE_DIR, exist_ok=True)

SETTINGS_SAVE = os.path.join(SAVE_DIR, "settings.json")
UPGRADES_SAVE = os.path.join(SAVE_DIR, "permanent_upgrades.json")
PLAYER_SAVE = os.path.join(SAVE_DIR, "player.json")

def confirmation(game, message="Are you sure?"):
    # ----------- Colors (from your HUD screenshot) -----------
    PANEL_BG     = (71, 42, 26)
    PANEL_BORDER = (44, 28, 19)
    PANEL_SHADOW = (0, 0, 0, 120)
    # ----------- Fonts -----------
    title_font = pygame.font.Font(resource_path("assets/Monocraft-Bold.ttf"), 32)
    sub_font   = pygame.font.Font(resource_path("assets/Monocraft-Bold.ttf"), 20)
    # ----------- Render text -----------
    title_surf = title_font.render(message, True, (255, 255, 255))
    esc_surf   = sub_font.render("Press ESC to cancel", True, (255, 180, 180))
    space_surf = sub_font.render("Press SPACE to confirm", True, (180, 255, 180))
    # ----------- Box sizing -----------
    padding = 40
    spacing = 20
    max_w = max(title_surf.get_width(), esc_surf.get_width(), space_surf.get_width())
    total_h = (
        title_surf.get_height() +
        esc_surf.get_height() +
        space_surf.get_height() +
        spacing * 2
    )
    box_w = max_w + padding * 2
    box_h = total_h + padding * 2
    box_x = (game.GAME_WIDTH - box_w) // 2
    box_y = (game.GAME_HEIGHT - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    # ----------- Modal loop (blocks until space/esc) -----------
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60)
        # Handle events specifically for this dialog
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    return True
        # ----------- Darken background -----------
        dark = pygame.Surface((game.GAME_WIDTH, game.GAME_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160))
        game.game_surface.blit(dark, (0, 0))
        # ----------- Draw shadow -----------
        shadow = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        shadow.fill(PANEL_SHADOW)
        game.game_surface.blit(shadow, (box_x, box_y + 4))
        # ----------- Draw Panel -----------
        pygame.draw.rect(game.game_surface, PANEL_BG, box_rect, border_radius=12)
        pygame.draw.rect(game.game_surface, PANEL_BORDER, box_rect, 3, border_radius=12)
        # ----------- Draw Text (centered) -----------
        cx = box_rect.centerx
        y = box_rect.y + padding
        game.game_surface.blit(title_surf, (cx - title_surf.get_width() // 2, y))
        y += title_surf.get_height() + spacing
        game.game_surface.blit(esc_surf, (cx - esc_surf.get_width() // 2, y))
        y += esc_surf.get_height() + spacing
        game.game_surface.blit(space_surf, (cx - space_surf.get_width() // 2, y))
        # ----------- Apply scaling before showing ----------- 
        window_w, window_h = game.screen.get_size()
        scaled = pygame.transform.smoothscale(game.game_surface, (window_w, window_h))
        game.screen.blit(scaled, (0, 0))
        pygame.display.update()
