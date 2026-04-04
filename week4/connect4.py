import tkinter as tk
from tkinter import messagebox
import random
import json
import os

class ConnectFour:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔴 Connect Four 🟡")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        # Board constants
        self.ROWS = 6
        self.COLS = 7
        self.CELL = 80
        self.RADIUS = 32

        # Colors
        self.COLORS = {
            "bg":      "#1a1a2e",
            "board":   "#0f3460",
            "empty":   "#16213e",
            "P1":      "#e94560",   # Red
            "P2":      "#f0c040",   # Yellow
            "AI":      "#f0c040",
            "hover":   "#ff8fa3",
            "win":     "#00ff88",
        }

        # Game state
        self.board = []
        self.current_player = 1
        self.game_over = False
        self.vs_ai = False
        self.hover_col = -1
        self.scores = {1: 0, 2: 0}
        self.move_history = []  # for undo

        # High score
        self.HS_FILE = "c4_scores.json"
        self.high_scores = self.load_scores()

        self.build_ui()
        self.reset_board()
        self.root.mainloop()

    # ──────────────── SCORES ────────────────
    def load_scores(self):
        if os.path.exists(self.HS_FILE):
            with open(self.HS_FILE, "r") as f:
                return json.load(f)
        return {"P1": 0, "P2": 0, "AI": 0}

    def save_scores(self):
        with open(self.HS_FILE, "w") as f:
            json.dump(self.high_scores, f)

    # ──────────────── UI ────────────────
    def build_ui(self):
        # ── Title ──
        tk.Label(self.root, text="🔴 Connect Four 🟡",
                 font=("Helvetica", 20, "bold"),
                 bg="#1a1a2e", fg="#00d4ff").pack(pady=8)

        # ── Score bar ──
        score_frame = tk.Frame(self.root, bg="#1a1a2e")
        score_frame.pack(fill="x", padx=20)

        self.p1_score_label = tk.Label(score_frame,
            text="🔴 Player 1: 0",
            font=("Helvetica", 12, "bold"),
            bg="#1a1a2e", fg="#e94560")
        self.p1_score_label.pack(side="left")

        self.turn_label = tk.Label(score_frame,
            text="🔴 Player 1's Turn",
            font=("Helvetica", 12, "bold"),
            bg="#1a1a2e", fg="white")
        self.turn_label.pack(side="left", expand=True)

        self.p2_score_label = tk.Label(score_frame,
            text="Player 2: 0 🟡",
            font=("Helvetica", 12, "bold"),
            bg="#1a1a2e", fg="#f0c040")
        self.p2_score_label.pack(side="right")

        # ── Canvas ──
        canvas_w = self.COLS * self.CELL + 20
        canvas_h = self.ROWS * self.CELL + 20
        self.canvas = tk.Canvas(self.root,
            width=canvas_w, height=canvas_h,
            bg="#0f3460",
            highlightthickness=2,
            highlightbackground="#00d4ff")
        self.canvas.pack(padx=20, pady=8)

        self.canvas.bind("<Motion>",   self.on_hover)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Leave>",    self.on_leave)

        # ── Mode + controls ──
        ctrl = tk.Frame(self.root, bg="#1a1a2e")
        ctrl.pack(pady=5)

        # Mode toggle
        tk.Label(ctrl, text="Mode:",
                 font=("Helvetica", 10),
                 bg="#1a1a2e", fg="#a0a0b0").grid(row=0, column=0, padx=5)

        self.pvp_btn = tk.Button(ctrl, text="👥 2 Players",
            font=("Helvetica", 10),
            bg="#00d4ff", fg="black",
            relief="flat", padx=8, pady=3,
            command=self.set_pvp)
        self.pvp_btn.grid(row=0, column=1, padx=5)

        self.ai_btn = tk.Button(ctrl, text="🤖 vs AI",
            font=("Helvetica", 10),
            bg="#16213e", fg="white",
            relief="flat", padx=8, pady=3,
            command=self.set_ai)
        self.ai_btn.grid(row=0, column=2, padx=5)

        # Difficulty
        tk.Label(ctrl, text="AI:",
                 font=("Helvetica", 10),
                 bg="#1a1a2e", fg="#a0a0b0").grid(row=0, column=3, padx=(15,3))

        self.diff_var = tk.StringVar(value="Medium")
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            tk.Radiobutton(ctrl, text=d,
                variable=self.diff_var, value=d,
                font=("Helvetica", 9),
                bg="#1a1a2e", fg="white",
                selectcolor="#0f3460",
                activebackground="#1a1a2e"
            ).grid(row=0, column=4+i, padx=2)

        # ── Buttons ──
        btn_row = tk.Frame(self.root, bg="#1a1a2e")
        btn_row.pack(pady=8)

        tk.Button(btn_row, text="🔄 New Game",
            font=("Helvetica", 11),
            bg="#e94560", fg="white",
            relief="flat", padx=12, pady=4,
            command=self.reset_board
        ).grid(row=0, column=0, padx=8)

        tk.Button(btn_row, text="↩ Undo",
            font=("Helvetica", 11),
            bg="#0f3460", fg="white",
            relief="flat", padx=12, pady=4,
            command=self.undo_move
        ).grid(row=0, column=1, padx=8)

        tk.Button(btn_row, text="🏆 Scores",
            font=("Helvetica", 11),
            bg="#0f3460", fg="#f0c040",
            relief="flat", padx=12, pady=4,
            command=self.show_scores
        ).grid(row=0, column=2, padx=8)

        # Hint
        tk.Label(self.root,
            text="Click a column to drop your piece",
            font=("Helvetica", 8),
            bg="#1a1a2e", fg="#555577").pack(pady=(0, 8))

    # ──────────────── MODE ────────────────
    def set_pvp(self):
        self.vs_ai = False
        self.pvp_btn.config(bg="#00d4ff", fg="black")
        self.ai_btn.config(bg="#16213e", fg="white")
        self.p2_score_label.config(text="Player 2: 0 🟡")
        self.reset_board()

    def set_ai(self):
        self.vs_ai = True
        self.ai_btn.config(bg="#e94560", fg="white")
        self.pvp_btn.config(bg="#16213e", fg="white")
        self.p2_score_label.config(text="AI: 0 🤖")
        self.reset_board()

    # ──────────────── BOARD ────────────────
    def reset_board(self):
        self.board = [[0]*self.COLS for _ in range(self.ROWS)]
        self.current_player = 1
        self.game_over = False
        self.hover_col = -1
        self.move_history = []
        self.update_turn_label()
        self.draw_board()

    def update_turn_label(self):
        if self.current_player == 1:
            self.turn_label.config(text="🔴 Player 1's Turn", fg="#e94560")
        else:
            label = "🤖 AI's Turn" if self.vs_ai else "🟡 Player 2's Turn"
            self.turn_label.config(text=label, fg="#f0c040")

    # ──────────────── DRAW ────────────────
    def draw_board(self):
        self.canvas.delete("all")
        pad = 10

        for r in range(self.ROWS):
            for c in range(self.COLS):
                x = pad + c * self.CELL + self.CELL // 2
                y = pad + r * self.CELL + self.CELL // 2

                # Hover highlight
                if c == self.hover_col and self.board[r][c] == 0 \
                        and not self.game_over:
                    p_color = self.COLORS["P1"] if self.current_player == 1 \
                              else self.COLORS["P2"]
                    self.canvas.create_oval(
                        x - self.RADIUS, y - self.RADIUS,
                        x + self.RADIUS, y + self.RADIUS,
                        fill=p_color, outline="", stipple="gray50")

                val = self.board[r][c]
                if val == 0:
                    color = self.COLORS["empty"]
                elif val == 1:
                    color = self.COLORS["P1"]
                else:
                    color = self.COLORS["P2"]

                self.canvas.create_oval(
                    x - self.RADIUS, y - self.RADIUS,
                    x + self.RADIUS, y + self.RADIUS,
                    fill=color, outline="#0f3460", width=2)

                # Shine effect on pieces
                if val != 0:
                    self.canvas.create_oval(
                        x - self.RADIUS + 8,
                        y - self.RADIUS + 8,
                        x - self.RADIUS + 22,
                        y - self.RADIUS + 22,
                        fill="white", outline="", stipple="gray75")

        # Column numbers hint
        for c in range(self.COLS):
            x = pad + c * self.CELL + self.CELL // 2
            self.canvas.create_text(x,
                self.ROWS * self.CELL + 14,
                text=str(c + 1),
                font=("Helvetica", 9),
                fill="#555577")

    def highlight_winner(self, cells):
        pad = 10
        for r, c in cells:
            x = pad + c * self.CELL + self.CELL // 2
            y = pad + r * self.CELL + self.CELL // 2
            self.canvas.create_oval(
                x - self.RADIUS, y - self.RADIUS,
                x + self.RADIUS, y + self.RADIUS,
                fill=self.COLORS["win"],
                outline="white", width=3)

    # ──────────────── EVENTS ────────────────
    def on_hover(self, event):
        col = (event.x - 10) // self.CELL
        if 0 <= col < self.COLS and col != self.hover_col:
            self.hover_col = col
            self.draw_board()

    def on_leave(self, event):
        self.hover_col = -1
        self.draw_board()

    def on_click(self, event):
        if self.game_over:
            return
        if self.vs_ai and self.current_player == 2:
            return
        col = (event.x - 10) // self.CELL
        if 0 <= col < self.COLS:
            self.drop_piece(col)

    # ──────────────── GAME LOGIC ────────────────
    def drop_piece(self, col):
        row = self.get_open_row(col)
        if row is None:
            return  # column full

        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        self.draw_board()

        win_cells = self.check_winner(self.current_player)
        if win_cells:
            self.highlight_winner(win_cells)
            self.end_game(winner=self.current_player)
            return

        if self.is_draw():
            self.end_game(winner=None)
            return

        self.current_player = 2 if self.current_player == 1 else 1
        self.update_turn_label()

        if self.vs_ai and self.current_player == 2:
            self.root.after(400, self.ai_move)

    def get_open_row(self, col):
        for r in range(self.ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return None

    def is_draw(self):
        return all(self.board[0][c] != 0 for c in range(self.COLS))

    # ──────────────── UNDO ────────────────
    def undo_move(self):
        if not self.move_history or self.game_over:
            return
        # If vs AI undo both moves
        moves_to_undo = 2 if self.vs_ai and len(self.move_history) >= 2 else 1
        for _ in range(moves_to_undo):
            if self.move_history:
                r, c, p = self.move_history.pop()
                self.board[r][c] = 0
                self.current_player = p
        self.update_turn_label()
        self.draw_board()

    # ──────────────── WIN CHECK ────────────────
    def check_winner(self, player):
        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                cells = [(r, c+i) for i in range(4)]
                if all(self.board[r][c+i] == player for i in range(4)):
                    return cells
        # Vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                cells = [(r+i, c) for i in range(4)]
                if all(self.board[r+i][c] == player for i in range(4)):
                    return cells
        # Diagonal ↘
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                cells = [(r+i, c+i) for i in range(4)]
                if all(self.board[r+i][c+i] == player for i in range(4)):
                    return cells
        # Diagonal ↙
        for r in range(self.ROWS - 3):
            for c in range(3, self.COLS):
                cells = [(r+i, c-i) for i in range(4)]
                if all(self.board[r+i][c-i] == player for i in range(4)):
                    return cells
        return None

    # ──────────────── AI ────────────────
    def ai_move(self):
        diff = self.diff_var.get()
        if diff == "Easy":
            col = self.ai_random()
        elif diff == "Medium":
            col = self.ai_medium()
        else:
            col = self.ai_minimax()
        self.drop_piece(col)

    def ai_random(self):
        valid = [c for c in range(self.COLS)
                 if self.get_open_row(c) is not None]
        return random.choice(valid)

    def ai_medium(self):
        # Win if possible
        for c in range(self.COLS):
            r = self.get_open_row(c)
            if r is not None:
                self.board[r][c] = 2
                if self.check_winner(2):
                    self.board[r][c] = 0
                    return c
                self.board[r][c] = 0
        # Block player 1
        for c in range(self.COLS):
            r = self.get_open_row(c)
            if r is not None:
                self.board[r][c] = 1
                if self.check_winner(1):
                    self.board[r][c] = 0
                    return c
                self.board[r][c] = 0
        return self.ai_random()

    def ai_minimax(self):
        best_score = -float("inf")
        best_col = None
        for c in range(self.COLS):
            r = self.get_open_row(c)
            if r is not None:
                self.board[r][c] = 2
                score = self.minimax(4, False, -float("inf"), float("inf"))
                self.board[r][c] = 0
                if score > best_score:
                    best_score = score
                    best_col = c
        return best_col if best_col is not None else self.ai_random()

    def minimax(self, depth, is_max, alpha, beta):
        if self.check_winner(2): return 1000 + depth
        if self.check_winner(1): return -(1000 + depth)
        if self.is_draw() or depth == 0: return 0

        if is_max:
            best = -float("inf")
            for c in range(self.COLS):
                r = self.get_open_row(c)
                if r is not None:
                    self.board[r][c] = 2
                    best = max(best, self.minimax(depth-1, False, alpha, beta))
                    self.board[r][c] = 0
                    alpha = max(alpha, best)
                    if beta <= alpha: break
            return best
        else:
            best = float("inf")
            for c in range(self.COLS):
                r = self.get_open_row(c)
                if r is not None:
                    self.board[r][c] = 1
                    best = min(best, self.minimax(depth-1, True, alpha, beta))
                    self.board[r][c] = 0
                    beta = min(beta, best)
                    if beta <= alpha: break
            return best

    # ──────────────── END ────────────────
    def end_game(self, winner):
        self.game_over = True
        if winner:
            self.scores[winner] += 1
            # Update score labels
            self.p1_score_label.config(
                text=f"🔴 Player 1: {self.scores[1]}")
            p2_text = f"AI: {self.scores[2]} 🤖" if self.vs_ai \
                      else f"Player 2: {self.scores[2]} 🟡"
            self.p2_score_label.config(text=p2_text)

            # Save high score
            key = "P1" if winner == 1 else ("AI" if self.vs_ai else "P2")
            self.high_scores[key] = self.high_scores.get(key, 0) + 1
            self.save_scores()

            if winner == 1:
                msg = "🔴 Player 1 Wins! 🎉"
            elif self.vs_ai:
                msg = "🤖 AI Wins! Better luck next time!"
            else:
                msg = "🟡 Player 2 Wins! 🎉"
            self.turn_label.config(text=msg, fg="#00ff88")
            messagebox.showinfo("Game Over", msg)
        else:
            self.turn_label.config(text="🤝 It's a Draw!", fg="#a0a0b0")
            messagebox.showinfo("Game Over", "It's a Draw! 🤝")

    def show_scores(self):
        msg = (f"🔴 Player 1 Wins: {self.high_scores.get('P1', 0)}\n"
               f"🟡 Player 2 Wins: {self.high_scores.get('P2', 0)}\n"
               f"🤖 AI Wins:       {self.high_scores.get('AI', 0)}")
        messagebox.showinfo("🏆 All Time Scores", msg)

# ── Start ──
ConnectFour()