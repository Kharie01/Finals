import time
import random
from settings import *
from enemy import ENEMY_TYPES

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
        self.casualties = 0
        random.seed()

    def update_state(self):
        # remove cooldown reset completely
        # self.wave_cooldown should NOT be touched here
        self.wave_cooldown = 20

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
    def __init__(self, spawn_callback, waypoint_paths, game_width, game_height, money_system=None):
        self.spawn_callback = spawn_callback
        self.mone_system = money_system

        self.ai = TowerDefenseEnemyAI()
        self.current_wave = []
        self.enemies_spawned = 0

        self.spawn_timer = 0
        self.spawn_interval = 800  # ms per enemy

        self.force_next_wave = False

        self.current_waypoints = None
        self.paths = waypoint_paths

        self.GAME_WIDTH = game_width
        self.GAME_HEIGHT = game_height

                # --- WAVE ANNOUNCEMENT ---
        self.wave_announce_duration = 2.5     # seconds
        self.wave_announce_timer = 0
        self.wave_state = "idle"              # "idle", "announce"
        self.wave_header_surf = None
        self.wave_path_surf = None
        self.wave_enemy_surf = None
        self.wave_header_pos = (game_width // 2, game_height // 2 - 60)
        self.wave_path_pos   = (game_width // 2, game_height // 2)
        self.wave_enemy_pos  = (game_width // 2, game_height // 2 + 40)
        self.wave_announce_alpha = 255


    def start_wave(self, towers, force=False):
        wave = self.ai.generate_wave(towers, force=force)
        if wave:
            weights = [0.5, 0.5]  # 70% chance for path 1, 30% for path 2
            self.current_waypoints = random.choices(self.paths, weights)[0]
            
            self.current_wave = wave
            self.enemies_spawned = 0
            self.spawn_timer = 0

            if self.ai.wave_number > 2:
                self.mone_system.on_wave_completed()
            self.make_wave_announcement(wave)

    def make_wave_announcement(self, wave):
        font_big   = pygame.font.Font(resource_path("assets/Monocraft-Bold.ttf"), 80)
        font_medium = pygame.font.Font(resource_path("assets/Monocraft.ttc"), 40)
        font_small = pygame.font.Font(resource_path("assets/Monocraft.ttc"), 16)

        wave_num = self.ai.wave_number - 1
        path_name = "Left" if self.current_waypoints == self.paths[0] else "Right"

        # Convert list ["grunt", "tank"] → "grunt, tank"
        enemy_list = ", ".join(wave)

        # Render text
        self.wave_header_surf = font_big.render(f"WAVE {wave_num}", True, (255,255,255))
        self.wave_path_surf   = font_medium.render(f"SPAWN SIDE: {path_name}", True, (255,255,100))
        self.wave_enemy_surf  = font_small.render(f"ENEMIES: {enemy_list}", True, (200,255,200))

        # Center alignment adjustments
        self.wave_header_pos = (self.GAME_WIDTH // 2 - self.wave_header_surf.get_width() // 2,
                                self.GAME_HEIGHT // 2 - 100)
        self.wave_path_pos   = (self.GAME_WIDTH // 2 - self.wave_path_surf.get_width() // 2,
                                self.GAME_HEIGHT // 2)
        self.wave_enemy_pos  = (self.GAME_WIDTH // 2 - self.wave_enemy_surf.get_width() // 2,
                                self.GAME_HEIGHT // 2 + 50)

        self.wave_state = "announce"
        self.wave_announce_timer = 0
        self.wave_announce_alpha = 255


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
            self.spawn_callback(enemy_type, self.current_waypoints, self.ai.wave_number - 1, self)
            self.enemies_spawned += 1
            self.spawn_timer = 0

        # If finished spawning all enemies, clear current_wave so next can start
        if self.enemies_spawned >= len(self.current_wave):
            self.current_wave = []
            self.enemies_spawned = 0
            self.spawn_timer = 0

        if self.wave_state == "announce":
            self.wave_announce_timer += dt
            if self.wave_announce_timer >= self.wave_announce_duration:
                self.wave_state = "idle"
            else:
                # Fade from 255 → 0
                progress = self.wave_announce_timer / self.wave_announce_duration
                self.wave_announce_alpha = max(0, 255 - int(progress * 255))
    
    def get_time_until_next_wave(self):
        """Return remaining time (in seconds) until the next wave spawns."""
        now = time.time()
        elapsed = now - self.ai.last_wave_time
        remaining = max(0, self.ai.wave_cooldown - elapsed)
        return remaining
    
    

