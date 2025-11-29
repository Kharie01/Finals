import os
# Must be set BEFORE pygame.init()
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
import random
from settings import *
from sprites import *
from monsters import Monster
from castle import CastleBox
from user_interface import UserInterface, Dropdown
from slider import Slider
from tower import Tower # import Tower class
from game_ai import ENEMY_TYPES, WaveDirector

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
        self.wave_director = WaveDirector(self.spawn_enemy)
        self.load_display_settings()
        self.settings = self.load_display_settings()
        self.GAME_WIDTH  = 1280
        self.GAME_HEIGHT = 720
        self.fullscreen = False

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
        
        self.inGame = False

        # Sounds
        self.button_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'button-click.wav'))
        self.start_bgmusic = pygame.mixer.Sound(join('assets', 'audio', 'bgm', 'start_bgm.wav'))
        self.game_bgmusic = pygame.mixer.Sound(join('assets', 'audio', 'bgm', 'game_bgm.wav'))
        self.hover_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'mouse-hover.wav'))

        # Load UI images
        self.startscreen_images = {
            "start": pygame.image.load(join('assets', 'images', 'startscreen', 'Startscreen.png')).convert_alpha(),
            "logo": pygame.image.load(join('assets', 'images', 'startscreen', 'logo.png')).convert_alpha(),
            "play": pygame.image.load(join('assets', 'images', 'startscreen', 'play.png')).convert_alpha(),
            "setting": pygame.image.load(join('assets', 'images', 'startscreen', 'settings.png')).convert_alpha(),
            "exit": pygame.image.load(join('assets', 'images', 'startscreen', 'exit.png')).convert_alpha(),}
        self.map_selection_images = {
            "map": pygame.image.load(join('assets', 'images', 'mapscreen', 'map.png')).convert_alpha(),
            "back": pygame.image.load(join('assets', 'images', 'mapscreen', 'back.png')).convert_alpha(),
            "upgrade": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrade.png')).convert_alpha()}
        self.upgrades_images = {"border": pygame.image.load(join('assets', 'images', 'mapscreen', 'border.png')).convert_alpha(),
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


        # -------------------
        # Tower images
        # -------------------

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
                "size": tuple(tdata["size"])
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

        self.settings_ui_surface = UserInterface("ui_bg", (-self.GAME_WIDTH, self.GAME_HEIGHT // 2), pygame.image.load(join('assets', 'images', 'grybg.png')).convert_alpha(), (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, None)
        self.settings_ui_surface.set_opacity(200) 
        self.settings_ui_back_btn = UserInterface("play_back_btn", (-self.GAME_WIDTH + 60, 20), self.map_selection_images["back"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        # settings
        self.settings_ui_display = UserInterface("ui_display", (-self.GAME_WIDTH, 150), self.settings_images["display"], (254, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.settings_ui_music = UserInterface("ui_music", (-self.GAME_WIDTH, 570), self.settings_images["music"], (200, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.settings_ui_sfx = UserInterface("ui_sfx", (-self.GAME_WIDTH, 670), self.settings_images["sfx"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        self.slider_music = Slider("slider_music", (-self.GAME_WIDTH // 2 + 300, 470), bar_surface=self.slider_images["bar"], bar_scale=(600, 40), handle_surface=self.slider_images["handle"], handle_scale=(45, 45), ui_group=self.ui_sprites, min_value=0, max_value=100, default_value=50, game_width=self.GAME_WIDTH, game_height=self.GAME_HEIGHT, hover_sfx=self.hover_sfx)
        self.slider_sfx = Slider("slider_sfx", (-self.GAME_WIDTH // 2 + 300, 570), bar_surface=self.slider_images["bar"], bar_scale=(600, 40), handle_surface=self.slider_images["handle"], handle_scale=(45, 45), ui_group=self.ui_sprites, min_value=0, max_value=100, default_value=50, game_width=self.GAME_WIDTH, game_height=self.GAME_HEIGHT, hover_sfx=self.hover_sfx)

        self.settings = self.load_display_settings()
        self.current_resolution = self.settings["resolution"]

        self.res_image_map = {
                                "fullscreen": self.drop_down_images["fullscreen"],
                                "1280x720": self.drop_down_images["1280"],
                                "1600x900": self.drop_down_images["1600"]
                            }

        self.resolution_dropdown = Dropdown("resolution_dd", (-self.GAME_WIDTH//2 + 300, 200), self.res_image_map[self.current_resolution], (401, 75), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.resolution_dropdown.add_option("fullscreen", self.drop_down_images["fullscreen"], (401,75), offset_y=80, hover_sfx=self.hover_sfx)
        self.resolution_dropdown.add_option("1280x720", self.drop_down_images["1280"], (401,75), offset_y=160, hover_sfx=self.hover_sfx)
        self.resolution_dropdown.add_option("1600x900", self.drop_down_images["1600"], (401,75), offset_y=240, hover_sfx=self.hover_sfx)

        for ui in (self.settings_ui_surface, self.settings_ui_back_btn, self.settings_ui_display, self.settings_ui_music, self.settings_ui_sfx, self.slider_music, self.slider_sfx, self.resolution_dropdown):
            self.settings_ui.append(ui)

        self.load_audio_settings()
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
        self.stone_tower_upg = UserInterface("stone_tower", (-self.GAME_WIDTH // 2 - 200, 150), self.upgrades_images["stone"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.sling_shot_tower_upg = UserInterface("sling_shot_tower", (-self.GAME_WIDTH // 2 + 50, 150), self.upgrades_images["slingshot"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)
        self.bomb_tower_upg = UserInterface("bomb_tower", (-self.GAME_WIDTH // 2 + 300, 150), self.upgrades_images["bomb"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT, self.hover_sfx)

        for ui in (self.archer_tower_upg, self.stone_tower_upg, self.sling_shot_tower_upg, self.bomb_tower_upg):
            self.upgrade_ui.append(ui)
    # -----------------------------------------------
    # Setup map, sprites, castles, monsters
    # -----------------------------------------------
    def setup(self):
        # reset wave director every game
        self.wave_director.ai.wave_number = 1
        self.wave_director.ai.last_wave_time = 0
        self.wave_director.current_wave = []
        self.wave_director.enemies_spawned = 0

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
                castle = CastleBox((obj.x, obj.y), obj.width, obj.height, self.all_sprites, image=obj.image)
                self.all_sprites.add(castle)
                self.castles.add(castle)
                if obj.properties.get("hp_castle", False):
                    castle.has_hp = True

        # Other layers
        for layer_name in ["House", "decoration", "fences"]:
            for obj in tmx_data.get_layer_by_name(layer_name):
                Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation, self.all_sprites)

        # Waypoints
        self.waypoints = [(waypoint.x, waypoint.y) for waypoint in tmx_data.get_layer_by_name("Waypoints1")]

        # Clear and repopulate monster group

        self.path_rects = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.waypoints]

    def spawn_enemy(self, enemy_type):
        """Spawns a monster based on its type with correct sprite and stats."""

        # Get stats for this enemy type
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["grunt"])

        # Create the Monster (animations & speed are handled inside)
        monster = Monster(
            enemy_type=enemy_type,
            waypoints=self.waypoints,
            group=self.all_sprites,
            money_system=self.money_system  # <-- pass money system here
        )

        # Assign extra attributes
        monster.hp = stats["hp"]
        monster.max_hp = stats["hp"]
        monster.flying = stats.get("flying", False)
        monster.type = enemy_type

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
            # Draw selection outline if tower is selected
            tower.draw_selection(surface)

            if tower == self.selected_tower:
                # --- Upgrade/Delete Buttons ---
                tower.delete_button = pygame.Rect(tower.rect.right + 10, tower.rect.top, 50, 30)
                tower.upgrade_button = pygame.Rect(tower.rect.right + 10, tower.rect.top + 40, 50, 30)
                pygame.draw.rect(surface, (255, 0, 0), tower.delete_button)
                pygame.draw.rect(surface, (0, 255, 0), tower.upgrade_button)

                # --- Range Indicator (semi-transparent) ---
                if hasattr(tower, "range"):
                    overlay = pygame.Surface((tower.range*2, tower.range*2), pygame.SRCALPHA)
                    pygame.draw.circle(overlay, (0, 255, 0, 80), (tower.range, tower.range), tower.range)
                    pygame.draw.circle(overlay, (0, 255, 0), (tower.range, tower.range), tower.range, 2)
                    surface.blit(overlay, (tower.rect.centerx - tower.range, tower.rect.centery - tower.range))
            else:
                tower.delete_button = None
                tower.upgrade_button = None

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

        surface.blit(small.render(f"WAVE  : {self.wave_director.ai.wave_number}", True, (255,255,255)),
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
    
    # -----------------------------------------------
    # Main game loop
    # -----------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
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
                    
                    if event.key == pygame.K_SPACE:
                        self.wave_director.force_next_wave = True

                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # --- Mouse Input ---
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                            tower_type=tower_btn["name"].lower().replace(" ", "_")
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
                    if self.show_start or self.show_map:
                        result = self.resolution_dropdown.handle_click((gx, gy))

                        if result:
                            self.current_resolution = result
                            self.apply_saved_resolution()
                            continue

                        for ui in list(self.ui_sprites):
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
                                elif ui.name == "settings":
                                    self.load_audio_settings()

                                    for elem in self.start_ui:
                                        try:
                                            elem.move_away()
                                        except Exception:
                                            pass
                                    for elem in self.settings_ui:
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
                                elif ui.name == "play_back_btn":
                                    for elem in self.start_ui:
                                        try:
                                            elem.move_to()
                                        except Exception:
                                            pass
                                    for elem in self.settings_ui:
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
                                elif ui.name == "archer_tower":
                                    self.permanent_upgrades["archer_tower"]["damage_mult"] += 0.10
                                    self.permanent_upgrades["archer_tower"]["range_mult"] += 0.05
                                    self.permanent_upgrades["archer_tower"]["fire_rate_mult"] *= 0.95
                                    self.permanent_upgrades["archer_tower"]["projectile_speed_mult"] += 0.10
                                    self.save_permanent_upgrades()
                                elif ui.name == "stone_tower":
                                    self.permanent_upgrades["stone_tower"]["damage_mult"] += 0.10
                                    self.permanent_upgrades["stone_tower"]["range_mult"] += 0.05
                                    self.permanent_upgrades["stone_tower"]["fire_rate_mult"] *= 0.95
                                    self.permanent_upgrades["stone_tower"]["projectile_speed_mult"] += 0.10
                                    self.save_permanent_upgrades()
                                elif ui.name == "slingshot_tower":
                                    self.permanent_upgrades["slingshot_tower"]["damage_mult"] += 0.10
                                    self.permanent_upgrades["slingshot_tower"]["range_mult"] += 0.05
                                    self.permanent_upgrades["slingshot_tower"]["fire_rate_mult"] *= 0.95
                                    self.permanent_upgrades["slingshot_tower"]["projectile_speed_mult"] += 0.10
                                    self.save_permanent_upgrades()
                                elif ui.name == "bomb_tower":
                                    self.permanent_upgrades["bomb_tower"]["damage_mult"] += 0.10
                                    self.permanent_upgrades["bomb_tower"]["range_mult"] += 0.05
                                    self.permanent_upgrades["bomb_tower"]["fire_rate_mult"] *= 0.95
                                    self.permanent_upgrades["bomb_tower"]["projectile_speed_mult"] += 0.10
                                    self.save_permanent_upgrades()
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
                                        self.show_map = False
                                        self.inGame = True
                                        self.ui_sprites.empty()
                                        self.setup()
                                        self.start_bgmusic.stop()
                                        self.game_bgmusic.play(loops=-1)
                                elif ui.name == "ui_back_btn":
                                    self.map_selected = False
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
            if self.inGame:
                self.all_sprites.update(dt)
                self.castles.update(dt)

                for tower in self.placed_towers:
                    tower.update(dt, self.monsters, self.all_sprites)
                
                self.wave_director.update(dt, self.placed_towers)

            if self.show_start or self.show_map:
                self.ui_sprites.update(dt, game_mouse)

                self.resolution_dropdown.update(dt, (gx, gy))
                self.slider_music.update(dt, (gx, gy))
                self.slider_sfx.update(dt, (gx, gy))

                self.start_bgmusic.set_volume(self.slider_music.get_value()/100)
                self.game_bgmusic.set_volume(self.slider_music.get_value()/100)
                self.button_sfx.set_volume(self.slider_sfx.get_value()/100)
                self.hover_sfx.set_volume(self.slider_sfx.get_value()/100)

            # --- Collisions ---
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
            if self.show_start:
                self.ui_sprites.set_target_surface(self.game_surface)
                self.ui_sprites.draw()

                self.slider_music.handle_event(event, (gx, gy))
                self.slider_sfx.handle_event(event, (gx, gy))

            # Draw tower menu with name and price
            
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
