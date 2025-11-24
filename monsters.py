from settings import *

class Monster(pygame.sprite.Sprite):
    def __init__(self, waypoints, image, speed, group):
        super().__init__(group)
        self.waypoints = waypoints
        self.pos = pygame.Vector2(self.waypoints[0])
        self.target_waypoint = 1

        self.angle = 360

        self.origin_img = image
        self.image = self.origin_img
        self.rect = self.image.get_rect(center = self.pos)

        self.speed = speed
        self.damage = 10

    def move(self):
        if self.target_waypoint < len(self.waypoints):
            self.target = pygame.Vector2(self.waypoints[self.target_waypoint])
            self.travel = self.target - self.pos
        else:
            #testing only
            self.pos = pygame.Vector2(self.waypoints[0])
            self.target_waypoint = 0


        distance = self.travel.length()

        if distance > self.speed:
            self.pos += self.travel.normalize() * self.speed
        else:
            if distance != 0:
                self.pos += self.travel.normalize() * distance
            self.target_waypoint += 1

        
        self.rect.center = self.pos

    def rotate(self):
        distance = self.target - self.pos
        self.angle = math.degrees(math.atan2(-distance[0], -distance[1]))
        self.image = pygame.transform.rotate(self.origin_img, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self, dt=None):
        self.move()
        self.rotate()