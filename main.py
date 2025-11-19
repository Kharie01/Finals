from settings import *
from sprites import *
from monsters import Monster

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

        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False

        self.setup()

        ## Set Monster spawns just for testing
        monster_img = pygame.image.load(join('assets', 'images', '0.png'))
        
        for monster in range(3):
            monster = Monster(self.waypoints, monster_img, randint(1,3), self.all_sprites)

    def setup(self):
        map = load_pygame(join('assets', 'data', 'tmx', 'finals.tmx'))

        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprites((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Objects"):
            Objects((obj.x, obj.y), obj.image, (obj.width, obj.height), obj.rotation,self.all_sprites)
            #print(type(obj.rotation))
        
        self.waypoints = [(waypoint.x, waypoint.y) for waypoint in map.get_layer_by_name("Waypoints")]

        ## Check x, y positions
        #print(self.waypoints)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

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

            # update
            self.all_sprites.update()
            
            # draw
            self.game_surface.fill((40, 40, 40))
            self.all_sprites.set_target_surface(self.game_surface)
            self.all_sprites.draw()

            # Draw everything on the game surface here

            # draw lines for the pathfinding debug
            # pygame.draw.lines(self.game_surface, "black", False, self.waypoints)
            

            window_w, window_h = self.screen.get_size()
            scale = min(window_w / self.GAME_WIDTH, window_h / self.GAME_HEIGHT)

            scaled_w = window_w
            scaled_h = window_h

            scaled_surface = pygame.transform.smoothscale(
                self.game_surface,
                (scaled_w, scaled_h)
            )

            # Center the scaled game (letterboxing)
            offset_x = 0
            offset_y = 0

            self.screen.fill("black")
            self.screen.blit(scaled_surface, (offset_x, offset_y))

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = TowerDefense()
    game.run()
