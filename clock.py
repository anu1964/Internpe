import tkinter as tk
from datetime import datetime

def update_clock():
    now = datetime.now().strftime("%H : %M : %S")
    date = datetime.now().strftime("%A, %d %B %Y")
    time_label.config(text=now)
    date_label.config(text=date)
    root.after(1000, update_clock)

# Window setup
root = tk.Tk()
root.title("Digital Clock")
root.geometry("500x250")
root.configure(bg="#1a1a2e")
root.resizable(False, False)

# Title
title_label = tk.Label(root, text="🕐 Digital Clock",
                        font=("Helvetica", 16),
                        bg="#1a1a2e", fg="#e94560")
title_label.pack(pady=(20, 0))

# Time display
time_label = tk.Label(root, font=("Courier", 55, "bold"),
                       bg="#1a1a2e", fg="#00d4ff")
time_label.pack(pady=10)

# Date display
date_label = tk.Label(root, font=("Helvetica", 14),
                       bg="#1a1a2e", fg="#a0a0b0")
date_label.pack()

update_clock()
root.mainloop()