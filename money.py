# ============================================================
#                      MONEY SYSTEM 
#               Tower Defense Game Logic
# ============================================================
class MoneySystem:

    def __init__(self, starting_money=200):
        # Private money value
        self._money = starting_money

        # ---- Game Economy Values (editable anytime) ----
        self.TOWER_COST = 100
        self.UPGRADE_COST = 75

        self.REWARD_KILL = 25
        self.REWARD_WAVE_START = 50
        self.REWARD_WAVE_COMPLETE = 150
        self.REWARD_CASTLE_DEFENSE = 50

    # ----------------------------------------------------
    #                    CORE FUNCTIONS
    # ----------------------------------------------------

    @property
    def money(self):
        """Read-only access to current available money."""
        return self._money

    def can_afford(self, amount: int) -> bool:
        """Returns True if money is enough to pay for amount."""
        return self._money >= amount

    def add(self, amount: int):
        """Increases player's money."""
        self._money += amount
        print(f"[MONEY] +{amount} → Total: {self._money}")

    def spend(self, amount: int) -> bool:
        """
        Attempts to spend money.
        Returns True if transaction is successful.
        """
        if self.can_afford(amount):
            self._money -= amount
            print(f"[MONEY] -{amount} → Total: {self._money}")
            return True

        print("[MONEY] Transaction failed → Not enough funds!")
        return False

    # ----------------------------------------------------
    #                GAME EVENT HOOKS 
    # ----------------------------------------------------

    def on_tower_placed(self) -> bool:
        """Called when player attempts to place a tower."""
        return self.spend(self.TOWER_COST)

    def on_tower_upgraded(self) -> bool:
        """Called when upgrading a tower."""
        return self.spend(self.UPGRADE_COST)

    def on_enemy_killed(self):
        """Called when a tower kills an enemy."""
        self.add(self.REWARD_KILL)

    def on_wave_start(self):
        """Called when a new wave begins."""
        self.add(self.REWARD_WAVE_START)

    def on_wave_completed(self):
        """Called when a wave is successfully cleared."""
        self.add(self.REWARD_WAVE_COMPLETE)

    def on_castle_defended(self):
        """Called if the castle survives the wave."""
        self.add(self.REWARD_CASTLE_DEFENSE)
