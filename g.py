import random
import tkinter as tk
from tkinter import messagebox


class Dragon:
    def __init__(self, name="Inferno"):
        self.name = name
        self.max_health = 100
        self.health = 100
        self.score = 0
        self.x = 0
        self.y = 0
        self.shield_active = False
        self.shield_used = False

    def take_damage(self, amount):
        if self.shield_active:
            amount = amount // 2
            self.shield_active = False
            msg = f"🛡️ Shield reduced damage! Took {amount} HP damage."
        else:
            msg = f"💥 Took {amount} damage!"

        self.health = max(0, self.health - amount)
        return amount, msg

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        return f"🧪 Power-up! Restored +{amount} HP."

    def add_score(self, amount):
        self.score += amount
        return f"💎 Treasure collected! +{amount} Score."


class Enemy:
    def __init__(self, x, y, enemy_type="Minion"):
        self.x = x
        self.y = y
        self.type = enemy_type
        if enemy_type == "Boss":
            self.symbol = "👹"
            self.damage = 25
            self.name = "Boss Dragon Hunter"
        else:
            self.symbol = "👾"
            self.damage = 15
            self.name = "Minion Enemy"

    def step_towards_dragon(self, dragon_x, dragon_y, grid_size, blocked_positions):
        dx, dy = 0, 0
        if self.x < dragon_x: dx = 1
        elif self.x > dragon_x: dx = -1

        if self.y < dragon_y: dy = 1
        elif self.y > dragon_y: dy = -1

        possible_moves = []
        if dx != 0: possible_moves.append((self.x + dx, self.y))
        if dy != 0: possible_moves.append((self.x, self.y + dy))

        random.shuffle(possible_moves)

        for nx, ny in possible_moves:
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if (nx, ny) not in blocked_positions:
                    self.x, self.y = nx, ny
                    break


class MapItem:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        symbols = {"Treasure": "💎", "PowerUp": "🧪", "SafeZone": "🏰"}
        self.symbol = symbols.get(kind, "?")


class DragonCityGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon City 2.0 - One-Time Shield Mode")
        self.grid_size = 10

        self.dragon = Dragon()
        self.enemies = []
        self.items = {}
        self.game_over = False

        self.setup_ui()
        self.generate_random_map()
        self.render_grid()

        self.root.bind("<Key>", self.handle_keypress)

    def setup_ui(self):
        self.header_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        self.header_frame.pack(fill=tk.X)

        self.stats_label = tk.Label(
            self.header_frame, text="", font=("Helvetica", 13, "bold"), bg="#2c3e50", fg="white"
        )
        self.stats_label.pack(side=tk.LEFT, padx=15)

        self.ability_btn = tk.Button(
            self.header_frame, text="🛡️ Shield Ready", font=("Helvetica", 11, "bold"),
            fg="#000000", disabledforeground="#7f8c8d", command=self.activate_shield
        )
        self.ability_btn.pack(side=tk.RIGHT, padx=15)

        self.grid_frame = tk.Frame(self.root, bg="#34495e", bd=5)
        self.grid_frame.pack(padx=10, pady=10)

        self.cells = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                lbl = tk.Label(
                    self.grid_frame, text=".", font=("Segoe UI Emoji", 15),
                    width=3, height=1, relief="ridge", bg="#ecf0f1"
                )
                lbl.grid(row=r, column=c, padx=1, pady=1)
                self.cells[(r, c)] = lbl

        self.bottom_frame = tk.Frame(self.root, pady=5)
        self.bottom_frame.pack(fill=tk.X, padx=10)

        self.log_label = tk.Label(
            self.bottom_frame, text="Use W/A/S/D or Arrow keys to move.",
            font=("Helvetica", 10, "italic"), fg="#16a085"
        )
        self.log_label.pack(side=tk.LEFT)

        self.restart_btn = tk.Button(
            self.bottom_frame, text="🔄 New Game", command=self.restart_game
        )
        self.restart_btn.pack(side=tk.RIGHT)

    def generate_random_map(self):
        self.dragon.x = 0
        self.dragon.y = 0
        self.dragon.health = 100
        self.dragon.score = 0
        self.dragon.shield_active = False
        self.dragon.shield_used = False
        self.game_over = False

        self.enemies.clear()
        self.items.clear()

        all_coords = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        all_coords.remove((0, 0))
        all_coords.remove((9, 9))
        random.shuffle(all_coords)

        self.items[(9, 9)] = MapItem(9, 9, "SafeZone")

        for _ in range(8):
            pos = all_coords.pop()
            self.items[pos] = MapItem(pos[0], pos[1], "Treasure")

        for _ in range(3):
            pos = all_coords.pop()
            self.items[pos] = MapItem(pos[0], pos[1], "PowerUp")

        for _ in range(6):
            pos = all_coords.pop()
            self.enemies.append(Enemy(pos[0], pos[1], "Minion"))

        for _ in range(1):
            pos = all_coords.pop()
            self.enemies.append(Enemy(pos[0], pos[1], "Boss"))

        self.update_log("🎮 Map Randomized! Shield is single-use only per game.")
        self.update_stats()

    def render_grid(self):
        for (r, c), lbl in self.cells.items():
            lbl.config(text="·", bg="#ecf0f1")

        for (r, c), item in self.items.items():
            self.cells[(r, c)].config(text=item.symbol)
            if item.kind == "SafeZone":
                self.cells[(r, c)].config(bg="#f1c40f")

        for enemy in self.enemies:
            bg_color = "#e74c3c" if enemy.type == "Boss" else "#e67e22"
            self.cells[(enemy.x, enemy.y)].config(text=enemy.symbol, bg=bg_color)

        dragon_color = "#9b59b6" if self.dragon.shield_active else "#3498db"
        self.cells[(self.dragon.x, self.dragon.y)].config(text="🐉", bg=dragon_color)

    def handle_keypress(self, event):
        if self.game_over:
            return

        key = event.keysym.lower()
        moves = {'w': (-1, 0), 'up': (-1, 0),
                 's': (1, 0),  'down': (1, 0),
                 'a': (0, -1), 'left': (0, -1),
                 'd': (0, 1),  'right': (0, 1)}

        if key in moves:
            dr, dc = moves[key]
            self.move_player(dr, dc)

    def move_player(self, dr, dc):
        new_x = self.dragon.x + dr
        new_y = self.dragon.y + dc

        if not (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size):
            self.update_log("⚠️ Cannot move off the 10x10 map!")
            return

        self.dragon.x = new_x
        self.dragon.y = new_y
        current_pos = (new_x, new_y)
        log_msg = "Moved."

        if current_pos in self.items:
            item = self.items[current_pos]
            if item.kind == "SafeZone":
                self.render_grid()
                self.game_over = True
                self.update_log("🏰 VICTORY! You escaped Dragon City!")
                messagebox.showinfo("Victory!", f"🎉 WINNER!\nFinal Score: {self.dragon.score}\nHealth Left: {self.dragon.health}")
                return
            elif item.kind == "Treasure":
                log_msg = self.dragon.add_score(100)
                del self.items[current_pos]
            elif item.kind == "PowerUp":
                log_msg = self.dragon.heal(30)
                del self.items[current_pos]

        enemy_killed = None
        for enemy in self.enemies:
            if enemy.x == new_x and enemy.y == new_y:
                dmg, fight_msg = self.dragon.take_damage(enemy.damage)
                log_msg = f"{fight_msg} Defeated {enemy.name}!"
                enemy_killed = enemy
                break

        if enemy_killed:
            self.enemies.remove(enemy_killed)

        self.run_enemy_ai(log_msg)

        if self.dragon.health <= 0:
            self.game_over = True
            self.render_grid()
            self.update_stats()
            self.update_log("☠️ Dragon has fallen!")
            messagebox.showerror("Game Over", "☠️ Health dropped to 0.")
            return

        self.render_grid()
        self.update_stats()

    def run_enemy_ai(self, step_log):
        blocked = set(self.items.keys())
        for e in self.enemies:
            blocked.add((e.x, e.y))

        ambushes = []
        defeated_enemies = []

        for enemy in self.enemies:
            blocked.discard((enemy.x, enemy.y))
            enemy.step_towards_dragon(self.dragon.x, self.dragon.y, self.grid_size, blocked)
            blocked.add((enemy.x, enemy.y))

            if enemy.x == self.dragon.x and enemy.y == self.dragon.y:
                dmg, _ = self.dragon.take_damage(enemy.damage)
                ambushes.append(f"{enemy.symbol} {enemy.name} ambushed you (-{dmg} HP)!")
                defeated_enemies.append(enemy)

        for enemy in defeated_enemies:
            self.enemies.remove(enemy)

        if ambushes:
            self.update_log(" | ".join(ambushes))
        else:
            self.update_log(step_log)

    def activate_shield(self):
        if not self.game_over and not self.dragon.shield_used and not self.dragon.shield_active:
            self.dragon.shield_active = True
            self.dragon.shield_used = True
            self.update_stats()
            self.render_grid()
            self.update_log("🛡️ Shield activated! Block 50% damage on next hit (Single-use item used).")

    def update_stats(self):
        shield_str = " 🛡️[SHIELD ACTIVE]" if self.dragon.shield_active else ""
        self.stats_label.config(
            text=f"HP: {self.dragon.health}/{self.dragon.max_health}{shield_str}  |  Score: {self.dragon.score}"
        )

        if self.dragon.shield_active:
            self.ability_btn.config(
                text="🛡️ Shield Active", state=tk.DISABLED,
                disabledforeground="#2c3e50"
            )
        elif self.dragon.shield_used:
            self.ability_btn.config(
                text="🚫 Shield Used", state=tk.DISABLED,
                disabledforeground="#7f8c8d"
            )
        else:
            self.ability_btn.config(
                text="🛡️ Shield Ready", state=tk.NORMAL,
                fg="#000000"
            )

    def update_log(self, text):
        self.log_label.config(text=text)

    def restart_game(self):
        self.generate_random_map()
        self.render_grid()


if __name__ == "__main__":
    root = tk.Tk()
    game = DragonCityGame(root)
    root.mainloop()
