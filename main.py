from settings import *
from sprites import *
from monsters import Monster
from castle import CastleBox
from user_interface import UserInterface
from tower import Tower
from pytmx.util_pygame import load_pygame
from money import MoneySystem 
import pygame

from random import randint

class TowerDefense:
    """
    Main Tower Defense game class.
    Handles initialization, event loop, rendering, and game logic.
    """

    def __init__(self):
        pygame.init()

        # Game window settings
        self.GAME_WIDTH  = 1280
        self.GAME_HEIGHT = 704
        self.game_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Fortress Frontline")
        pygame.display.set_icon(pygame.image.load(join('assets', 'images', 'icon', 'gameicon.ico')).convert_alpha())

        # Sprite groups
        self.all_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)
        self.ui_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)
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
        self.start_bgmusic.set_volume(0.5)
        self.start_bgmusic.play(loops=-1)

        # Load UI images
        self.startscreen_images = {
            "start": pygame.image.load(join('assets', 'images', 'startscreen', 'Startscreen.png')).convert_alpha(),
            "logo": pygame.image.load(join('assets', 'images', 'startscreen', 'logo.png')).convert_alpha(),
            "play": pygame.image.load(join('assets', 'images', 'startscreen', 'play.png')).convert_alpha(),
            "setting": pygame.image.load(join('assets', 'images', 'startscreen', 'settings.png')).convert_alpha(),
            "exit": pygame.image.load(join('assets', 'images', 'startscreen', 'exit.png')).convert_alpha(),
        }
        self.map_selection_images = {
            "map": pygame.image.load(join('assets', 'images', 'mapscreen', 'map.png')).convert_alpha(),
            "back": pygame.image.load(join('assets', 'images', 'mapscreen', 'back.png')).convert_alpha(),
            "upgrade": pygame.image.load(join('assets', 'images', 'mapscreen', 'upgrade.png')).convert_alpha()
        }
        self.upgrades_images = {}
        self.map_images = {"map1": pygame.image.load(join('assets', 'images', 'mapscreen', 'map1.png')).convert_alpha()}

        # -------------------
        # Tower images
        # -------------------

        # Archer Tower
        archer_idle = pygame.image.load("assets/data/graphics/tower/archer/archer1.png").convert_alpha()
        archer_build = [
            pygame.image.load("assets/data/graphics/tower/archer/building1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/archer/archer1.png").convert_alpha()
        ]
        archer_upgrades = [
            pygame.image.load("assets/data/graphics/tower/archer/archer1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/archer/archer2.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/archer/archer3.png").convert_alpha()
        ]

        # Stone Tower
        stone_idle = pygame.image.load("assets/data/graphics/tower/stone/3.png").convert_alpha()
        stone_build = [
            pygame.image.load("assets/data/graphics/tower/stone/5.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/stone/3.png").convert_alpha()
        ]
        stone_upgrades = [
            pygame.image.load("assets/data/graphics/tower/stone/3.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/stone/6.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/stone/7.png").convert_alpha()
        ]

        # Slingshot Tower
        slingshot_idle = pygame.image.load("assets/data/graphics/tower/slingshot/slingshot1.png").convert_alpha()
        slingshot_build = [
            pygame.image.load("assets/data/graphics/tower/slingshot/progressSlingShot1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/slingshot/slingshot1.png").convert_alpha()
        ]
        slingshot_upgrades = [
            pygame.image.load("assets/data/graphics/tower/slingshot/slingshot1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/slingshot/slingshot2.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/slingshot/slingshot3.png").convert_alpha()
        ]

        # Bomb Tower
        bomb_idle = pygame.image.load("assets/data/graphics/tower/bomb/bombtower1.png").convert_alpha()
        bomb_build = [
            pygame.image.load("assets/data/graphics/tower/bomb/progressBomb1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/bomb/bombtower1.png").convert_alpha()
        ]
        bomb_upgrades = [
            pygame.image.load("assets/data/graphics/tower/bomb/bombtower1.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/bomb/bombtower2.png").convert_alpha(),
            pygame.image.load("assets/data/graphics/tower/bomb/bombtower3.png").convert_alpha()
        ]


        # Tower drag-and-drop
        self.placed_towers = []       # stores all towers placed
        self.selected_tower = None    # currently selected tower
        self.dragging_tower = None
        menu_y = self.GAME_HEIGHT - 100
        self.tower_menu = [
            {
                "rect": pygame.Rect(50, menu_y, 80, 80),
                "class": Tower,
                "idle": archer_idle,
                "building_frames": archer_build,
                "upgrade_images": archer_upgrades,
                "damage": 15,
                "range": 120,
                "fire_rate": 1.2,
                "projectile_image": pygame.image.load("assets/data/graphics/projectiles/arrow.png").convert_alpha(),
                "projectile_speed": 400,
                "size": (80, 100)
            },
            {
                "rect": pygame.Rect(150, menu_y, 80, 80),
                "class": Tower,
                "idle": stone_idle,
                "building_frames": stone_build,
                "upgrade_images": stone_upgrades,
                "damage": 25,
                "range": 180,
                "fire_rate": 0.8,
                "projectile_image": pygame.image.load("assets/data/graphics/projectiles/stone.png").convert_alpha(),
                "projectile_speed": 300,
                "size": (50, 60)
            },
            {
                "rect": pygame.Rect(250, menu_y, 80, 80),
                "class": Tower,
                "idle": slingshot_idle,
                "building_frames": slingshot_build,
                "upgrade_images": slingshot_upgrades,
                "damage": 10,
                "range": 150,
                "fire_rate": 1.5,
                "projectile_image": pygame.image.load("assets/data/graphics/projectiles/slingshot.png").convert_alpha(),
                "projectile_speed": 500,
                "size": (50, 70)
            },
            {
            "rect": pygame.Rect(350, menu_y, 80, 80),
            "class": Tower,
            "idle": bomb_idle,
            "building_frames": bomb_build,
            "upgrade_images": bomb_upgrades,
            "damage": 40,
            "range": 80,
            "fire_rate": 0.5,
            "projectile_image": pygame.image.load("assets/data/graphics/projectiles/bomb.png").convert_alpha(),
            "projectile_speed": 250,
            "size": (50, 70)
            }
        ]

        #Money
        self.money_system = MoneySystem(starting_money=500)


        self.setup()  # make sure setup is called after
        # Setup game map, sprites, castles, monsters
       

    # -----------------------------------------------
    # Start screen UI
    # -----------------------------------------------
    def start_screen(self):
        self.show_start = True
        if not hasattr(self, "start_screen_bg"):
            self.start_screen_bg = UserInterface("startscreen", (0, 0), self.startscreen_images["start"], (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)

        # Clouds background
        if not hasattr(self, "cloud"):
            for cloud in range(5):
                self.cloud = UserInterface("cloud",(randint(-100, self.GAME_WIDTH), randint(0, self.GAME_HEIGHT // 2 - 200)),pygame.image.load(join('assets', 'images', 'startscreen', 'clouds', f'cloud{randint(1, 4)}.png')).convert_alpha(),(300, 80),self.ui_sprites)

        self.logo = UserInterface("logo", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 250), self.startscreen_images["logo"], (417, 146), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.play_button = UserInterface("play", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 100), self.startscreen_images["play"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.settings_button = UserInterface("settings", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2), self.startscreen_images["setting"], (254, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.exit_button = UserInterface("exit", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 + 100), self.startscreen_images["exit"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)

    # -----------------------------------------------
    # Map selection screen
    # -----------------------------------------------
    def map_selection(self):
        self.show_map = True
        self.map_selected = False

        self.map_button = UserInterface("map", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 - 100), self.map_selection_images["map"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.upgrades_button = UserInterface("upgrades", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2), self.map_selection_images["upgrade"], (265, 68), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.back_button = UserInterface("back", (self.GAME_WIDTH // 2 + 360, self.GAME_HEIGHT // 2 + 100), self.map_selection_images["back"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)

        self.map_ui_surface = UserInterface("ui_bg", (-self.GAME_WIDTH, self.GAME_HEIGHT // 2), pygame.image.load(join('assets', 'images', 'grybg.png')).convert_alpha(), (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.map_ui_surface.set_opacity(200)  # Slightly transparent (0-255, 255 is fully opaque)
        self.map_ui_back_btn = UserInterface("ui_back_btn", (-self.GAME_WIDTH + 60, 0 + 60), self.map_selection_images["back"], (139, 58), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.map_ui_play_btn = UserInterface("ui_play_btn", (-self.GAME_WIDTH, self.GAME_HEIGHT - 200), self.startscreen_images["play"], (150, 65), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.map_ui_map_1 = UserInterface("map_1", (-self.GAME_WIDTH // 2 - 150, 0 + 150), self.map_images["map1"], (250, 250), self.ui_sprites, self.GAME_WIDTH, self.GAME_HEIGHT)

        self.map_ui_play_btn.set_dimmed(True)

    # -----------------------------------------------
    # Setup map, sprites, castles, monsters
    # -----------------------------------------------
    def setup(self):
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
        self.monsters.empty()
        monster_img = pygame.image.load(join('assets', 'images', '0.png'))
        for _ in range(5):
            monster = Monster(self.waypoints, monster_img, randint(1, 5), self.all_sprites)
            self.monsters.add(monster)

        self.path_rects = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.waypoints]

        for _ in range(5):
            Monster(self.waypoints, monster_img, randint(1,5), self.all_sprites)


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

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)

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
                    # 1️⃣ Check UI buttons first
                    for ui in list(self.ui_sprites):
                        if ui.rect.collidepoint(game_mouse):
                            if ui.name not in ["cloud", "startscreen"]:
                                try: self.button_sfx.play()
                                except: pass
                            if ui.name == "play":
                                self.show_start = False
                                self.ui_sprites.remove(self.play_button, self.settings_button, self.exit_button)
                                self.map_selection()
                            elif ui.name == "settings":
                                print("Settings clicked")
                            elif ui.name == "exit":
                                self.running = False
                            elif ui.name == "back":
                                self.show_map = False
                                self.ui_sprites.remove(self.map_button, self.upgrades_button, self.back_button, self.map_ui_surface)
                                self.start_screen()
                            elif ui.name == "map":
                                print("Map clicked")
                            elif ui.name == "upgrades":
                                print("Upgrades clicked")

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
                            money_system=self.money_system  # pass reference
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
            self.all_sprites.update(dt)
            self.ui_sprites.update(dt, game_mouse)
            self.castles.update(dt)
            for tower in self.placed_towers:
                tower.update(dt, self.monsters, self.all_sprites)

            # --- Collisions ---
            hits = pygame.sprite.groupcollide(self.castles, self.monsters, False, False)
            for castle, monsters in hits.items():
                for monster in monsters:
                    castle.take_damage(getattr(monster, "damage", 10))
                    monster.kill()

            # --- Drawing ---
            self.game_surface.fill("grey")
            self.all_sprites.set_target_surface(self.game_surface)
            self.all_sprites.draw()

            # Tower UI (selection, range, buttons)
            self.draw_tower_ui(self.game_surface)

            # Dragging tower preview
            if self.dragging_tower:
                pos = self.dragging_tower.rect.center
                valid = self.can_place_tower(pos)
                color = (0, 255, 0) if valid else (255, 0, 0)
                overlay = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(overlay, (*color, 80), (40, 40), 38)
                pygame.draw.circle(self.game_surface, color, pos, 40, 3)
                self.game_surface.blit(overlay, (pos[0] - 40, pos[1] - 40))
                self.game_surface.blit(self.dragging_tower.image, self.dragging_tower.rect.topleft)

            # Draw tower menu
            for tower_btn in self.tower_menu:
                self.game_surface.blit(
                    pygame.transform.scale(tower_btn["idle"], (tower_btn["rect"].width, tower_btn["rect"].height)),
                    tower_btn["rect"].topleft
                )

            # Draw UI
            if self.show_start or self.show_map:
                self.ui_sprites.set_target_surface(self.game_surface)
                self.ui_sprites.draw()

            # Draw tower menu with name and price
            font = pygame.font.SysFont("Arial", 20)
            money_font = pygame.font.SysFont("Arial", 24)

            # 1️⃣ Draw current money
            money_text = money_font.render(f"Money: {self.money_system.money}", True, (255, 255, 0))
            self.game_surface.blit(money_text, (10, 10))

            # 2️⃣ Draw each tower button with name & cost
            for idx, tower_btn in enumerate(self.tower_menu):
                # Draw tower icon
                self.game_surface.blit(
                    pygame.transform.scale(tower_btn["idle"], (tower_btn["rect"].width, tower_btn["rect"].height)),
                    tower_btn["rect"].topleft
                )
                
                # Draw tower name
                tower_name = tower_btn.get("name", f"Tower {idx+1}")  # fallback name
                name_text = font.render(tower_name, True, (255, 255, 255))
                self.game_surface.blit(name_text, (tower_btn["rect"].x, tower_btn["rect"].y - 25))
                
                # Draw tower price
                price = self.money_system.TOWER_COST
                price_text = font.render(f"${price}", True, (0, 255, 0))
                self.game_surface.blit(price_text, (tower_btn["rect"].x, tower_btn["rect"].y + tower_btn["rect"].height + 5))

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
