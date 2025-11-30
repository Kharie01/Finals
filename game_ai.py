import time
import random
from settings import *

# Define enemy types with attributes
ENEMY_TYPES = {
    "grunt":   {"cost": 5,  "speed": 1.67,  "hp": 60},
    "fast":    {"cost": 7,  "speed": 3.00, "hp": 40},
    "tank":    {"cost": 20, "speed": 1.00,  "hp": 250},
    "flying":  {"cost": 10, "speed": 2.43, "hp": 45, "flying": True},
    "swarm":   {"cost": 3,  "speed": 1.95,  "hp": 20},
}

# Predefined wave patterns
WAVE_PATTERNS = {
    "balanced": ["grunt", "grunt", "fast", "grunt"],
    "swarm":    ["swarm"] * 10,
    "tank_push":["tank", "grunt", "tank"],
    "fast_rush":["fast", "fast", "fast", "grunt"],
    "mixed":    ["grunt", "fast", "tank", "grunt", "flying"]
}

# AI STATES
class EnemyAIState:
    EARLY_GAME = 0
    MID_GAME   = 1
    LATE_GAME  = 2

# Strategic AI for Tower Defense Enemy Waves
class TowerDefenseEnemyAI:
    def __init__(self):
        self.state = EnemyAIState.EARLY_GAME
        self.wave_number = 1
        self.last_wave_time = 0.0
        self.wave_cooldown = 6.0
        random.seed()

    def update_state(self):
        # remove cooldown reset completely
        # self.wave_cooldown should NOT be touched here
        self.wave_cooldown = 0.0

        if self.wave_number < 4:
            self.state = EnemyAIState.EARLY_GAME
        elif self.wave_number < 9:
            self.state = EnemyAIState.MID_GAME
        else:
            self.state = EnemyAIState.LATE_GAME

    def pick_strategy(self):
        if self.state == EnemyAIState.EARLY_GAME:
            return random.choice(["balanced", "swarm"])
        elif self.state == EnemyAIState.MID_GAME:
            return random.choice(["balanced", "fast_rush", "mixed"])
        else:
            return random.choice(["tank_push", "mixed", "swarm"])

    def pick_monsters(self, strategy):
        pattern = WAVE_PATTERNS.get(strategy, ["grunt"])
        mutated = []
        for monster in pattern:
            if random.random() < 0.12:
                mutated.append(random.choice(list(ENEMY_TYPES.keys())))
            else:
                mutated.append(monster)
        return mutated

    def maybe_adapt(self, towers):
        if random.random() >= 0.20:
            return None
        if any(getattr(t, "type", "") == "anti_ground_only" for t in towers):
            return ["flying", "flying"]
        if any(getattr(t, "type", "") == "slow_shooter" for t in towers):
            return ["fast", "fast", "fast"]
        if any(getattr(t, "type", "") == "short_range" for t in towers):
            return ["tank"]
        return None

    def can_spawn_wave_now(self):
        return True

    def generate_wave(self, towers, force=False):
        self.update_state()

        if not force:
            now = time.time()
            if now - self.last_wave_time < self.wave_cooldown:
                return None

        strategy = self.pick_strategy()
        wave = self.pick_monsters(strategy)

        adapt = self.maybe_adapt(towers)
        if adapt:
            wave.extend(adapt)

        self.wave_number += 1
        self.last_wave_time = time.time()
        return wave

# Wave Director to manage spawning
class WaveDirector:
    def __init__(self, spawn_callback, waypoint_paths, game_width, game_height):
        self.spawn_callback = spawn_callback

        self.ai = TowerDefenseEnemyAI()
        self.current_wave = []
        self.enemies_spawned = 0

        self.spawn_timer = 0
        self.spawn_interval = 800  # ms per enemy

        self.force_next_wave = False

        self.current_waypoints = None
        self.paths = waypoint_paths

        # Wave announcement state
        self.wave_announce_alpha = 0
        self.wave_announce_timer = 0
        self.wave_announce_duration = 2.0     # fully visible
        self.wave_fade_speed = 150            # alpha per second
        self.wave_state = "idle"              # "fade_in", "hold", "fade_out"

        self.GAME_WIDTH = game_width
        self.GAME_HEIGHT = game_height

    def start_wave(self, towers, force=False):
        wave = self.ai.generate_wave(towers, force=force)
        if wave:
            weights = [0.5, 0.5]  # 70% chance for path 1, 30% for path 2
            self.current_waypoints = random.choices(self.paths, weights)[0]
    
            wave_number = self.ai.wave_number - 1
            path_index = 0 if self.current_waypoints == self.paths[0] else 1
            enemies_text = ", ".join(wave)

            # ---- FONTS ----
            header_font    = pygame.font.Font("assets/Monocraft.ttc", 80)  # big header
            subheader_font = pygame.font.Font("assets/Monocraft.ttc", 48)  # medium
            normal_font    = pygame.font.Font("assets/Monocraft.ttc", 32)  # normal text

            # ---- RENDER TEXT SURFACES ----
            self.wave_header_surf = header_font.render(f"Wave {wave_number}", True, (255, 230, 80))
            self.wave_path_surf = subheader_font.render(f"Path: {path_index}", True, (220, 220, 255))
            self.wave_enemy_surf = normal_font.render(f"Enemies: {enemies_text}", True, (255, 255, 255))

            # ---- POSITIONS (centered horizontally) ----
            screen_center = self.GAME_WIDTH // 2

            self.wave_header_pos = self.wave_header_surf.get_rect(center=(screen_center, 100))
            self.wave_path_pos   = self.wave_path_surf.get_rect(center=(screen_center, 160))
            self.wave_enemy_pos  = self.wave_enemy_surf.get_rect(center=(screen_center, 200))

            # ---- Start fade-in animation ----
            self.wave_announce_alpha = 0
            self.wave_announce_timer = 0
            self.wave_state = "fade_in"

            self.current_wave = wave
            self.enemies_spawned = 0
            self.spawn_timer = 0

    def update_wave_announcement(self, dt):

        if self.wave_state == "fade_in":
            print("a")
            self.wave_announce_alpha += self.wave_fade_speed * dt
            if self.wave_announce_alpha >= 255:
                self.wave_announce_alpha = 255
                self.wave_state = "hold"

        elif self.wave_state == "hold":
            print("b")
            self.wave_announce_timer += dt
            if self.wave_announce_timer >= self.wave_announce_duration:
                self.wave_state = "fade_out"

        elif self.wave_state == "fade_out":
            print("C")
            self.wave_announce_alpha -= self.wave_fade_speed * dt
            if self.wave_announce_alpha <= 0:
                self.wave_state = "idle"
                self.wave_announce_alpha = 0

    def update(self, dt, towers):
        if not self.current_wave:
            if self.force_next_wave:
                # Attempt to start now, forcing the AI to bypass cooldown
                self.start_wave(towers, force=True)
                # consume the force flag regardless of success (prevents repeated attempts)
                self.force_next_wave = False
            else:
                # Normal behavior (will only start when AI cooldown allows)
                self.start_wave(towers, force=False)
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval / 1000.0:
            enemy_type = self.current_wave[self.enemies_spawned]
            self.spawn_callback(enemy_type, self.current_waypoints)
            self.enemies_spawned += 1
            self.spawn_timer = 0

        # If finished spawning all enemies, clear current_wave so next can start
        if self.enemies_spawned >= len(self.current_wave):
            self.current_wave = []
            self.enemies_spawned = 0
            self.spawn_timer = 0
        
        self.update_wave_announcement(dt)

