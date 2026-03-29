import tkinter as tk
import random
import json
import os

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐍 Snake Game")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        # Constants
        self.WIDTH = 500
        self.HEIGHT = 500
        self.CELL = 20
        self.BASE_SPEED = 120

        # Difficulty speeds
        self.DIFFICULTIES = {
            "Easy":   150,
            "Medium": 120,
            "Hard":   80
        }
        self.difficulty = "Medium"
        self.SPEED = self.BASE_SPEED

        # High score file
        self.HS_FILE = "highscore.json"
        self.high_score = self.load_high_score()

        # Game state
        self.snake = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = None
        self.bonus_food = None
        self.bonus_timer = 0
        self.score = 0
        self.lives = 3
        self.level = 1
        self.running = False
        self.game_over = False
        self.paused = False
        self.wall_wrap = False  # wrap mode toggle

        # Snake themes
        self.themes = {
            "Ocean":  {"head": "#00d4ff", "body": "#0099bb"},
            "Fire":   {"head": "#ff6b35", "body": "#cc4400"},
            "Matrix": {"head": "#00ff41", "body": "#007a1f"},
        }
        self.current_theme = "Ocean"

        self.build_ui()
        self.root.mainloop()

    # ─────────────────── HIGH SCORE ───────────────────
    def load_high_score(self):
        if os.path.exists(self.HS_FILE):
            with open(self.HS_FILE, "r") as f:
                return json.load(f).get("high_score", 0)
        return 0

    def save_high_score(self):
        with open(self.HS_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    # ─────────────────── UI BUILD ───────────────────
    def build_ui(self):

        # ── Top info bar ──
        top = tk.Frame(self.root, bg="#1a1a2e")
        top.pack(fill="x", padx=20, pady=5)

        self.score_label = tk.Label(top, text="Score: 0",
            font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#00d4ff")
        self.score_label.pack(side="left")

        self.hs_label = tk.Label(top,
            text=f"Best: {self.high_score}",
            font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#e94560")
        self.hs_label.pack(side="right")

        self.level_label = tk.Label(top, text="Level: 1",
            font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#f0c040")
        self.level_label.pack(side="right", padx=20)

        # ── Lives ──
        self.lives_label = tk.Label(self.root,
            text="❤️ ❤️ ❤️",
            font=("Helvetica", 13), bg="#1a1a2e", fg="#e94560")
        self.lives_label.pack()

        # ── Canvas ──
        self.canvas = tk.Canvas(self.root,
            width=self.WIDTH, height=self.HEIGHT,
            bg="#0f3460",
            highlightthickness=2,
            highlightbackground="#e94560")
        self.canvas.pack(padx=20)

        # ── Controls row ──
        ctrl = tk.Frame(self.root, bg="#1a1a2e")
        ctrl.pack(pady=8)

        # Difficulty
        tk.Label(ctrl, text="Difficulty:",
            font=("Helvetica", 10), bg="#1a1a2e",
            fg="#a0a0b0").grid(row=0, column=0, padx=5)

        self.diff_var = tk.StringVar(value="Medium")
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            tk.Radiobutton(ctrl, text=d, variable=self.diff_var,
                value=d, command=self.set_difficulty,
                font=("Helvetica", 9),
                bg="#1a1a2e", fg="white",
                selectcolor="#0f3460",
                activebackground="#1a1a2e"
            ).grid(row=0, column=i+1, padx=3)

        # Theme
        tk.Label(ctrl, text="Theme:",
            font=("Helvetica", 10), bg="#1a1a2e",
            fg="#a0a0b0").grid(row=0, column=4, padx=(15,5))

        self.theme_var = tk.StringVar(value="Ocean")
        for i, t in enumerate(["Ocean", "Fire", "Matrix"]):
            tk.Radiobutton(ctrl, text=t, variable=self.theme_var,
                value=t, command=lambda th=t: self.set_theme(th),
                font=("Helvetica", 9),
                bg="#1a1a2e", fg="white",
                selectcolor="#0f3460",
                activebackground="#1a1a2e"
            ).grid(row=0, column=5+i, padx=3)

        # Wall wrap toggle
        self.wrap_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="🌀 Wall Wrap",
            variable=self.wrap_var,
            command=lambda: setattr(self, 'wall_wrap', self.wrap_var.get()),
            font=("Helvetica", 9),
            bg="#1a1a2e", fg="#a0a0b0",
            selectcolor="#0f3460",
            activebackground="#1a1a2e"
        ).grid(row=0, column=8, padx=10)

        # ── Buttons row ──
        btn_row = tk.Frame(self.root, bg="#1a1a2e")
        btn_row.pack(pady=5)

        self.start_btn = tk.Button(btn_row,
            text="▶ Start Game",
            font=("Helvetica", 11),
            bg="#e94560", fg="white",
            relief="flat", padx=12, pady=4,
            command=self.start_game)
        self.start_btn.grid(row=0, column=0, padx=8)

        self.pause_btn = tk.Button(btn_row,
            text="⏸ Pause",
            font=("Helvetica", 11),
            bg="#0f3460", fg="white",
            relief="flat", padx=12, pady=4,
            command=self.toggle_pause,
            state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=8)

        # ── Hint label ──
        tk.Label(self.root,
            text="Arrow Keys / WASD to move  |  Space to pause",
            font=("Helvetica", 8),
            bg="#1a1a2e", fg="#555577").pack(pady=(0, 8))

        # ── Key bindings ──
        self.root.bind("<Left>",  lambda e: self.change_dir("Left"))
        self.root.bind("<Right>", lambda e: self.change_dir("Right"))
        self.root.bind("<Up>",    lambda e: self.change_dir("Up"))
        self.root.bind("<Down>",  lambda e: self.change_dir("Down"))
        self.root.bind("<a>",     lambda e: self.change_dir("Left"))
        self.root.bind("<d>",     lambda e: self.change_dir("Right"))
        self.root.bind("<w>",     lambda e: self.change_dir("Up"))
        self.root.bind("<s>",     lambda e: self.change_dir("Down"))
        self.root.bind("<space>", lambda e: self.toggle_pause())

        self.draw_start_screen()

    # ─────────────────── SETTINGS ───────────────────
    def set_difficulty(self):
        self.difficulty = self.diff_var.get()
        self.SPEED = self.DIFFICULTIES[self.difficulty]

    def set_theme(self, theme):
        self.current_theme = theme

    # ─────────────────── SCREENS ───────────────────
    def draw_start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2 - 40,
            text="🐍 SNAKE GAME",
            font=("Helvetica", 30, "bold"), fill="#00d4ff")
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2 + 10,
            text="Features: Lives • Levels • Bonus Food",
            font=("Helvetica", 12), fill="#a0a0b0")
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2 + 40,
            text="Wall Wrap • Themes • High Score",
            font=("Helvetica", 12), fill="#a0a0b0")
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2 + 80,
            text="Press ▶ Start to Play!",
            font=("Helvetica", 14, "bold"), fill="#e94560")

    # ─────────────────── GAME FLOW ───────────────────
    def start_game(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.running = True
        self.paused = False
        self.game_over = False
        self.bonus_food = None
        self.bonus_timer = 0
        self.SPEED = self.DIFFICULTIES[self.diff_var.get()]

        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 1")
        self.lives_label.config(text="❤️ ❤️ ❤️")
        self.start_btn.config(text="🔄 Restart")
        self.pause_btn.config(state="normal")

        self.place_food()
        self.update()

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        self.running = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ Resume")
            self.canvas.create_rectangle(
                125, 200, 375, 300,
                fill="#1a1a2e", outline="#00d4ff", width=2)
            self.canvas.create_text(self.WIDTH//2, 245,
                text="⏸  PAUSED",
                font=("Helvetica", 26, "bold"), fill="#00d4ff")
            self.canvas.create_text(self.WIDTH//2, 280,
                text="Press Space to resume",
                font=("Helvetica", 11), fill="#a0a0b0")
        else:
            self.pause_btn.config(text="⏸ Pause")
            self.update()

    # ─────────────────── FOOD ───────────────────
    def place_food(self):
        while True:
            x = random.randint(0, (self.WIDTH  - self.CELL)//self.CELL) * self.CELL
            y = random.randint(0, (self.HEIGHT - self.CELL)//self.CELL) * self.CELL
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def place_bonus_food(self):
        while True:
            x = random.randint(0, (self.WIDTH  - self.CELL)//self.CELL) * self.CELL
            y = random.randint(0, (self.HEIGHT - self.CELL)//self.CELL) * self.CELL
            if (x, y) not in self.snake and (x, y) != self.food:
                self.bonus_food = (x, y)
                self.bonus_timer = 50  # disappears after 50 ticks
                break

    # ─────────────────── DIRECTION ───────────────────
    def change_dir(self, new_dir):
        opposites = {"Left": "Right", "Right": "Left",
                     "Up": "Down", "Down": "Up"}
        if new_dir != opposites.get(self.direction):
            self.next_direction = new_dir

    # ─────────────────── MAIN LOOP ───────────────────
    def update(self):
        if not self.running:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]

        moves = {
            "Left":  (-self.CELL, 0),
            "Right": ( self.CELL, 0),
            "Up":    (0, -self.CELL),
            "Down":  (0,  self.CELL)
        }
        dx, dy = moves[self.direction]
        new_x = head_x + dx
        new_y = head_y + dy

        # ── Wall wrap or collision ──
        if self.wall_wrap:
            new_x = new_x % self.WIDTH
            new_y = new_y % self.HEIGHT
        else:
            if new_x < 0 or new_x >= self.WIDTH or \
               new_y < 0 or new_y >= self.HEIGHT:
                self.lose_life()
                return

        new_head = (new_x, new_y)

        # ── Self collision ──
        if new_head in self.snake:
            self.lose_life()
            return

        self.snake.insert(0, new_head)

        # ── Eat normal food ──
        if new_head == self.food:
            self.score += 10
            self.place_food()
            self.check_level_up()

            # Spawn bonus food every 5 foods
            if self.score % 50 == 0:
                self.place_bonus_food()

        # ── Eat bonus food ──
        elif self.bonus_food and new_head == self.bonus_food:
            self.score += 30
            self.bonus_food = None
            self.bonus_timer = 0
        else:
            self.snake.pop()

        # ── Bonus food timer countdown ──
        if self.bonus_food:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus_food = None

        # ── Update labels ──
        self.score_label.config(text=f"Score: {self.score}")
        if self.score > self.high_score:
            self.high_score = self.score
            self.hs_label.config(text=f"Best: {self.high_score} 🏆")
            self.save_high_score()

        self.draw()
        self.root.after(self.SPEED, self.update)

    # ─────────────────── LEVEL UP ───────────────────
    def check_level_up(self):
        new_level = self.score // 50 + 1
        if new_level > self.level:
            self.level = new_level
            self.level_label.config(text=f"Level: {self.level}")
            if self.SPEED > 60:
                self.SPEED -= 8
            # Flash level up message
            self.canvas.create_text(
                self.WIDTH//2, 50,
                text=f"⬆ LEVEL {self.level}!",
                font=("Helvetica", 16, "bold"),
                fill="#f0c040", tags="levelup")
            self.root.after(800,
                lambda: self.canvas.delete("levelup"))

    # ─────────────────── LIVES ───────────────────
    def lose_life(self):
        self.lives -= 1
        hearts = "❤️ " * self.lives
        self.lives_label.config(text=hearts if self.lives > 0 else "💔")

        if self.lives <= 0:
            self.end_game()
        else:
            # Reset snake position, keep score
            self.snake = [(100, 100), (80, 100), (60, 100)]
            self.direction = "Right"
            self.next_direction = "Right"
            self.place_food()
            # Brief flash
            self.canvas.create_text(
                self.WIDTH//2, self.HEIGHT//2,
                text=f"💔 {self.lives} Lives Left!",
                font=("Helvetica", 20, "bold"),
                fill="#e94560", tags="life_msg")
            self.root.after(1000, lambda: self.canvas.delete("life_msg"))
            self.root.after(1000, self.update)

    # ─────────────────── DRAW ───────────────────
    def draw(self):
        self.canvas.delete("all")
        theme = self.themes[self.current_theme]

        # Grid
        for x in range(0, self.WIDTH, self.CELL):
            self.canvas.create_line(x, 0, x, self.HEIGHT,
                fill="#112244", width=1)
        for y in range(0, self.HEIGHT, self.CELL):
            self.canvas.create_line(0, y, self.WIDTH, y,
                fill="#112244", width=1)

        # Normal food 🍎
        fx, fy = self.food
        self.canvas.create_oval(
            fx+2, fy+2, fx+self.CELL-2, fy+self.CELL-2,
            fill="#e94560", outline="")
        self.canvas.create_text(fx+10, fy+10,
            text="🍎", font=("Helvetica", 11))

        # Bonus food ⭐ (blinking)
        if self.bonus_food:
            bx, by = self.bonus_food
            blink = self.bonus_timer % 6 < 3
            if blink:
                self.canvas.create_oval(
                    bx+1, by+1, bx+self.CELL-1, by+self.CELL-1,
                    fill="#f0c040", outline="")
                self.canvas.create_text(bx+10, by+10,
                    text="⭐", font=("Helvetica", 11))
            # Timer bar
            ratio = self.bonus_timer / 50
            self.canvas.create_rectangle(
                10, self.HEIGHT-8, 10 + int(200*ratio), self.HEIGHT-3,
                fill="#f0c040", outline="")
            self.canvas.create_text(120, self.HEIGHT-14,
                text="⭐ Bonus!", font=("Helvetica", 9), fill="#f0c040")

        # Snake body
        for i, (x, y) in enumerate(self.snake):
            color = theme["head"] if i == 0 else theme["body"]
            # Gradient effect — body gets slightly darker
            if i > 0 and i % 3 == 0:
                color = "#007799" if self.current_theme == "Ocean" else color
            self.canvas.create_rectangle(
                x+1, y+1, x+self.CELL-1, y+self.CELL-1,
                fill=color, outline="")

        # Eyes on head
        hx, hy = self.snake[0]
        d = self.direction
        if d == "Right":
            e1, e2 = (hx+12, hy+4, hx+16, hy+8), (hx+12, hy+12, hx+16, hy+16)
        elif d == "Left":
            e1, e2 = (hx+4, hy+4, hx+8, hy+8),   (hx+4, hy+12, hx+8, hy+16)
        elif d == "Up":
            e1, e2 = (hx+4, hy+4, hx+8, hy+8),   (hx+12, hy+4, hx+16, hy+8)
        else:
            e1, e2 = (hx+4, hy+12, hx+8, hy+16),  (hx+12, hy+12, hx+16, hy+16)

        self.canvas.create_oval(*e1, fill="white", outline="")
        self.canvas.create_oval(*e2, fill="white", outline="")

    # ─────────────────── GAME OVER ───────────────────
    def end_game(self):
        self.running = False
        self.game_over = True
        self.pause_btn.config(state="disabled")

        self.canvas.create_rectangle(
            80, 160, 420, 340,
            fill="#1a1a2e", outline="#e94560", width=2)
        self.canvas.create_text(self.WIDTH//2, 195,
            text="💀 GAME OVER",
            font=("Helvetica", 26, "bold"), fill="#e94560")
        self.canvas.create_text(self.WIDTH//2, 235,
            text=f"Score: {self.score}",
            font=("Helvetica", 16), fill="#00d4ff")
        self.canvas.create_text(self.WIDTH//2, 265,
            text=f"🏆 Best: {self.high_score}",
            font=("Helvetica", 14), fill="#f0c040")
        self.canvas.create_text(self.WIDTH//2, 295,
            text=f"Level Reached: {self.level}",
            font=("Helvetica", 12), fill="#a0a0b0")
        self.canvas.create_text(self.WIDTH//2, 325,
            text="Press 🔄 Restart to play again",
            font=("Helvetica", 10), fill="#555577")

# ── Start ──
SnakeGame()