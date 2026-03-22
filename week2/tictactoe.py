import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        self.score = {"X": 0, "O": 0}
        self.vs_ai = False  # AI toggle

        self.build_ui()
        self.root.mainloop()

    def build_ui(self):
        # Title
        tk.Label(self.root, text="Tic Tac Toe",
                 font=("Helvetica", 20, "bold"),
                 bg="#1a1a2e", fg="#e94560").pack(pady=10)

        # Score
        self.score_label = tk.Label(
            self.root,
            text="X: 0  |  O: 0",
            font=("Helvetica", 13),
            bg="#1a1a2e", fg="#a0a0b0"
        )
        self.score_label.pack(pady=5)

        # Turn indicator
        self.turn_label = tk.Label(
            self.root,
            text="Player X's Turn",
            font=("Helvetica", 13),
            bg="#1a1a2e", fg="#00d4ff"
        )
        self.turn_label.pack(pady=5)

        # Mode toggle buttons frame
        mode_frame = tk.Frame(self.root, bg="#1a1a2e")
        mode_frame.pack(pady=5)

        tk.Label(mode_frame, text="Mode: ",
                 font=("Helvetica", 11),
                 bg="#1a1a2e", fg="#a0a0b0").grid(row=0, column=0)

        self.pvp_btn = tk.Button(
            mode_frame,
            text="👥 2 Players",
            font=("Helvetica", 10),
            bg="#00d4ff", fg="black",
            relief="flat", padx=8, pady=3,
            command=self.set_pvp
        )
        self.pvp_btn.grid(row=0, column=1, padx=5)

        self.ai_btn = tk.Button(
            mode_frame,
            text="🤖 vs AI",
            font=("Helvetica", 10),
            bg="#16213e", fg="white",
            relief="flat", padx=8, pady=3,
            command=self.set_ai
        )
        self.ai_btn.grid(row=0, column=2, padx=5)

        # Grid frame
        frame = tk.Frame(self.root, bg="#16213e")
        frame.pack(pady=10)

        for i in range(9):
            btn = tk.Button(
                frame,
                text="",
                font=("Helvetica", 30, "bold"),
                width=4, height=2,
                bg="#16213e", fg="white",
                activebackground="#0f3460",
                relief="ridge", bd=3,
                command=lambda i=i: self.on_click(i)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        # Restart button
        tk.Button(
            self.root,
            text="🔄 Restart",
            font=("Helvetica", 12),
            bg="#e94560", fg="white",
            activebackground="#c73652",
            relief="flat", padx=10, pady=5,
            command=self.reset_board
        ).pack(pady=15)

    # --- Mode Switchers ---
    def set_pvp(self):
        self.vs_ai = False
        self.pvp_btn.config(bg="#00d4ff", fg="black")
        self.ai_btn.config(bg="#16213e", fg="white")
        self.reset_board()

    def set_ai(self):
        self.vs_ai = True
        self.ai_btn.config(bg="#e94560", fg="white")
        self.pvp_btn.config(bg="#16213e", fg="white")
        self.reset_board()

    # --- Human Click ---
    def on_click(self, index):
        if self.board[index] != "":
            return
        if self.vs_ai and self.current_player == "O":
            return  # block click during AI turn

        self.make_move(index, self.current_player)

        if self.vs_ai and not self.game_ended():
            self.root.after(400, self.ai_move)  # AI plays after 400ms delay

    # --- Make a Move ---
    def make_move(self, index, player):
        self.board[index] = player
        color = "#00d4ff" if player == "X" else "#e94560"
        self.buttons[index].config(text=player, fg=color)

        if self.check_winner(player):
            self.score[player] += 1
            self.score_label.config(
                text=f"X: {self.score['X']}  |  O: {self.score['O']}"
            )
            winner_text = "You win! 🎉" if player == "X" else (
                "AI wins! 🤖" if self.vs_ai else "Player O wins! 🎉"
            )
            messagebox.showinfo("Game Over", winner_text)
            self.reset_board()
            return

        if "" not in self.board:
            messagebox.showinfo("Draw!", "It's a draw! 🤝")
            self.reset_board()
            return

        self.current_player = "O" if player == "X" else "X"
        if self.vs_ai and self.current_player == "O":
            self.turn_label.config(text="🤖 AI is thinking...")
        else:
            self.turn_label.config(text=f"Player {self.current_player}'s Turn")

    # --- AI Move using Minimax ---
    def ai_move(self):
        best_score = -float("inf")
        best_index = None

        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "O"
                score = self.minimax(self.board, False)
                self.board[i] = ""
                if score > best_score:
                    best_score = score
                    best_index = i

        if best_index is not None:
            self.make_move(best_index, "O")

    # --- Minimax Algorithm ---
    def minimax(self, board, is_maximizing):
        if self.check_winner_board(board, "O"):
            return 1
        if self.check_winner_board(board, "X"):
            return -1
        if "" not in board:
            return 0

        if is_maximizing:
            best = -float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = "O"
                    best = max(best, self.minimax(board, False))
                    board[i] = ""
            return best
        else:
            best = float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = "X"
                    best = min(best, self.minimax(board, True))
                    board[i] = ""
            return best

    # --- Winner Check (on board list) ---
    def check_winner_board(self, board, player):
        wins = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        return any(board[a] == board[b] == board[c] == player
                   for a, b, c in wins)

    # --- Winner Check (on UI + highlight) ---
    def check_winner(self, player):
        wins = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        for combo in wins:
            a, b, c = combo
            if (self.board[a] == self.board[b] == self.board[c] == player):
                for idx in combo:
                    self.buttons[idx].config(bg="#0f3460")
                return True
        return False

    def game_ended(self):
        return ("" not in self.board or
                self.check_winner_board(self.board, "X") or
                self.check_winner_board(self.board, "O"))

    # --- Reset ---
    def reset_board(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.turn_label.config(text="Player X's Turn")
        for btn in self.buttons:
            btn.config(text="", bg="#16213e")

# Start
TicTacToe()