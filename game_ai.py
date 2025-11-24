import time
import random

# Define enemy types with attributes
ENEMY_TYPES = {
    "grunt":   {"cost": 5,  "speed": 80,  "hp": 60},
    "fast":    {"cost": 7,  "speed": 150, "hp": 40},
    "tank":    {"cost": 20, "speed": 45,  "hp": 250},
    "flying":  {"cost": 10, "speed": 120, "hp": 45, "flying": True},
    "swarm":   {"cost": 3,  "speed": 95,  "hp": 20},
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
        if self.wave_number < 4:
            self.state = EnemyAIState.EARLY_GAME
            self.wave_cooldown = 6.0
        elif self.wave_number < 9:
            self.state = EnemyAIState.MID_GAME
            self.wave_cooldown = 5.0
        else:
            self.state = EnemyAIState.LATE_GAME
            self.wave_cooldown = 4.0

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
        return (time.time() - self.last_wave_time) >= self.wave_cooldown

    def generate_wave(self, towers):
        self.update_state()
        if not self.can_spawn_wave_now():
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
    def __init__(self, spawn_callback):
        self.spawn_callback = spawn_callback

        self.ai = TowerDefenseEnemyAI()
        self.current_wave = []
        self.enemies_spawned = 0

        self.spawn_timer = 0
        self.spawn_interval = 800  # ms per enemy

    def start_wave(self, towers):
        wave = self.ai.generate_wave(towers)
        if wave:
            print(f"🔥 Starting Wave {self.ai.wave_number - 1} - {wave}")
            self.current_wave = wave
            self.enemies_spawned = 0

    def update(self, dt, towers):
        if not self.current_wave:
            self.start_wave(towers)
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.enemies_spawned < len(self.current_wave):
            enemy_type = self.current_wave[self.enemies_spawned]
            self.spawn_callback(enemy_type)
            self.enemies_spawned += 1
            self.spawn_timer = 0

        if self.enemies_spawned >= len(self.current_wave):
            self.current_wave = []
