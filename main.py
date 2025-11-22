from settings import *
from sprites import *
from monsters import Monster
from user_interface import UserInterface

import pygame

class TowerDefense:
    def __init__(self):
        pygame.init()

        self.GAME_WIDTH  = 1280
        self.GAME_HEIGHT = 704
        self.game_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Fortress Frontline")

        self.all_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)
        self.ui_sprites = AllSprite(self.GAME_WIDTH, self.GAME_HEIGHT)

        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.show_start = False

        self.button_sfx = pygame.mixer.Sound(join('assets', 'audio', 'sfx', 'button-click.wav'))

        # Load start screen and button images
        self.startscreen_images = {"start": pygame.image.load(join('assets', 'images', 'startscreen', 'Startscreen.png')).convert_alpha(),
                                    "play": pygame.image.load(join('assets', 'images', 'startscreen', 'play.png')).convert_alpha(),
                                    "setting": pygame.image.load(join('assets', 'images', 'startscreen', 'settings.png')).convert_alpha(),
                                    "exit": pygame.image.load(join('assets', 'images', 'startscreen', 'exit.png')).convert_alpha(),
                                }

        self.start_screen()

    def start_screen(self):
        self.show_start = True

        # User interface elements
        self.start_screen_bg = UserInterface("startscreen", (0, 0), self.startscreen_images["start"], (self.GAME_WIDTH, self.GAME_HEIGHT), self.ui_sprites)
        self.play_button = UserInterface("play", (self.GAME_WIDTH//2 + 350, self.GAME_HEIGHT//2 - 100), self.startscreen_images["play"], (150, 65), self.ui_sprites)
        self.settings_button = UserInterface("settings", (self.GAME_WIDTH//2 + 350, self.GAME_HEIGHT//2), self.startscreen_images["setting"], (254, 68), self.ui_sprites)
        self.exit_button = UserInterface("exit", (self.GAME_WIDTH//2 + 350, self.GAME_HEIGHT//2 + 100), self.startscreen_images["exit"], (139, 58), self.ui_sprites)

    def map_selection(self):
        pass

    def setup(self):
        map = load_pygame(join('assets', 'data', 'tmx', 'finals.tmx'))

        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprites((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("castle"):
            Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation,self.all_sprites)

        for obj in map.get_layer_by_name("House"):
            Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation,self.all_sprites)
            #print(type(obj.rotation))
        for obj in map.get_layer_by_name("decoration"):
            Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation,self.all_sprites)

        for obj in map.get_layer_by_name("fences"):
            Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation,self.all_sprites)
        
        self.waypoints = [(waypoint.x, waypoint.y) for waypoint in map.get_layer_by_name("Waypoints")]

        ## Set Monster spawns just for testing
        monster_img = pygame.image.load(join('assets', 'images', '0.png'))
        
        for monster in range(3):
            monster = Monster(self.waypoints, monster_img, randint(1,3), self.all_sprites)
        ## Check x, y positions
        #print(self.waypoints)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            window_w, window_h = self.screen.get_size()
            scale_x = window_w / self.GAME_WIDTH if self.GAME_WIDTH != 0 else 1
            scale_y = window_h / self.GAME_HEIGHT if self.GAME_HEIGHT != 0 else 1
            scaled_w = window_w
            scaled_h = window_h

            offset_x = 0
            offset_y = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Fullscreen toggle
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            w, h = self.screen.get_size()
                            self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

                # WINDOW RESIZE
                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Mouse clicks: convert screen coordinates to game-surface coordinates (stretch mapping)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.show_start:
                    mx, my = event.pos
                    gx = (mx - offset_x) / scale_x
                    gy = (my - offset_y) / scale_y
                    for ui in list(self.ui_sprites):
                        if ui.rect.collidepoint((gx, gy)):
                            if ui.name == "play":
                                self.show_start = False
                                self.ui_sprites.empty()
                                self.setup()
                                try:
                                    self.button_sfx.play()
                                except Exception:
                                    pass
                            elif ui.name == "settings":
                                print("Settings button clicked")
                                try:
                                    self.button_sfx.play()
                                except Exception:
                                    pass
                            elif ui.name == "exit":
                                self.running = False
                                try:
                                    self.button_sfx.play()
                                except Exception:
                                    pass

            # map current mouse position to game-surface coordinates for hover checks (stretch mapping)
            mx, my = pygame.mouse.get_pos()
            game_mouse = ( (mx - offset_x) / scale_x, (my - offset_y) / scale_y )

            # update
            self.all_sprites.update()
            # update UI sprites hover using mapped game_mouse
            for ui in self.ui_sprites:
                try:
                    ui.onMouseOver(game_mouse)
                except Exception:
                    # fallback to default update
                    ui.update()

            # draw
            self.all_sprites.set_target_surface(self.game_surface)
            self.all_sprites.draw()

            if self.show_start:
                self.ui_sprites.set_target_surface(self.game_surface)
                self.ui_sprites.draw()

            scaled_surface = pygame.transform.smoothscale(self.game_surface, (scaled_w, scaled_h))

            # draw onto the window centered (letterbox)
            self.screen.fill("black")
            self.screen.blit(scaled_surface, (offset_x, offset_y))

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = TowerDefense()
    game.run()
