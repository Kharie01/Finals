from settings import *

class ExperienceSystem:
    def __init__(self):
        self.current_exp = 0
        self.stat_points = 0     # ADD THIS

        self.exp_per_stat = 100  # EXP needed for 1 stat point (adjust as needed)
        self.data_path = "assets/data/player.json"
        self.load_progress()

    def calculate_exp(self, base_exp: int, wave_count: int, multiplier: float) -> int:
        gained = base_exp + int(wave_count * multiplier)
        return max(gained, 0)

    def add_exp(self, amount: int):
        """Add EXP and convert excess into stat points."""
        self.current_exp += amount

        # Convert EXP into stat points
        while self.current_exp >= self.exp_per_stat:
            self.current_exp -= self.exp_per_stat
            self.stat_points += 1
            print(f"[STAT] +1 Stat Point awarded! Total: {self.stat_points}")
        
        self.save_progress()

    def grant_wave_exp(self, base_exp: int, wave_count: int, multiplier: float) -> int:
        gained = self.calculate_exp(base_exp, wave_count, multiplier)
        self.add_exp(gained)
        return gained

    def save_progress(self):
        data = {
            "exp": self.current_exp,
            "stat_points": self.stat_points
        }

        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=4)

        print("[SAVE] Player EXP and Stat Points saved.")

    def load_progress(self):
        if not os.path.exists(self.data_path):
            print("[LOAD] No progress file found — using defaults.")
            return

        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)
                self.current_exp = data.get("exp", 0)
                self.stat_points = data.get("stat_points", 0)

            print(f"[LOAD] EXP: {self.current_exp}, Stat Points: {self.stat_points}")

        except Exception as e:
            print(f"[ERROR] Failed to load progress: {e}")