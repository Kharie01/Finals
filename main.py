from settings import *
from sprites import *
from monsters import Monster
from castle import CastleBox
from user_interface import UserInterface
from tower import Tower  # import Tower class

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

        # Tower drag-and-drop
        self.tower_menu = []
        for i in range(3):  # three tower types
            rect = pygame.Rect(50 + i*100, self.GAME_HEIGHT - 100, 80, 80)
            self.tower_menu.append({"rect": rect, "tower_type": f"tower_{i}"})
        self.dragging_tower = None

        # Placed towers and selected tower
        self.placed_towers = []       # stores all towers placed
        self.selected_tower = None    # currently selected tower

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

        # Setup game map, sprites, castles, monsters
        self.start_screen()

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
    def setup(self, map_name = None):
        map = load_pygame(join('assets', 'data', 'tmx', 'finals.tmx'))

        # Ground tiles
        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprites((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        # Castles - clear and repopulate
        self.castles.empty()
        castle_layer = map.get_layer_by_name("castle")
        for obj in castle_layer:
            if hasattr(obj, "image") and obj.image is not None:
                castle = CastleBox((obj.x, obj.y), obj.width, obj.height, self.all_sprites, image=obj.image)
                self.all_sprites.add(castle)
                self.castles.add(castle)
                if obj.properties.get("hp_castle", False):
                    castle.has_hp = True

        # Houses, decorations, fences
        for layer_name in ["House", "decoration", "fences"]:
            for obj in map.get_layer_by_name(layer_name):
                Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation, self.all_sprites)

        # Waypoints for monsters
        self.waypoints = [(waypoint.x, waypoint.y) for waypoint in map.get_layer_by_name("Waypoints1")]

        # Clear and repopulate monster group
        self.monsters.empty()
        monster_img = pygame.image.load(join('assets', 'images', '0.png'))
        for _ in range(5):
            monster = Monster(self.waypoints, monster_img, randint(1, 5), self.all_sprites)
            self.monsters.add(monster)

        # Path rectangles
        self.path_rects = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.waypoints]

        # Spawn extra monsters for testing
        for _ in range(3):
            Monster(self.waypoints, monster_img, randint(1,3), self.all_sprites)

    # -----------------------------------------------
    # Main game loop
    # -----------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            window_w, window_h = self.screen.get_size()
            scale_x = window_w / self.GAME_WIDTH
            scale_y = window_h / self.GAME_HEIGHT
            offset_x = 0
            offset_y = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Fullscreen toggle
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)

                # Window resize
                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Mouse clicks for UI and tower drag/drop
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (self.show_start or self.show_map):
                    mx, my = event.pos
                    gx = (mx - offset_x) / scale_x
                    gy = (my - offset_y) / scale_y

                    # UI interactions
                    for ui in list(self.ui_sprites):
                        if ui.rect.collidepoint((gx, gy)):
                            if ui.name != "cloud":
                                try:
                                    self.button_sfx.play()
                                except Exception:
                                    pass
                            if ui.name == "play":
                                self.show_start = False
                                self.ui_sprites.remove(self.play_button, self.settings_button, self.exit_button)
                                self.map_selection()
                            if ui.name == "settings":
                                print("Settings button clicked")
                            if ui.name == "exit":
                                self.running = False
                            if ui.name == "map":
                                self.map_ui_surface.move_to()
                                self.map_ui_back_btn.move_to()
                                self.map_ui_play_btn.move_to()
                                self.map_ui_map_1.move_to()
                                self.map_button.move_away()
                                self.upgrades_button.move_away()
                                self.back_button.move_away()
                                self.logo.move_away()
                            if ui.name == "upgrades":
                                print("Upgrades button clicked")
                            if ui.name == "back":
                                self.show_map = False
                                self.ui_sprites.remove(self.map_button, self.upgrades_button, self.back_button, self.map_ui_surface)
                                self.start_screen()
                            if ui.name == "map_1":
                                self.map_selected = True
                                self.map_ui_play_btn.set_dimmed(False)
                            if ui.name == "ui_play_btn":
                                if self.map_selected:
                                    self.show_map = False
                                    self.inGame = True
                                    self.ui_sprites.empty()
                                    self.setup()
                                    self.start_bgmusic.stop()
                            if ui.name == "ui_back_btn":
                                self.map_selected = False
                                self.inGame = False
                                self.map_ui_play_btn.set_dimmed(True)
                                self.map_ui_surface.move_away()
                                self.map_ui_back_btn.move_away()
                                self.map_ui_play_btn.move_away()
                                self.map_ui_map_1.move_away()
                                self.map_button.move_to()
                                self.upgrades_button.move_to()
                                self.back_button.move_to()
                                self.logo.move_to()

            # map current mouse position to game-surface coordinates for hover checks (stretch mapping)

                    # Select towers (only when in game)
                    if self.inGame:
                        for tower in self.placed_towers:
                            if tower.rect.collidepoint((gx, gy)):
                                if self.selected_tower:
                                    self.selected_tower.deselect()
                                tower.select()
                                self.selected_tower = tower
                                break
                        else:
                            if self.selected_tower:
                                self.selected_tower.deselect()
                                self.selected_tower = None

                # Handle tower button clicks (only when in game)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.inGame:
                    if self.selected_tower:
                        mx, my = event.pos
                        gx = (mx - offset_x) / scale_x
                        gy = (my - offset_y) / scale_y
                        action = self.selected_tower.handle_button_click((gx, gy))
                        if action == "delete":
                            self.all_sprites.remove(self.selected_tower)
                            self.placed_towers.remove(self.selected_tower)
                            self.selected_tower = None

            # Tower drag from menu
            mx, my = pygame.mouse.get_pos()
            # Convert to game coordinates
            gx = (mx - offset_x) / scale_x
            gy = (my - offset_y) / scale_y

            if self.inGame:
                if pygame.mouse.get_pressed()[0]:
                    for tower in self.tower_menu:
                        if tower["rect"].collidepoint((mx, my)):
                            self.dragging_tower = {
                                "type": tower["tower_type"],
                                "image": pygame.Surface((50,50)),
                                "pos": pygame.Vector2(gx, gy)  # use game coordinates
                            }
                            self.dragging_tower["image"].fill((0,255,0))
                            break

                # Update dragging tower position every frame if dragging
                if self.dragging_tower:
                    self.dragging_tower["pos"].update(gx, gy)

                # Drop tower
                if self.dragging_tower and not pygame.mouse.get_pressed()[0]:
                    tower = Tower(self.dragging_tower["pos"], self.dragging_tower["image"])
                    self.all_sprites.add(tower)
                    self.placed_towers.append(tower)
                    self.dragging_tower = None

            # Update sprites
            self.all_sprites.update(dt)
            self.ui_sprites.update(dt)
            self.castles.update(dt)

            # Collisions: monsters hitting castles
            hits = pygame.sprite.groupcollide(self.castles, self.monsters, False, False)
            for castle, monsters in hits.items():
                for monster in monsters:
                    damage = getattr(monster, "damage", 10)
                    castle.take_damage(damage)
                    monster.kill()

            # Update towers (attack, buttons)
            for tower in self.placed_towers:
                tower.update(dt)
                tower.draw_buttons(self.game_surface)

            # Drawing
            self.game_surface.fill("grey")
            self.all_sprites.set_target_surface(self.game_surface)
            self.all_sprites.draw()
            for castle in self.castles:
                castle.draw_health(self.game_surface)

            if self.show_start or self.show_map:
                self.ui_sprites.set_target_surface(self.game_surface)
                self.ui_sprites.draw()

            if self.inGame:
            # Draw tower menu and dragging tower
                for tower in self.tower_menu:
                    pygame.draw.rect(self.game_surface, (100,100,100), tower["rect"])
                if self.dragging_tower:
                    img = self.dragging_tower["image"]
                    rect = img.get_rect(center=self.dragging_tower["pos"])
                    self.game_surface.blit(img, rect.topleft)

            # Scale and draw to window
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
