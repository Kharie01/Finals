import os
# Must be set BEFORE pygame.init()
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
from settings import *
from sprites import *
from monsters import Monster
from castle import CastleBox
from user_interface import UserInterface, Dropdown
from slider import Slider
from tower import Tower # import Tower class
from game_ai import ENEMY_TYPES, WaveDirector
from expSystem import ExperienceSystem

from pytmx.util_pygame import load_pygame

from money import MoneySystem 
import pygame
import json

class TowerDefense:
    """
    Main Tower Defense game class.
    Handles initialization, event loop, rendering, and game logic.
    """

    def __init__(self):
        pygame.init()
        self.main_castle = None
        self.load_display_settings()
        self.settings = self.load_display_settings()
        self.GAME_WIDTH  = 1280
        self.GAME_HEIGHT = 720
        self.fullscreen = False
        self.time_scale = 1.0
        self.fast_forward = False
        self.exp_system = ExperienceSystem()
        self.upgrade_cost = {
                "archer_tower": 1,
                "stone_tower": 1,
                "slingshot_tower": 1,
                "bomb_tower": 1
            }  # each tower upgrade costs 1 stat point


        if self.fullscreen:
            self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))

        self.game_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        self.settings = self.load_display_settings()
        self.current_resolution = self.settings["resolution"]

        self.apply_saved_resolution()
        pygame.display.set_caption("Fortress Frontline")
        pygame.display.set_icon(pygame.image.load(join('assets', 'images', 'icon', 'gameicon.ico')).convert_alpha())

        # Custom mouse cursor
        mouse_cursor_img = pygame.image.load(join('assets', 'images', 'mouse.png')).convert_alpha()
        mouse_cursor_img = pygame.transform.scale(mouse_cursor_img, (40, 32))  # Scale to cursor size
        mouse_cursor = pygame.cursors.Cursor((0, 0), mouse_cursor_img)
        pygame.mouse.set_cursor(mouse_cursor)
        
        # Wave director


        # Sprite groups
        self.all_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)
        self.ui_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)
        self.settings_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)

        self.start_ui = []
        self.settings_ui = []
        self.map_ui = []
        self.map_selection_ui = []
        self.upgrade_ui = []

        self.castles = pygame.sprite.Group()  # Initialize empty castles group
        self.monsters = pygame.sprite.Group()  # Initialize empty monsters group

        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.show_start = False
        self.show_map = False
        self.paused = False
        self.inGame = False
        self.settings_ui_created = False
        self.game_over = False
        self.show_upgrades = False
        self.base_exp = 25
        self.exp_multiplier = 1.15

        # Sounds
        self.button_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'button-click.wav'))
        self.start_bgmusic = pygame.mixer.Sound(join('assets', 'audio', 'bgm', 'start_bgm.wav'))
        self.game_bgmusic = pygame.mixer.Sound(join('assets', 'audio', 'bgm', 'game_bgm.wav'))
        self.hover_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'mouse-hover.wav'))
        self.gameover_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'gameover.wav'))

        # Load UI images
        self.startscreen_images = {
            "start": pygame.image.load(join('assets', 'images', 'startscreen', 'Startscreen.png')).convert_alpha(),
            "logo": pygame.image.load(join('assets', 'images', 'startscreen', 'logo.png')).convert_alpha(),
            "play": pygame.image.load(join('assets', 'images', 'startscreen', 'play.png')).convert_alpha(),
            "setting": pygame.image.load(join('assets', 'images', 'startscreen', 'settings.png')).convert_alpha(),
            "exit": pygame.image.load(join('assets', 'images', 'startscreen', 'exit.png')).convert_alpha(),
            "paused": pygame.image.load(join('assets', 'images', 'startscreen', 'paused.png')).convert_alpha(),
            "gameover": pygame.image.load(join('assets', 'images', 'startscreen', 'game_over.png')).convert_alpha()
            }
        self.map_selection_images = {
            "map": pygame.image.load(join('assets', 'images', 'mapscreen', 'map.png')).convert_alpha(),
            "back": pygame.image.load(join('assets', 'images', 'mapscreen', 'back.png')).convert_alpha(),
            "upgrade": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrade.png')).convert_alpha()}
        self.upgrades_images = {"border": pygame.image.load(join('assets', 'images', 'mapscreen', 'border.png')).convert_alpha(),
                                "upgrade": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'up.png')).convert_alpha(),
                                "downgrade": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'down.png')).convert_alpha(),
                                "archer": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'archer.png')).convert_alpha(),
                                "stone": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'stone.png')).convert_alpha(),
                                "slingshot": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'slingshot.png')).convert_alpha(),
                                "bomb": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrades', 'bomb.png')).convert_alpha()}
        self.map_images = {"map1": pygame.image.load(join('assets', 'images', 'mapscreen', 'map1.png')).convert_alpha(),
                            "map2": pygame.image.load(join('assets', 'images', 'mapscreen', 'map2.png')).convert_alpha()}
        self.settings_images = {"display": pygame.image.load(join('assets', 'images', 'startscreen','settings', 'display.png')).convert_alpha(),
                                "music": pygame.image.load(join('assets', 'images', 'startscreen','settings', 'music.png')).convert_alpha(),
                                "sfx": pygame.image.load(join('assets', 'images', 'startscreen','settings', 'sfx.png')).convert_alpha()
                                }
        self.slider_images = {"handle": pygame.image.load(join('assets', 'images', 'slider','slider_handle.png')).convert_alpha(),
                                "bar": pygame.image.load(join('assets', 'images', 'slider','slider_bar.png')).convert_alpha()}
        self.drop_down_images = {"fullscreen": pygame.image.load(join('assets', 'images', 'startscreen', 'settings', 'fullscreen.png')).convert_alpha(),
                                "1280": pygame.image.load(join('assets', 'images', 'startscreen', 'settings', '1280x720.png')).convert_alpha(),
                                "1600": pygame.image.load(join('assets', 'images', 'startscreen', 'settings', '1600x900.png')).convert_alpha(),
                                "arrow": pygame.image.load(join('assets', 'images', 'startscreen', 'settings', 'arrow.png')).convert_alpha()}
        self.game_icons = {
            "gear": pygame.image.load(join('assets', 'images', 'icon', 'gear.png')).convert_alpha(),
            "pause": pygame.image.load(join('assets', 'images', 'icon', 'pause.png')).convert_alpha(),
            "unpause": pygame.image.load(join('assets', 'images', 'icon', 'unpause.png')).convert_alpha(),
            "2x": pygame.image.load(join('assets', 'images', 'icon', '2x.png')).convert_alpha()
        }

        # font loader
        self.small   = pygame.font.Font("assets/Monocraft.ttc", 12)
        self.title_f = pygame.font.Font("assets/Monocraft.ttc", 14)
        self.title = pygame.font.Font("assets/Monocraft.ttc", 32)

        self.multiplier_labels = {
            "title": self.title_f.render("ACTIVE MULTIPLIERS:", True, (255,255,255)),
            "dmg":   self.small.render("DMG Mult:", True, (255,0,0)),
            "range": self.small.render("Range Mult:", True, (0,255,0)),
            "rate":  self.small.render("Firerate Mult:", True, (0,0,255)),
            "speed": self.small.render("Projectile Spd Mult:", True, (255,0,255)),
        }

        # Archer Tower
        # Tower drag-and-drop
        self.placed_towers = []       # stores all towers placed
        self.selected_tower = None    # currently selected tower
        self.dragging_tower = None
         # --- Initialize wave control variables ---
        self.wave_in_progress = False
        self.countdown_active = False
        self.wave_timer = None
        self.countdown = 0  
        #Money
        self.money_system = MoneySystem(starting_money=500)

        # load tower stats and upgrades
        self.load_towers_from_json()
        self.load_permanent_upgrades()

        self.start_screen()  # make sure setup is called after
        self.start_bgmusic.play(loops=-1)
        # Setup game map, sprites, castles, monsters

    # ----------------------------------------------
    # SAVE AND LOAD FUNCTIONS
    # ----------------------------------------------
    def load_image(self, path):
        return pygame.image.load(path).convert_alpha()

    def load_towers_from_json(self):
        json_path = "assets/data/upgrades/towers.json"

        with open(json_path, "r") as f:
            data = json.load(f)
        
        self.tower_menu = []

        menu_start_x = 30
        menu_start_y = self.GAME_HEIGHT - 90   # higher so panel is smaller

        slot_w, slot_h = 70, 70   # SHRUNK
        gap = 25                 # SHRUNK spacing

        slot_index = 0

        for tower_name, tdata in list(data.items())[:4]:

            x = menu_start_x + slot_index * (slot_w + gap)
            y = menu_start_y

            rect = pygame.Rect(x, y, slot_w, slot_h)

            folder = "assets/data/graphics/" + tdata["folder"]
            idle = self.load_image(f"{folder}/{tdata['idle']}")
            icon = pygame.transform.scale(self.load_image("assets/images/mapscreen/" + tdata["icon"]), (slot_w, slot_h))
            build_frames = [self.load_image(f"{folder}/{img}") for img in tdata["build"]]
            upgrade_frames = [self.load_image(f"{folder}/{img}") for img in tdata["upgrades"]]
            projectile = self.load_image("assets/data/graphics/" + tdata["projectile"])

            self.tower_menu.append({
                "name": tower_name,
                "rect": rect,
                "class": Tower,
                "icon": icon,
                "idle": idle,
                "building_frames": build_frames,
                "upgrade_images": upgrade_frames,
                "damage": tdata["damage"],
                "range": tdata["range"],
                "fire_rate": tdata["fire_rate"],
                "projectile_image": projectile,
                "projectile_speed": tdata["projectile_speed"],
                "size": tuple(tdata["size"]),
                "sound": tdata.get("sound")  # ✅ add sound path from JSON
            })

            slot_index += 1

    def load_permanent_upgrades(self):
        path = "assets/data/upgrades/permanent_upgrades.json"
        try:
            with open(path, "r") as f:
                self.permanent_upgrades = json.load(f)
        except FileNotFoundError:
            print("WARNING: permanent_upgrades.json not found!")
            self.permanent_upgrades = {}

    def save_permanent_upgrades(self):
        path = "assets/data/upgrades/permanent_upgrades.json"
        with open(path, "w") as f:
            json.dump(self.permanent_upgrades, f, indent=4)
        print("Permanent upgrades saved!")

    def save_settings(self):
        data = {
            "music": self.slider_music.get_value(),
            "sfx": self.slider_sfx.get_value(),
            "resolution": self.current_resolution
        }
        with open("assets/data/settings.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_display_settings(self):
        try:
            with open("assets/data/settings.json", "r") as f:
                data = json.load(f)
                return data
        except:
            return {"resolution": "1280x720"}

    def load_audio_settings(self):
        try:
            with open("assets/data/settings.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # File missing → create defaults
            data = {
                "music": 50,
                "sfx": 50,
                "resolution": "1280x720"
            }
            with open("settings.json", "w") as f:
                json.dump(data, f, indent=4)

        # Apply to sliders if they exist
        if hasattr(self, "slider_music") and self.slider_music:
            self.slider_music.set_value(data.get("music", 50))
        if hasattr(self, "slider_sfx") and self.slider_sfx:
            self.slider_sfx.set_value(data.get("sfx", 50))

        # Apply resolution too
        self.current_resolution = data.get("resolution", "1280x720")

        # Apply loaded values (with safe fallback)
        self.music_volume = data.get("music", 1.0)
        self.sfx_volume = data.get("sfx", 1.0)
        self.current_resolution = data.get("resolution", "1280x720")
    
    def apply_saved_resolution(self):
        if self.current_resolution == "fullscreen":
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        elif self.current_resolution == "1600x900":
            self.screen = pygame.display.set_mode((1600, 900))

        else:  # default 1280x720
            self.screen = pygame.display.set_mode((1280, 720))

    # -----------------------------------------------
    # Start screen UI
    # -----------------------------------------------
    def start_screen(self):
        if not hasattr(self, "settings_ui_created"):
            self.settings_ui_created = False
        self.show_start = True
        if not hasattr(self, "start_screen_bg"):
            self.start_screen_bg = UserInterface("startscreen", (0, 0), self.startscreen_images["start"], (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, None)

        # Clouds background
        if not hasattr(self, "cloud"):
            for cloud in range(5):
                self.cloud = UserInterface("cloud",(randint(-100, self.GAME_WIDTH), randint(0, self.GAME_HEIGHT // 2 - 200)),pygame.image.load(join('assets', 'images', 'startscreen', 'clouds', f'cloud{randint(1, 4)}.png')).convert_alpha(),(300, 80),self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, None)
                self.start_ui.append(self.cloud)

        if not hasattr(self, "logo"):
            self.logo = UserInterface("logo", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 250), self.startscreen_images["logo"], (417, 146), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
            self.start_ui.append(self.logo)
        
        self.play_button = UserInterface("play", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 100), self.startscreen_images["play"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.settings_button = UserInterface("settings", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2), self.startscreen_images["setting"], (254, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.exit_button = UserInterface("exit", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 + 100), self.startscreen_images["exit"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        for ui in (self.play_button, self.settings_button, self.exit_button):
            self.start_ui.append(ui)

        if not self.settings_ui_created:    
            self.settings_ui_surface = UserInterface("ui_bg", (-self.GAME_WIDTH, self.GAME_HEIGHT // 2), pygame.image.load(join('assets', 'images', 'grybg.png')).convert_alpha(), (self.GAME_WIDTH, self.GAME_HEIGHT), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, None)
            self.settings_ui_surface.set_opacity(200) 
            self.settings_ui_back_btn = UserInterface("play_back_btn", (-self.GAME_WIDTH + 60, 20), self.map_selection_images["back"], (139, 58), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

            # settings
            self.settings_ui_display = UserInterface("ui_display", (-self.GAME_WIDTH, 150), self.settings_images["display"], (254, 68), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
            self.settings_ui_music = UserInterface("ui_music", (-self.GAME_WIDTH, 570), self.settings_images["music"], (200, 65), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
            self.settings_ui_sfx = UserInterface("ui_sfx", (-self.GAME_WIDTH, 670), self.settings_images["sfx"], (150, 65), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
            self.quit = UserInterface("quit", (-self.GAME_WIDTH, 670), self.startscreen_images["exit"], (139, 58), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

            self.slider_music = Slider("slider_music", (-self.GAME_WIDTH // 2 + 300, 470), bar_surface=self.slider_images["bar"], bar_scale=(600, 40), handle_surface=self.slider_images["handle"], handle_scale=(45, 45), ui_group=self.settings_sprites, min_value=0, max_value=100, default_value=50, game_width=self.GAME_WIDTH, game_height=self.GAME_HEIGHT, hover_sfx=self.hover_sfx)
            self.slider_sfx = Slider("slider_sfx", (-self.GAME_WIDTH // 2 + 300, 570), bar_surface=self.slider_images["bar"], bar_scale=(600, 40), handle_surface=self.slider_images["handle"], handle_scale=(45, 45), ui_group=self.settings_sprites, min_value=0, max_value=100, default_value=50, game_width=self.GAME_WIDTH, game_height=self.GAME_HEIGHT, hover_sfx=self.hover_sfx)
             
            self.settings = self.load_display_settings()
            self.current_resolution = self.settings["resolution"]

            self.res_image_map = {
                                    "fullscreen": self.drop_down_images["fullscreen"],
                                    "1280x720": self.drop_down_images["1280"],
                                    "1600x900": self.drop_down_images["1600"]
                                }

            self.resolution_dropdown = Dropdown("resolution_dd", (-self.GAME_WIDTH//2 + 300, 200), self.res_image_map[self.current_resolution], (401, 75), self.settings_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
            self.resolution_dropdown.add_option("fullscreen", self.drop_down_images["fullscreen"], (401,75), offset_y=80, hover_sfx=self.hover_sfx)
            self.resolution_dropdown.add_option("1280x720", self.drop_down_images["1280"], (401,75), offset_y=160, hover_sfx=self.hover_sfx)
            self.resolution_dropdown.add_option("1600x900", self.drop_down_images["1600"], (401,75), offset_y=240, hover_sfx=self.hover_sfx)

            for ui in (self.settings_ui_surface, self.settings_ui_back_btn, self.settings_ui_display, self.settings_ui_music, self.settings_ui_sfx, self.resolution_dropdown):
                self.settings_ui.append(ui)

            self.load_audio_settings()

            self.settings_ui_created = True
    # -----------------------------------------------
    # Map selection screen
    # -----------------------------------------------
    def map_selection(self):
        self.show_map = True
        self.map_selected = False

        self.map_button = UserInterface("map", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 100), self.map_selection_images["map"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.upgrades_button = UserInterface("upgrades", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2), self.map_selection_images["upgrade"], (265, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.back_button = UserInterface("back", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 + 100), self.map_selection_images["back"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        for ui in (self.map_button, self.upgrades_button, self.back_button):
            self.map_ui.append(ui)

        self.map_ui_surface = UserInterface("ui_bg", (-self.GAME_WIDTH, self.GAME_HEIGHT // 2), pygame.image.load(join('assets', 'images', 'grybg.png')).convert_alpha(), (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, None)
        self.map_ui_surface.set_opacity(200)  # Slightly transparent (0-255, 255 is fully opaque)
        self.map_ui_back_btn = UserInterface("ui_back_btn", (-self.GAME_WIDTH + 60, 0 + 60), self.map_selection_images["back"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.map_ui_play_btn = UserInterface("ui_play_btn", (-self.GAME_WIDTH, self.GAME_HEIGHT - 200), self.startscreen_images["play"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        
        self.map_ui_map_1 = UserInterface("map_1", (-self.GAME_WIDTH // 2 - 150, 150), self.map_images["map1"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.map_ui_map_2 = UserInterface("map_2", (-self.GAME_WIDTH // 2 + 150, 150), self.map_images["map2"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        self.map_ui_play_btn.set_dimmed(True)

        for ui in (self.map_ui_surface, self.map_ui_back_btn, self.map_ui_play_btn, self.map_ui_map_1, self.map_ui_map_2):
            self.map_selection_ui.append(ui)

        self.towers = None
        self.archer_tower_upg = UserInterface("archer_tower", (-self.GAME_WIDTH // 2 - 450, 150), self.upgrades_images["archer"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.upgrade_btn_archer, self.downgrade_btn_archer = self.create_bottom_buttons(self.archer_tower_upg, "archer_tower")
        self.downgrade_btn_archer.attach(parent=self.archer_tower_upg, offset_x=40, offset_y=self.archer_tower_upg.rect.height + 40)
        self.upgrade_btn_archer.attach(parent=self.archer_tower_upg, offset_x=self.archer_tower_upg.rect.width - 80, offset_y=self.archer_tower_upg.rect.height + 40)

        self.stone_tower_upg = UserInterface("stone_tower", (-self.GAME_WIDTH // 2 - 200, 150), self.upgrades_images["stone"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.upgrade_btn_stone, self.downgrade_btn_stone = self.create_bottom_buttons(self.stone_tower_upg, "stone_tower")
        self.downgrade_btn_stone.attach(parent=self.stone_tower_upg, offset_x=40, offset_y=self.stone_tower_upg.rect.height + 40)
        self.upgrade_btn_stone.attach(parent=self.stone_tower_upg, offset_x=self.stone_tower_upg.rect.width - 80, offset_y=self.archer_tower_upg.rect.height + 40)

        self.sling_shot_tower_upg = UserInterface("slingshot_tower", (-self.GAME_WIDTH // 2 + 50, 150), self.upgrades_images["slingshot"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.upgrade_btn_slingshot, self.downgrade_btn_slingshot = self.create_bottom_buttons(self.sling_shot_tower_upg, "slingshot_tower")
        self.downgrade_btn_slingshot.attach(parent=self.sling_shot_tower_upg, offset_x=40, offset_y=self.sling_shot_tower_upg.rect.height + 40)
        self.upgrade_btn_slingshot.attach(parent=self.sling_shot_tower_upg, offset_x=self.sling_shot_tower_upg.rect.width - 80, offset_y=self.archer_tower_upg.rect.height + 40)

        self.bomb_tower_upg = UserInterface("bomb_tower", (-self.GAME_WIDTH // 2 + 300, 150), self.upgrades_images["bomb"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.upgrade_btn_bomb, self.downgrade_btn_bomb = self.create_bottom_buttons(self.bomb_tower_upg, "bomb_tower")
        self.downgrade_btn_bomb.attach(parent=self.bomb_tower_upg, offset_x=40, offset_y=self.bomb_tower_upg.rect.height + 40)
        self.upgrade_btn_bomb.attach(parent=self.bomb_tower_upg, offset_x=self.bomb_tower_upg.rect.width - 80, offset_y=self.archer_tower_upg.rect.height + 40)

        for ui in (self.archer_tower_upg, self.stone_tower_upg, self.sling_shot_tower_upg, self.bomb_tower_upg, self.upgrade_btn_archer, self.downgrade_btn_archer, self.upgrade_btn_stone, self.downgrade_btn_stone, self.upgrade_btn_slingshot, self.downgrade_btn_slingshot, self.upgrade_btn_bomb, self.downgrade_btn_bomb):
            self.upgrade_ui.append(ui)

    def create_bottom_buttons(self, parent_ui, name_prefix, x_offset=0):
        """Create upgrade & downgrade buttons under a UI element."""
        px, py = parent_ui.rect.topleft
        w, h = parent_ui.rect.size

        button_y = py + h + 40  # position near bottom

        upgrade_btn = UserInterface(
            f"{name_prefix}_upgrade",
            (px + 100 + x_offset, button_y),
            self.upgrades_images["upgrade"],
            (40, 40),
            self.ui_sprites,
            self.GAME_WIDTH,
            self.GAME_HEIGHT,
            self.hover_sfx
        )

        downgrade_btn = UserInterface(
            f"{name_prefix}_downgrade",
            (px + w - 80 + x_offset, button_y),
            self.upgrades_images["downgrade"],
            (40, 40),
            self.ui_sprites,
            self.GAME_WIDTH,
            self.GAME_HEIGHT,
            self.hover_sfx
        )

        return upgrade_btn, downgrade_btn

    def handle_upgrade_button(self, ui_name: str):
        parts = ui_name.split("_")
        if len(parts) < 3:
            return  # Not an upgrade/downgrade button

        tower_name = "_".join(parts[:2])   # 'archer_tower'
        action = parts[2]                  # 'upgrade' or 'downgrade'

        if tower_name not in self.permanent_upgrades:
            return

        cost = self.upgrade_cost.get(tower_name, 1)

        # --- REQUIRE STAT POINTS ONLY FOR UPGRADE ---
        if action == "upgrade":
            if self.exp_system.stat_points < cost:
                print("[UPGRADE] Not enough stat points!")
                return
            else:
                self.exp_system.stat_points -= cost
                print(f"[UPGRADE] {tower_name} upgraded! SP left: {self.exp_system.stat_points}")
                

        # Define stat changes
        UPGRADE = {
            "damage_mult": 0.10,
            "range_mult": 0.05,
            "fire_rate_mult": -0.05,
            "projectile_speed_mult": 0.10
        }

        DOWNGRADE = {
            "damage_mult": -0.10,
            "range_mult": -0.05,
            "fire_rate_mult": 0.05,
            "projectile_speed_mult": -0.10
        }

        if action == "upgrade":
            vals = UPGRADE
            if self.exp_system.stat_points < cost:
                print("[UPGRADE] Not enough stat points!")
                return

            self.exp_system.stat_points -= cost
            self.exp_system.save_progress()
        elif action == "downgrade":
            vals = DOWNGRADE
        else:
            return

        tower = self.permanent_upgrades[tower_name]

        tower["damage_mult"] += vals["damage_mult"]
        tower["damage_mult"] = max(1.0, tower["damage_mult"])

        tower["range_mult"] += vals["range_mult"]
        tower["range_mult"] = max(1.0, min(tower["range_mult"], 2.0))

        tower["fire_rate_mult"] += vals["fire_rate_mult"]
        tower["fire_rate_mult"] = max(0.75, min(tower["fire_rate_mult"], 1.0))

        tower["projectile_speed_mult"] += vals["projectile_speed_mult"]
        tower["projectile_speed_mult"] = max(1.0, min(tower["projectile_speed_mult"], 1.75))

        self.save_permanent_upgrades()

    def draw_tower_multipliers(self, surface, parent_ui, tower_name):

        # Animated rect position (follows movement)
        small = self.small
        title = self.title_f

        x = parent_ui.rect.x
        y = parent_ui.rect.y

        xpos = x + 5
        ypos = y + parent_ui.rect.height + 90

        stats = self.permanent_upgrades.get(tower_name, None)
        if stats is None:
            return

        # HEADER
        surface.blit(self.multiplier_labels["title"], (xpos, ypos))
        ypos += 25

        def draw_value(value, limit=None):
            color = (255, 255, 255)
            text = f"{value:.2f}"
            if limit is not None and abs(value - limit) < 0.001:  # reached max
                text += "  (MAXED)"
                color = (255,255,0)
            return small.render(text, True, color)
        # Dynamic values
        # --- DMG
        surface.blit(self.multiplier_labels["dmg"], (xpos, ypos))
        surface.blit(small.render(f"{stats['damage_mult']:.2f}", True, (255,255,255)), 
                    (xpos + 165, ypos))
        ypos += 18

        # --- Range
        surface.blit(self.multiplier_labels["range"], (xpos, ypos))
        surface.blit(draw_value(stats["range_mult"], limit=2.0),
                    (xpos + 165, ypos))
        ypos += 18

        # --- Fire rate
        surface.blit(self.multiplier_labels["rate"], (xpos, ypos))
        surface.blit(draw_value(stats["fire_rate_mult"], limit=0.75),
                    (xpos + 165, ypos))
        ypos += 18

        # --- Projectile Speed
        surface.blit(self.multiplier_labels["speed"], (xpos, ypos))
        surface.blit(draw_value(stats["projectile_speed_mult"], limit=1.75),
                    (xpos + 165, ypos))

        if self.show_upgrades:
            sp_text = self.title.render(f"Stat Points: {self.exp_system.stat_points}", True, (255, 255, 255))
            surface.blit(sp_text, (self.GAME_WIDTH//2 - 100, 60))

    # -----------------------------------------------
    # Setup map, sprites, castles, monsters
    # -----------------------------------------------
    def setup(self):
        self.pause_text = UserInterface("pText", (self.GAME_WIDTH // 2, -self.GAME_HEIGHT), self.startscreen_images["paused"], (254, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        
        self.inGame = True
        self.grass_tiles = []  # initialize here
        tmx_data = load_pygame(join('assets', 'data', 'tmx', 'finals.tmx'))

        # Ground tiles
        ground_layer = tmx_data.get_layer_by_name("Ground")
        for x, y, image in ground_layer.tiles():
            Sprites((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            
            tile_gid = ground_layer.data[y][x]  # get the GID for this tile
            tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            self.grass_tiles.append({"rect": tile_rect, "id": tile_gid})

        # Castles
        self.castles = pygame.sprite.Group()
        castle_layer = tmx_data.get_layer_by_name("castle")
        for obj in castle_layer:
            if hasattr(obj, "image") and obj.image is not None:
                castle = CastleBox((obj.x, obj.y), obj.width, obj.height, self.all_sprites, image=obj.image, game=self)
                self.all_sprites.add(castle)
                self.castles.add(castle)
                if obj.properties.get("hp_castle", False):
                    castle.has_hp = True


        # Other layers
        for layer_name in ["House", "decoration", "fences"]:
            for obj in tmx_data.get_layer_by_name(layer_name):
                Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation, self.all_sprites)

        self.waypoints  = [(wp.x, wp.y) for wp in tmx_data.get_layer_by_name("Waypoints1")]
        self.waypoints2 = [(wp.x, wp.y) for wp in tmx_data.get_layer_by_name("Waypoints2")]

        # Store them as a list of possible path options
        self.all_paths = [self.waypoints, self.waypoints2]
        self.wave_director = WaveDirector(self.spawn_enemy, self.all_paths, self.GAME_WIDTH, self.GAME_HEIGHT)

        # Reset wave director every game
        self.wave_director.ai.wave_number = 1
        self.wave_director.ai.last_wave_time = 0
        self.wave_director.current_wave = []
        self.wave_director.enemies_spawned = 0

        self.path_rects = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.waypoints]
        self.create_middle_hud_icons()

    def spawn_enemy(self, enemy_type, waypoints, wave_number):
        """Spawns a monster based on its type with correct sprite and stats."""

        # Get stats for this enemy type
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["grunt"])

        # Create the Monster (animations & speed are handled inside)
        monster = Monster(
            enemy_type=enemy_type,
            waypoints=waypoints,
            group=self.all_sprites,
            wave_number=wave_number,
            money_system=self.money_system  # <-- pass money system here
        )

        #debugger
        #base_hp = ENEMY_TYPES[enemy_type]["hp"]
        #print(
        #    f"DEBUG -> {enemy_type}: base={base_hp}, scaled={monster.hp}, "
        #    f"wave={wave_number}, growth_rate used={self.growth_rate if hasattr(self,'growth_rate') else 'internal'}"
        #)

        # Add to monster group
        self.monsters.add(monster)

    def can_place_tower(self, pos, tower_size=(64,64)):
        px, py = pos
        w, h = tower_size

        tower_rect = pygame.Rect(px - w//2, py - h, w, h)   # bottom-center placement

        # Check if all corners are on valid grass tiles
        corners = [
            (tower_rect.left, tower_rect.top),
            (tower_rect.right, tower_rect.top),
            (tower_rect.left, tower_rect.bottom),
            (tower_rect.right, tower_rect.bottom),
            (tower_rect.centerx, tower_rect.bottom),
        ]

        valid_tile = False
        for tile in self.grass_tiles:
            if tile["id"] == 1:  # grass tile
                for c in corners:
                    if tile["rect"].collidepoint(c):
                        valid_tile = True
                        break
            if valid_tile:
                break

        if not valid_tile:
            return False

        # Check tower overlap
        for t in self.placed_towers:
            if tower_rect.colliderect(t.rect):
                return False

        return True

    def draw_tower_ui(self, surface):
        """
        Draw tower selection UI: upgrade/delete buttons and range indicator.
        Should be called each frame for all placed towers.
        """
        for tower in self.placed_towers:
            tower.draw_selection(surface)

            if tower == self.selected_tower:

                # --- Range Indicator ---
                if hasattr(tower, "range"):
                    overlay = pygame.Surface((tower.range * 2, tower.range * 2), pygame.SRCALPHA)
                    pygame.draw.circle(overlay, (0, 255, 0, 80), (tower.range, tower.range), tower.range)
                    pygame.draw.circle(overlay, (0, 255, 0), (tower.range, tower.range), tower.range, 2)
                    surface.blit(overlay, (tower.rect.centerx - tower.range, tower.rect.centery - tower.range))

                # Medieval Colors
                BROWN = (139, 69, 19)
                DARK_BROWN = (100, 50, 15)
                TEXT_COLOR = (240, 220, 180)
                GOLD = (212, 175, 55)

                font = pygame.font.Font("assets/Monocraft.ttc", 12)   

                # Always draw delete button
                tower.delete_button = pygame.Rect(tower.rect.right + 10, tower.rect.top, 80, 32)

                # Draw DELETE
                pygame.draw.rect(surface, BROWN, tower.delete_button, border_radius=6)
                pygame.draw.rect(surface, DARK_BROWN, tower.delete_button, 2, border_radius=6)

                delete_text = font.render("DELETE", True, TEXT_COLOR)
                surface.blit(delete_text, (
                    tower.delete_button.centerx - delete_text.get_width() // 2,
                    tower.delete_button.centery - delete_text.get_height() // 2
                ))

                # --- Upgrade button only if tower can still upgrade ---
                if tower.level < 3:
                    tower.upgrade_button = pygame.Rect(tower.rect.right + 10, tower.rect.top + 40, 80, 32)

                    # Draw UPGRADE button
                    pygame.draw.rect(surface, BROWN, tower.upgrade_button, border_radius=6)
                    pygame.draw.rect(surface, DARK_BROWN, tower.upgrade_button, 2, border_radius=6)

                    upgrade_text = font.render("UPGRADE", True, TEXT_COLOR)
                    surface.blit(upgrade_text, (
                        tower.upgrade_button.centerx - upgrade_text.get_width() // 2,
                        tower.upgrade_button.centery - upgrade_text.get_height() // 2
                    ))

                else:
                    # When maxed: remove upgrade button
                    tower.upgrade_button = None

                    # Show MAX label
                    # MAX badge rect
                    max_rect = pygame.Rect(tower.rect.right + 10, tower.rect.top + 40, 80, 32)

                    # Draw MAX background (same as upgrade button style)
                    pygame.draw.rect(surface, BROWN, max_rect, border_radius=6)
                    pygame.draw.rect(surface, DARK_BROWN, max_rect, 2, border_radius=6)

                    # Draw MAX text
                    max_text = font.render("MAX", True, GOLD)
                    surface.blit(max_text, (
                        max_rect.centerx - max_text.get_width() // 2,
                        max_rect.centery - max_text.get_height() // 2
                    ))

                # --- Level Banner (always shown) ---
                banner = pygame.Rect(
                    tower.rect.right + 10,
                    tower.rect.top + 80,
                    80, 28
                )

                pygame.draw.rect(surface, GOLD, banner, border_radius=4)
                pygame.draw.rect(surface, DARK_BROWN, banner, 2, border_radius=4)

                level_text = font.render(f"Lvl {tower.level}", True, (50, 30, 10))
                surface.blit(level_text, (
                    banner.centerx - level_text.get_width() // 2,
                    banner.centery - level_text.get_height() // 2
                ))

            else:
                tower.delete_button = None
                tower.upgrade_button = None

    def get_icon_surface(self, name):
        if name == "pause_toggle":
            return self.game_icons["pause"]     # default
        else:
            return self.game_icons[name]
    
    def draw_middle_hud(self, surface):
        panel_h = 125
        panel_y = self.GAME_HEIGHT - panel_h
        panel_w = 380
        panel_x = (self.GAME_WIDTH // 2) - (panel_w // 2)

        # icon sizes
        icon_w = 64
        icon_h = 64

        # Icon order on HUD
        names = ["gear", "pause_toggle", "2x"]

        # Spacing formula
        icon_count = 3
        total_icons_width = icon_count * icon_w
        total_spacing = panel_w - total_icons_width
        spacing = total_spacing // (icon_count + 1)

        # X/Y base for all icons
        x = panel_x + spacing + icon_w // 2
        y = panel_y + panel_h // 2

        self.hud_icons = {}

        for name in names:
            ui = UserInterface(
                name=name,
                pos=(x, y),
                surface=self.get_icon_surface(name),   # <— conversion from name → surface
                scale=(icon_w, icon_h),
                group=self.ui_sprites,
                game_width=self.GAME_WIDTH,
                game_height=self.GAME_HEIGHT
            )
            self.hud_icons[name] = ui

            x += icon_w + spacing
            
    def create_middle_hud_icons(self):
        panel_h = 125
        panel_w = 380
        panel_x = (self.GAME_WIDTH // 2) - (panel_w // 2)
        panel_y = self.GAME_HEIGHT - panel_h

        icon_w = 64
        icon_h = 64
        names = ["gear", "pause_toggle", "2x"]

        icon_count = len(names)
        total_icons_width = icon_count * icon_w
        total_spacing = panel_w - total_icons_width
        spacing = total_spacing // (icon_count + 1)

        x = panel_x + spacing + icon_w // 2
        y = panel_y + panel_h // 2

        self.hud_icons = {}

        for name in names:
            self.ui = UserInterface(
                name=name,
                pos=(x, y),
                surface=self.get_icon_surface(name),
                scale=(icon_w, icon_h),
                group=self.ui_sprites,
                game_width=self.GAME_WIDTH,
                game_height=self.GAME_HEIGHT,
                hover_sfx=self.hover_sfx
            )

            self.hud_icons[name] = self.ui
            x += icon_w + spacing

    def draw_right_hud(self, surface):
        # Right panel matches height of left panel
        panel_h = 125
        panel_y = self.GAME_HEIGHT - panel_h - 0
        panel_w = 380
        panel_x = self.GAME_WIDTH - panel_w - 20

        pygame.draw.rect(surface, (60,40,30),
                        (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(surface, (100,80,60),
                        (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

        small = pygame.font.Font("assets/Monocraft.ttc", 12)
        title_f = pygame.font.Font("assets/Monocraft.ttc", 14)

        xpos = panel_x + 15
        ypos = panel_y + 5

        # =====================
        # CASTLE HP
        # =====================
        surface.blit(title_f.render("CASTLE Health", True, (255,255,255)), (xpos, ypos))
        ypos += 25

        # load hp
        castle = self.main_castle
        if castle is None:
            hp = max_hp = 100
        else:
            hp = castle.hp
            max_hp = castle.max_hp

        # small HP bar
        bar_w = 150
        bar_h = 14
        pygame.draw.rect(surface, (40,25,20), (xpos, ypos, bar_w, bar_h), border_radius=4)
        fill = max(0, (hp / max_hp) * bar_w)
        pygame.draw.rect(surface, (50,200,60), (xpos, ypos, fill, bar_h), border_radius=4)

        # hp text
        surface.blit(small.render(f"{hp}/{max_hp}", True, (255,255,255)),
                    (xpos + bar_w + 10, ypos))

        ypos += 25

        # =====================
        # OTHER STATS
        # =====================

        surface.blit(small.render(f"MONEY : {self.money_system.money}", True, (255,255,0)),
                    (xpos, ypos))
        ypos += 18

        surface.blit(small.render(f"WAVE  : {self.wave_director.ai.wave_number - 1}", True, (255,255,255)),
                    (xpos, ypos))
        ypos += 18

        if hasattr(self.wave_director.ai, "formatted_time"):
            time_str = self.wave_director.ai.formatted_time
        else:
            time_str = "00:00"

        surface.blit(small.render(f"TIME  : {time_str}", True, (255,255,255)),
                    (xpos, ypos))
        ypos += 18

        cas = getattr(self.wave_director.ai, "casualties", 0)
        surface.blit(small.render(f"KILLS : {cas}", True, (255,120,120)),
                    (xpos, ypos))
    
    def toggle_pause(self, ui):
        self.paused = not self.paused

        # Scale icons to the UI size
        self.pause_icon_scaled    = pygame.transform.scale(self.game_icons["pause"], ui.base_size)
        self.unpause_icon_scaled  = pygame.transform.scale(self.game_icons["unpause"], ui.base_size)
                
        if self.paused:
            ui.base_image = self.unpause_icon_scaled
            self.pause_text.move_to()
        else:
            ui.base_image = self.pause_icon_scaled
            self.pause_text.move_away()

        ui.image = ui.base_image

    def trigger_game_over(self):

        self.game_over = True
        self.paused = True # freeze gameplay

        wave_count = self.wave_director.ai.wave_number - 1  

            # Your EXP formula inputs
        base_exp = self.base_exp            # you define this
        multiplier = self.exp_multiplier    # you define this
    
        gained_exp = self.exp_system.grant_wave_exp(
            base_exp=base_exp,
            wave_count=wave_count,
            multiplier=multiplier
        )


        # Create UI element off-screen with slide animation
        self.gameover_ui = UserInterface(
            "gameover",
            pos=(self.GAME_WIDTH // 2, -300),  # start off-screen (top)
            surface=self.startscreen_images["gameover"],
            scale=(600, 150),  # or whatever size fits your image
            group=self.ui_sprites,
            game_width=self.GAME_WIDTH,
            game_height=self.GAME_HEIGHT,
            hover_sfx=None
        )

        font = pygame.font.Font("assets/Monocraft.ttc", 50)  # choose your font/size
        exp_text_str = f"EXP GAINED: {gained_exp}"

        self.exp_text_surface = font.render(exp_text_str, True, (255, 215, 0))  # gold yellow
        self.exp_text_rect = self.exp_text_surface.get_rect()

        # Position: centered horizontally, below the Game Over UI
        self.exp_text_rect.centerx = self.GAME_WIDTH // 2
        self.exp_text_rect.top = self.gameover_ui.rect.bottom + 20

        self.gameover_ui.move_to()
        self.gameover_sfx.play()
        print("GAME OVER")

    def reset_game(self):
        """Full game reset: clears gameplay state and returns to start screen."""
        print("RESETTING GAME...")

        # --- Reset flags ---
        self.game_over = False
        self.inGame = False
        self.paused = False
        self.fast_forward = False
        self.time_scale = 1.0
        self.main_castle = None

        # --- Clear all sprite groups ---
        self.all_sprites.empty()
        self.ui_sprites.empty()
        self.settings_sprites.empty()
        self.castles.empty()
        self.monsters.empty()

        # --- Clear tower-related data ---
        self.placed_towers.clear()
        self.selected_tower = None
        self.dragging_tower = None

        ATTRS_TO_DELETE = [
            "start_screen_bg",
            "cloud",
            "logo",
            "settings_ui_surface",
            "settings_ui_back_btn",
            "settings_ui_display",
            "settings_ui_music",
            "settings_ui_sfx",
            "slider_music",
            "slider_sfx",
            "resolution_dropdown",
            "settings_ui_created",
        ]

        for attr in ATTRS_TO_DELETE:
            if hasattr(self, attr):
                delattr(self, attr)

        # --- Map & upgrade UI UI objects should be rebuilt ---
        for attr in [
            "map_button", "upgrades_button", "back_button",
            "map_ui_surface", "map_ui_back_btn", "map_ui_play_btn",
            "map_ui_map_1", "map_ui_map_2",
            "archer_tower_upg", "stone_tower_upg",
            "sling_shot_tower_upg", "bomb_tower_upg",
        ]:
            if hasattr(self, attr):
                delattr(self, attr)


        # --- Stop game BGM & restart start screen BGM ---
        self.game_bgmusic.stop()
        self.start_bgmusic.play(loops=-1)

        # --- Restore start UI ---
        self.start_ui.clear()
        self.map_ui.clear()
        self.map_selection_ui.clear()
        self.upgrade_ui.clear()

        self.start_screen()

    def confirmation(self, message="Are you sure?"):
        """
        HUD-styled confirmation dialog.
        ESC = cancel, SPACE = confirm.
        Blocks the game until the user decides.
        Returns True (confirm) or False (cancel)
        """

        # ----------- Colors (from your HUD screenshot) -----------
        PANEL_BG     = (71, 42, 26)
        PANEL_BORDER = (44, 28, 19)
        PANEL_SHADOW = (0, 0, 0, 120)

        # ----------- Fonts -----------
        title_font = pygame.font.Font("assets/Monocraft-Bold.ttf", 32)
        sub_font   = pygame.font.Font("assets/Monocraft-Bold.ttf", 20)

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

        box_x = (self.GAME_WIDTH - box_w) // 2
        box_y = (self.GAME_HEIGHT - box_h) // 2
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
            dark = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 160))
            self.game_surface.blit(dark, (0, 0))

            # ----------- Draw shadow -----------
            shadow = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            shadow.fill(PANEL_SHADOW)
            self.game_surface.blit(shadow, (box_x, box_y + 4))

            # ----------- Draw Panel -----------
            pygame.draw.rect(self.game_surface, PANEL_BG, box_rect, border_radius=12)
            pygame.draw.rect(self.game_surface, PANEL_BORDER, box_rect, 3, border_radius=12)

            # ----------- Draw Text (centered) -----------
            cx = box_rect.centerx
            y = box_rect.y + padding

            self.game_surface.blit(title_surf, (cx - title_surf.get_width() // 2, y))
            y += title_surf.get_height() + spacing

            self.game_surface.blit(esc_surf, (cx - esc_surf.get_width() // 2, y))
            y += esc_surf.get_height() + spacing

            self.game_surface.blit(space_surf, (cx - space_surf.get_width() // 2, y))

            # ----------- Apply scaling before showing ----------- 
            window_w, window_h = self.screen.get_size()
            scaled = pygame.transform.smoothscale(self.game_surface, (window_w, window_h))
            self.screen.blit(scaled, (0, 0))
            pygame.display.update()

    # -----------------------------------------------
    # Main game loop
    # -----------------------------------------------
    def run(self):
        while self.running:
            dt = (self.clock.tick(60) / 1000) * self.time_scale
            window_w, window_h = self.screen.get_size()
            scale_x = window_w / self.GAME_WIDTH
            scale_y = window_h / self.GAME_HEIGHT
            offset_x, offset_y = 0, 0

            # Convert mouse to game coordinates
            mx, my = pygame.mouse.get_pos()
            gx = (mx - offset_x) / scale_x
            gy = (my - offset_y) / scale_y
            game_mouse = (gx, gy)

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
                    
                    if self.game_over:
                        self.reset_game()
                        continue
                    
                    if event.key == pygame.K_SPACE:
                        self.wave_director.force_next_wave = True
                    
                    if event.key == pygame.K_ESCAPE:
                        self.toggle_pause(self.hud_icons["pause_toggle"])
                        

                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # --- Mouse Input ---
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.inGame and not self.paused:
                        if self.dragging_tower:
                            px, py = self.dragging_tower.rect.center
                            # Check if tower can be placed
                            if self.can_place_tower((px, py), self.dragging_tower.rect.size):
                                # Try spending money
                                if self.money_system.on_tower_placed():
                                    self.all_sprites.add(self.dragging_tower)
                                    self.placed_towers.append(self.dragging_tower)
                                    print(f"{self.dragging_tower} placed!")
                                else:
                                    print("Not enough money to place this tower!")
                            else:
                                print("Cannot place tower here!")
                            # Clear dragging tower regardless of placement
                            self.dragging_tower = None

                        # 2️⃣ Tower menu click → start dragging
                        for tower_btn in self.tower_menu:
                            if tower_btn["rect"].collidepoint(game_mouse):
                                self.dragging_tower = Tower(
                                (gx, gy),
                                [tower_btn["idle"]],
                                tower_btn["building_frames"],
                                tower_btn["upgrade_images"],
                                damage=tower_btn.get("damage", 10),
                                range_=tower_btn.get("range", 100),
                                fire_rate=tower_btn.get("fire_rate", 1.0),
                                projectile_image=tower_btn.get("projectile_image"),
                                projectile_speed=tower_btn.get("projectile_speed", 300),
                                size=tower_btn.get("size", (64, 64)),
                                money_system=self.money_system,  # pass reference
                                tower_type=tower_btn["name"].lower().replace(" ", "_"),
                                sound_path=tower_btn.get("sound"),
                                sfx_volume=self.slider_sfx.get_value() / 100
                            )
                            
                                break

                        # 3️⃣ Check placed towers for selection / upgrade / delete
                        self.selected_tower = None
                        for tower in self.placed_towers:
                            if tower.delete_button and tower.delete_button.collidepoint(game_mouse):
                                self.all_sprites.remove(tower)
                                self.placed_towers.remove(tower)
                                break
                            elif tower.upgrade_button and tower.upgrade_button.collidepoint(game_mouse):
                                # Check if player has enough money to upgrade tower
                                if self.money_system.on_tower_upgraded():
                                    tower.upgrade()
                                else:
                                    print("Not enough money to upgrade tower!")
                                break
                            elif tower.rect.collidepoint(game_mouse):
                                self.selected_tower = tower

                    # UI interactions
                    if self.show_start or self.show_map or self.inGame:
                        result = self.resolution_dropdown.handle_click((gx, gy))

                        if result:
                            self.current_resolution = result
                            self.apply_saved_resolution()
                            continue
                            
                        all_ui = (
                            list(self.ui_sprites) +
                            list(self.settings_sprites)
                        )

                        for ui in all_ui:
                            # IMPORTANT: use game coords for hit detection
                            if ui.rect.collidepoint((gx, gy)):
                                if ui.name == "resolution_dd":
                                    if self.resolution_dropdown.open:
                                        continue
                                if ui.name != "cloud":
                                    try:
                                        self.button_sfx.play()
                                    except:
                                        pass
                                    
                                # --- START SCREEN BUTTONS ---
                                if ui.name == "play":
                                    for elem in self.start_ui:
                                        if elem.name not in ("cloud", "startscreen", "logo"):
                                            try:
                                                self.ui_sprites.remove(elem)
                                            except Exception:
                                                pass
                                    for elem in self.settings_ui:
                                        self.ui_sprites.remove(elem)
                                    # show map selection
                                    self.map_selection()
                                elif ui.name == "settings" or ui.name == "gear":
                                    self.load_audio_settings()

                                    if self.inGame:
                                        self.paused = not self.paused
                                        self.quit.move_to()
                                    for elem in self.settings_ui:
                                        if elem.name not in ("quit"):
                                            try:
                                                elem.move_to()
                                            except Exception:
                                                pass
                                    try:
                                        self.slider_music.bar.move_to()
                                        self.slider_music.handle.move_to()
                                        self.slider_sfx.bar.move_to()
                                        self.slider_sfx.handle.move_to()
                                    except Exception:
                                        pass
                                    try:
                                        self.resolution_dropdown.move_to()
                                    except Exception:
                                        pass
                                    if self.show_start:
                                        for elem in self.start_ui:
                                            try:
                                                elem.move_away()
                                            except Exception:
                                                pass
                                elif ui.name == "play_back_btn":
                                    if self.inGame:
                                        self.paused = not self.paused
                                        self.quit.move_away()
                                    for elem in self.settings_ui:
                                        if elem.name not in ("quit"):
                                            try:
                                                elem.move_away()
                                            except Exception:
                                                pass
                                    try:
                                        self.slider_music.bar.move_away()
                                        self.slider_music.handle.move_away()
                                        self.slider_sfx.bar.move_away()
                                        self.slider_sfx.handle.move_away()
                                    except Exception:
                                        pass
                                    try:
                                        self.resolution_dropdown.move_away()
                                    except Exception:
                                        pass
                                    if self.show_start:
                                        for elem in self.start_ui:
                                            try:
                                                elem.move_to()
                                            except Exception:
                                                pass
                                    self.save_settings()
                                elif ui.name == "exit":
                                    self.running = False
                                
                                # --- MAP SCREEN BUTTONS ---
                                elif ui.name == "map":
                                    for elem in self.map_ui:
                                        try:
                                            elem.move_away()
                                        except Exception:
                                            pass
                                    for elem in self.map_selection_ui:
                                        try:
                                            elem.move_to()
                                        except Exception:
                                            pass

                                    self.logo.move_away()
                                elif ui.name == "upgrades":
                                    self.show_upgrades = True
                                    self.map_ui_surface.move_to()
                                    self.map_ui_back_btn.move_to()
                                    for elem in self.upgrade_ui:
                                        try:
                                            elem.move_to()
                                        except Exception:
                                            pass

                                    for elem in self.map_ui:
                                        try:
                                            elem.move_away()
                                        except Exception:
                                            pass
                                    self.logo.move_away()
                                if "_upgrade" in ui.name or "_downgrade" in ui.name:
                                    self.handle_upgrade_button(ui.name)
                                    continue
                                elif ui.name == "back":
                                    self.show_map = False
                                    for elem in self.map_ui:
                                        try:
                                            self.ui_sprites.remove(elem)
                                        except Exception:
                                            pass
                                    for elem in self.map_selection_ui:
                                        try:
                                            self.ui_sprites.remove(elem)
                                        except Exception:
                                            pass
                                    for elem in self.upgrade_ui:
                                        try:
                                            self.ui_sprites.remove(elem)
                                        except Exception:
                                            pass
                                    self.load_display_settings()
                                    self.start_screen()
                                elif ui.name == "map_1":
                                    self.map_selected = True
                                    self.map_ui_play_btn.set_dimmed(False)
                                elif ui.name == "ui_play_btn":
                                    if self.map_selected:

                                        # Re-add background & UI first
                                        for ui in self.settings_ui:
                                            if ui.name not in ("slider_music", "slider_sfx"):
                                                self.settings_sprites.add(ui)

                                        # NOW add the sliders LAST (handle & bar are inside slider group)
                                        self.settings_sprites.add(self.slider_music.bar)
                                        self.settings_sprites.add(self.slider_music.handle)

                                        self.settings_sprites.add(self.slider_sfx.bar)
                                        self.settings_sprites.add(self.slider_sfx.handle)


                                        self.show_map = False
                                        self.inGame = True
                                        self.ui_sprites.empty()
                                        self.setup()
                                        self.start_bgmusic.stop()
                                        self.game_bgmusic.play(loops=-1)
                                elif ui.name == "ui_back_btn":
                                    self.map_selected = False
                                    self.show_upgrades = False
                                    self.map_ui_play_btn.set_dimmed(True)
                                    for elem in self.map_selection_ui:
                                        try:
                                            elem.move_away()
                                        except Exception:
                                            pass
                                    for elem in self.map_ui:
                                        try:
                                            elem.move_to()
                                        except Exception:
                                            pass
                                    for elem in self.upgrade_ui:
                                        try:
                                            elem.move_away()
                                        except Exception:
                                            pass
                                    self.logo.move_to()
                                elif ui.name == "gear":
                                    print("settings")
                                elif ui.name == "pause_toggle":
                                    self.toggle_pause(self.hud_icons["pause_toggle"])
                                elif ui.name == "2x":
                                    self.fast_forward = not self.fast_forward
                                    self.time_scale = 2.0 if self.fast_forward else 1.0
                                    print(self.time_scale)
                                elif ui.name == "quit":
                                    if self.confirmation("Quit Match?"):
                                        self.reset_game()

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_tower:
                        mx, my = event.pos
                        gx = mx / scale_x
                        gy = my / scale_y
                        self.dragging_tower.rect.center = (gx, gy)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging_tower:
                        px, py = self.dragging_tower.rect.center
                        # Check if tower can be placed
                        if self.can_place_tower((px, py), self.dragging_tower.rect.size):
                            # Try spending money
                            if self.money_system.on_tower_placed():
                                self.all_sprites.add(self.dragging_tower)
                                self.placed_towers.append(self.dragging_tower)
                                print(f"{self.dragging_tower} placed!")
                            else:
                                print("Not enough money to place this tower!")
                        else:
                            print("Cannot place tower here!")
                        # Clear dragging tower regardless of placement
                        self.dragging_tower = None

            # --- Update Sprites ---
            if self.inGame and not self.paused and not self.game_over:
                self.all_sprites.update(dt)
                self.castles.update(dt)
                for tower in self.placed_towers:
                    tower.update(dt, self.monsters, self.all_sprites)
                self.wave_director.update(dt, self.placed_towers)

            self.ui_sprites.update(dt, game_mouse)
            self.settings_sprites.update(dt,game_mouse)

            self.resolution_dropdown.update(dt, (gx, gy))

            self.slider_music.update(dt, (gx, gy))
            self.slider_sfx.update(dt, (gx, gy))

            self.start_bgmusic.set_volume(self.slider_music.get_value()/100)
            self.game_bgmusic.set_volume(self.slider_music.get_value()/100)
            self.button_sfx.set_volume(self.slider_sfx.get_value()/100)
            self.hover_sfx.set_volume(self.slider_sfx.get_value()/100)
            self.gameover_sfx.set_volume(self.slider_sfx.get_value()/100)

            if self.inGame and self.dragging_tower:
                sound = getattr(self.dragging_tower, "shoot_sound", None)
                if sound:
                    sound.set_volume(self.slider_sfx.get_value() / 100)


            # --- Collisions ---
            if self.inGame and not self.paused and not self.game_over:
                hits = pygame.sprite.groupcollide(self.castles, self.monsters, False, False)
                for castle, monsters in hits.items():

                # AUTO-SELECT THE CORRECT CASTLE THE FIRST TIME IT TAKES DAMAGE
                    if self.main_castle is None:
                        self.main_castle = castle

                    for monster in monsters:
                        castle.take_damage(getattr(monster, "damage", 10))
                        monster.kill()

            # --- Drawing ---
            self.game_surface.fill("grey")
            if self.game_over:
                self.game_surface.blit(self.exp_text_surface, self.exp_text_rect)

            if self.inGame:
                self.all_sprites.set_target_surface(self.game_surface)
                self.all_sprites.draw()

                # Draw right-side HUD (castle HP, money, wave, time)
                self.draw_right_hud(self.game_surface)
                # --- draw castle health ---
                for castle in self.castles:
                    castle.draw_health(self.game_surface)

                for monster in self.monsters:
                    monster.draw_hp(self.game_surface)
            # Tower UI (selection, range, buttons)
                self.draw_tower_ui(self.game_surface)

            # Dragging tower preview
                if self.dragging_tower:
                    pos = self.dragging_tower.rect.center
                    valid = self.can_place_tower(pos, tower_size=self.dragging_tower.rect.size)

                    # Set color based on validity
                    color = (0, 255, 0) if valid else (255, 0, 0)

                    # Correct overlay size to match tower size
                    w, h = self.dragging_tower.rect.size
                    scale = 0.6
                    nw, nh = int(w * scale), int(h * scale)
                    overlay = pygame.Surface((nw, nh), pygame.SRCALPHA)
                    
                    # Draw semi-transparent rectangle
                    pygame.draw.rect(overlay, (*color, 80), (0, 0, nw, nh))
                    
                    # Draw outline rectangle on the game surface
                    outline_rect = pygame.Rect(pos[0] - nw // 2, pos[1] - nh // 2, nw, nh)
                    pygame.draw.rect(self.game_surface, color, outline_rect, 3)
                    
                    # Blit overlay and tower image
                    self.game_surface.blit(overlay, (pos[0] - nw // 2, pos[1] - nh // 2))
                    self.game_surface.blit(self.dragging_tower.image, self.dragging_tower.rect.topleft)\
                
                panel_x = 0
                panel_y = self.GAME_HEIGHT - 120
                panel_w = 420
                panel_h = 120

                # Panel background
                pygame.draw.rect(self.game_surface, (60, 40, 30), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
                pygame.draw.rect(self.game_surface, (100, 80, 60), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

                font_small = pygame.font.Font("assets/Monocraft.ttc", 12)   # SHRUNK FONT

                for tower_btn in self.tower_menu:
                    x, y = tower_btn["rect"].topleft

                    # Slot background (smaller)
                    pygame.draw.rect(self.game_surface, (90, 70, 55), tower_btn["rect"], border_radius=10)
                    pygame.draw.rect(self.game_surface, (120, 90, 70), tower_btn["rect"], 2, border_radius=10)

                    # Tower icon (already scaled smaller)
                    self.game_surface.blit(tower_btn["icon"], tower_btn["rect"].topleft)

                    # Tower name (smaller text)
                    name_text = font_small.render(tower_btn["name"], True, (255, 255, 255))
                    self.game_surface.blit(name_text, (x, y - 18))

                    # Price
                    price_text = font_small.render(f"${self.money_system.TOWER_COST}", True, (0, 255, 0))
                    self.game_surface.blit(price_text, (x, y + tower_btn["rect"].height + 3))
            # Draw UI
            # Always draw
            if self.inGame:
                header = self.wave_director.wave_header_surf.copy()
                path   = self.wave_director.wave_path_surf.copy()
                enemy  = self.wave_director.wave_enemy_surf.copy()

                alpha = self.wave_director.wave_announce_alpha

                header.set_alpha(alpha)
                path.set_alpha(alpha)
                enemy.set_alpha(alpha)

                self.game_surface.blit(header, self.wave_director.wave_header_pos)
                self.game_surface.blit(path,   self.wave_director.wave_path_pos)
                self.game_surface.blit(enemy,  self.wave_director.wave_enemy_pos)

            self.ui_sprites.set_target_surface(self.game_surface)
            self.ui_sprites.draw()
            self.settings_sprites.set_target_surface(self.game_surface)
            self.settings_sprites.draw()
            self.slider_music.handle_event(event, (gx, gy))
            self.slider_sfx.handle_event(event, (gx, gy))

            if self.show_map:
                self.draw_tower_multipliers(self.game_surface, self.archer_tower_upg, "archer_tower")
                self.draw_tower_multipliers(self.game_surface, self.stone_tower_upg, "stone_tower")
                self.draw_tower_multipliers(self.game_surface, self.sling_shot_tower_upg, "slingshot_tower")
                self.draw_tower_multipliers(self.game_surface, self.bomb_tower_upg, "bomb_tower")
            # Draw tower menu with name and price
            
            # optional refactoring (put all draw method in this function) #FIXME

            # Scale game surface to window
            scaled_surface = pygame.transform.smoothscale(self.game_surface, (window_w, window_h))
            self.screen.fill("black")
            self.screen.blit(scaled_surface, (offset_x, offset_y))
            pygame.display.update()

        pygame.quit()

# -----------------------------------------------
# Run game
# -----------------------------------------------
if __name__ == "__main__":
    game = TowerDefense()
    game.run()
