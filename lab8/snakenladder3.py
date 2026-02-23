import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import math
import random
import heapq
from collections import deque
from typing import Dict, List, Tuple
from PIL import Image, ImageTk, ImageDraw  # Requires: pip install pillow
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
#  CONFIGURATION & THEME
# ==========================================
THEME = {
    "bg": "#f4f6f9",           
    "panel_bg": "#ffffff",
    "board_bg_1": "#ffffff",
    "board_bg_2": "#E3F2FD",   
    "snake_body": "#43A047",   
    "snake_outline": "#1B5E20",
    "ladder_wood": "#795548",  
    "ladder_shadow": "#3E2723",
    "player": "#D32F2F",     
    "highlight": "#FFC107",
    "dice_bg": "#333333",
    "dice_fg": "#00FF00"
}

# ==========================================
#  CORE LOGIC (GRAPH ALGORITHMS)
# ==========================================
class SnakeLadderGame:
    def __init__(self, board_size=100):
        self.board_size = board_size
        # Standard "Hard" Layout - LOGIC IS HERE
        self.snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
        self.ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

    def get_next_positions(self, current_pos):
        positions = []
        for dice in range(1, 7):
            next_pos = current_pos + dice
            if next_pos in self.snakes: next_pos = self.snakes[next_pos]
            elif next_pos in self.ladders: next_pos = self.ladders[next_pos]
            if next_pos <= self.board_size: positions.append(next_pos)
        return positions

    def reverse_engineer_dice(self, current, next_spot):
        """
        Helper to figure out what dice roll caused the move.
        Since we might have jumped via snake/ladder, we check all 1-6 possibilities.
        """
        for dice in range(1, 7):
            temp = current + dice
            # Simulate snake/ladder logic
            if temp in self.snakes: temp = self.snakes[temp]
            elif temp in self.ladders: temp = self.ladders[temp]
            
            if temp == next_spot:
                return dice
        return 1 # Default fallback

class GameAI:
    def __init__(self, game):
        self.game = game

    def bfs_search(self, start, target):
        queue = deque([(start, [start])])
        visited = {start}
        nodes = 0
        while queue:
            curr, path = queue.popleft()
            nodes += 1
            if curr == target: return path, nodes
            for nxt in self.game.get_next_positions(curr):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return [], nodes

    def dfs_search(self, start, target):
        stack = [(start, [start])]
        visited = {start}
        nodes = 0
        while stack:
            curr, path = stack.pop()
            nodes += 1
            if curr == target: return path, nodes
            for nxt in reversed(self.game.get_next_positions(curr)):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append((nxt, path + [nxt]))
        return [], nodes

    def a_star_search(self, start, target):
        pq = [(0, start, [start])]
        g_score = {start: 0}
        nodes = 0
        while pq:
            _, curr, path = heapq.heappop(pq)
            nodes += 1
            if curr == target: return path, nodes
            
            tentative_g = g_score[curr] + 1
            for nxt in self.game.get_next_positions(curr):
                if nxt not in g_score or tentative_g < g_score[nxt]:
                    g_score[nxt] = tentative_g
                    f = tentative_g + (target - nxt) / 6
                    heapq.heappush(pq, (f, nxt, path + [nxt]))
        return [], nodes

# ==========================================
#  MODERN UI WITH DICE & IMAGES
# ==========================================
class SuperSnakeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Ultimate Snake & Ladder AI | Innovation Project")
        self.root.geometry("1280x760")
        self.root.configure(bg=THEME["bg"])
        
        self.game = SnakeLadderGame()
        self.ai = GameAI(self.game)
        self.stats = {'BFS': [], 'DFS': [], 'A*': []}
        self.custom_bg_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- LEFT: THE BOARD ---
        self.board_frame = tk.Frame(self.root, bg=THEME["bg"], padx=20, pady=20)
        self.board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.board_frame, width=650, height=650, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True)
        self.draw_default_board()

        # --- RIGHT: CONTROL CENTER ---
        self.panel = tk.Frame(self.root, bg=THEME["panel_bg"], width=400, relief=tk.RAISED, bd=1)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        # 1. Header
        tk.Label(self.panel, text="GAME CONTROL", font=("Helvetica", 14, "bold"), bg=THEME["panel_bg"], fg="#333").pack(pady=(20, 10))

        # 2. Controls
        ctrl_frame = tk.LabelFrame(self.panel, text="Settings", bg=THEME["panel_bg"], font=("Arial", 10, "bold"), padx=10, pady=10)
        ctrl_frame.pack(fill=tk.X, padx=20)
        
        self.algo_var = tk.StringVar(value="BFS")
        tk.Label(ctrl_frame, text="Strategy:", bg=THEME["panel_bg"]).pack(anchor="w")
        for text, val in [("BFS (Shortest)", "BFS"), ("DFS (Explorer)", "DFS"), ("A* (Heuristic)", "A*")]:
            tk.Radiobutton(ctrl_frame, text=text, variable=self.algo_var, value=val, bg=THEME["panel_bg"]).pack(anchor="w")

        tk.Label(ctrl_frame, text="Animation Speed:", bg=THEME["panel_bg"]).pack(anchor="w", pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=1.0)
        tk.Scale(ctrl_frame, from_=0.5, to=5.0, orient=tk.HORIZONTAL, variable=self.speed_var, bg=THEME["panel_bg"]).pack(fill=tk.X)

        # 3. Dice Display (NEW FEATURE)
        dice_frame = tk.LabelFrame(self.panel, text="Live Dice Roll", bg=THEME["panel_bg"], font=("Arial", 10, "bold"), padx=10, pady=10)
        dice_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.dice_label = tk.Label(dice_frame, text="🎲", font=("Arial", 40), bg=THEME["dice_bg"], fg=THEME["dice_fg"], width=4)
        self.dice_label.pack()
        
        self.move_info_var = tk.StringVar(value="Waiting to roll...")
        tk.Label(dice_frame, textvariable=self.move_info_var, bg=THEME["panel_bg"], fg="#555").pack(pady=5)

        # 4. Image Options
        img_frame = tk.LabelFrame(self.panel, text="Board Appearance", bg=THEME["panel_bg"], font=("Arial", 10, "bold"), padx=10, pady=10)
        img_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Button(img_frame, text="🖼️ Upload Board Image", command=self.upload_image, bg="#607D8B", fg="white").pack(fill=tk.X, pady=2)
        self.show_assets_var = tk.BooleanVar(value=True)
        tk.Checkbutton(img_frame, text="Show Generated Assets", variable=self.show_assets_var, command=self.refresh_board, bg=THEME["panel_bg"]).pack(anchor="w")

        # 5. Buttons & Graphs
        btn_frame = tk.Frame(self.panel, bg=THEME["panel_bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="▶ RUN SOLVER", bg="#4CAF50", fg="white", command=self.run_visual_search).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="📊 COMPARE ALL", bg="#2196F3", fg="white", command=self.run_comparison).pack(fill=tk.X, pady=2)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(3.5, 3))
        self.fig.patch.set_facecolor('white')
        self.chart = FigureCanvasTkAgg(self.fig, self.panel)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    # ==========================================
    #  GRAPHICS & IMAGE HANDLING
    # ==========================================
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((650, 650), Image.Resampling.LANCZOS)
                self.custom_bg_image = ImageTk.PhotoImage(img)
                self.refresh_board()
                messagebox.showinfo("Note", "Image Loaded!\n\nRemember: The AI follows the internal logic (Snakes at 16, 47, etc.), not the drawing on your image.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")

    def get_coords(self, pos):
        row = (pos - 1) // 10
        col = (pos - 1) % 10
        if row % 2 == 1: col = 9 - col
        x = col * 65 + 32.5
        y = (9 - row) * 65 + 32.5
        return x, y

    def refresh_board(self):
        self.canvas.delete("all")
        if self.custom_bg_image:
            self.canvas.create_image(0, 0, image=self.custom_bg_image, anchor="nw")
        else:
            self.draw_default_board_grid()

        if self.show_assets_var.get():
            self.draw_assets()
        
        self.token = self.canvas.create_oval(-20, -20, 0, 0, fill=THEME["player"], outline="white", width=2)

    def draw_default_board_grid(self):
        for i in range(10):
            for j in range(10):
                x1, y1 = j*65, i*65
                x2, y2 = x1+65, y1+65
                color = THEME["board_bg_1"] if (i+j)%2==0 else THEME["board_bg_2"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ddd")
                row_idx = 9 - i
                num = row_idx*10 + j + 1 if row_idx % 2 == 0 else row_idx*10 + (9-j) + 1
                self.canvas.create_text(x1+10, y1+15, text=str(num), font=("Arial", 9, "bold"), fill="#aaa")

    def draw_default_board(self):
        self.draw_default_board_grid()
        self.draw_assets()
        self.token = self.canvas.create_oval(-20, -20, 0, 0, fill=THEME["player"], outline="white", width=2)

    def draw_assets(self):
        for s, e in self.game.snakes.items(): self.draw_curved_snake(s, e)
        for s, e in self.game.ladders.items(): self.draw_3d_ladder(s, e)

    def draw_curved_snake(self, start, end):
        sx, sy = self.get_coords(start)
        ex, ey = self.get_coords(end)
        cx1, cy1 = (sx + ex) / 2 + 40, (sy + ey) / 2
        cx2, cy2 = (sx + ex) / 2 - 40, (sy + ey) / 2
        self.canvas.create_line(sx, sy, cx1, cy1, cx2, cy2, ex, ey, smooth=True, width=10, fill=THEME["snake_body"])
        self.canvas.create_oval(sx-8, sy-8, sx+8, sy+8, fill=THEME["snake_outline"])

    def draw_3d_ladder(self, start, end):
        sx, sy = self.get_coords(start)
        ex, ey = self.get_coords(end)
        self.canvas.create_line(sx-6, sy, ex-6, ey, width=4, fill=THEME["ladder_wood"])
        self.canvas.create_line(sx+6, sy, ex+6, ey, width=4, fill=THEME["ladder_wood"])
        steps = int(math.hypot(ex-sx, ey-sy) / 20)
        for i in range(steps):
            t = i / steps
            rx, ry = sx + (ex-sx)*t, sy + (ey-sy)*t
            self.canvas.create_line(rx-6, ry, rx+6, ry, width=3, fill=THEME["ladder_wood"])

    # ==========================================
    #  ANIMATIONS
    # ==========================================
    def animate_dice_roll(self, final_value):
        """Simulate rolling dice by flashing numbers"""
        for _ in range(5):
            self.dice_label.config(text=str(random.randint(1, 6)), fg="#888")
            self.root.update()
            time.sleep(0.05)
        
        # Show Final Value
        self.dice_label.config(text=str(final_value), fg=THEME["dice_fg"])
        self.root.update()

    def animate_move(self, path):
        # Place token at start
        sx, sy = self.get_coords(path[0])
        self.canvas.coords(self.token, sx-10, sy-10, sx+10, sy+10)
        self.root.update()
        
        speed = self.speed_var.get()
        
        for i in range(len(path)-1):
            curr_pos = path[i]
            next_pos = path[i+1]
            
            # 1. Calculate and Show Dice
            dice_val = self.game.reverse_engineer_dice(curr_pos, next_pos)
            self.move_info_var.set(f"Moving {curr_pos} -> {next_pos}")
            self.animate_dice_roll(dice_val)
            
            time.sleep(0.3 / speed) # Pause to let user see dice
            
            # 2. Animate Movement
            sx, sy = self.get_coords(curr_pos)
            ex, ey = self.get_coords(next_pos)
            
            steps = 15
            for s in range(steps):
                t = s / steps
                cx = sx + (ex - sx) * t
                cy = sy + (ey - sy) * t
                self.canvas.coords(self.token, cx-10, cy-10, cx+10, cy+10)
                self.canvas.update()
                time.sleep(0.02 / speed)
            
            # Snap to grid
            self.canvas.coords(self.token, ex-10, ey-10, ex+10, ey+10)
            self.root.update()
            time.sleep(0.1 / speed)

    def run_visual_search(self):
        algo = self.algo_var.get()
        if algo == "BFS": path, nodes = self.ai.bfs_search(1, 100)
        elif algo == "DFS": path, nodes = self.ai.dfs_search(1, 100)
        else: path, nodes = self.ai.a_star_search(1, 100)
        
        if not path:
            messagebox.showerror("Error", "No path found!")
            return
            
        self.animate_move(path)

    def run_comparison(self):
        nodes_data, len_data = {}, {}
        for algo in ['BFS', 'DFS', 'A*']:
            if algo == "BFS": p, n = self.ai.bfs_search(1, 100)
            elif algo == "DFS": p, n = self.ai.dfs_search(1, 100)
            else: p, n = self.ai.a_star_search(1, 100)
            nodes_data[algo] = n
            len_data[algo] = len(p)
            
        self.ax1.clear(); self.ax2.clear()
        self.ax1.bar(nodes_data.keys(), nodes_data.values(), color='#42A5F5')
        self.ax1.set_title("Nodes Explored")
        self.ax2.bar(len_data.keys(), len_data.values(), color='#66BB6A')
        self.ax2.set_title("Path Length")
        self.fig.tight_layout()
        self.chart.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperSnakeGUI(root)
    root.mainloop()