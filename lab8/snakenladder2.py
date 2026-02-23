import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
import random
import heapq
from collections import deque
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
#  CONFIGURATION & THEME
# ==========================================
THEME = {
    "bg": "#E6F2F5",           # Light Blue-Grey Background
    "board_bg_1": "#FFFFFF",   # White Tile
    "board_bg_2": "#E0F7FA",   # Cyan Tint Tile
    "snake_body": "#4CAF50",   # Jungle Green
    "snake_outline": "#1B5E20",# Dark Green
    "ladder_wood": "#8D6E63",  # Brown
    "ladder_shadow": "#5D4037",# Dark Brown
    "player_1": "#FF5252",     # Red
    "player_2": "#2196F3",     # Blue (AI)
    "highlight": "#FFEB3B"     # Yellow Glow
}

# ==========================================
#  CORE LOGIC (GRAPH ALGORITHMS)
# ==========================================
class SnakeLadderGame:
    def __init__(self, board_size=100):
        self.board_size = board_size
        # Professional "Hard" Layout
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
            
            # Heuristic: Distance / 6 (Max movement)
            tentative_g = g_score[curr] + 1
            for nxt in self.game.get_next_positions(curr):
                if nxt not in g_score or tentative_g < g_score[nxt]:
                    g_score[nxt] = tentative_g
                    f = tentative_g + (target - nxt) / 6
                    heapq.heappush(pq, (f, nxt, path + [nxt]))
        return [], nodes

# ==========================================
#  MODERN UI (THE INNOVATION)
# ==========================================
class SuperSnakeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Ultimate Snake & Ladder AI | Innovation Project")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME["bg"])
        
        self.game = SnakeLadderGame()
        self.ai = GameAI(self.game)
        self.stats = {'BFS': [], 'DFS': [], 'A*': []}
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- LEFT: THE BOARD ---
        self.board_frame = tk.Frame(self.root, bg=THEME["bg"], padx=20, pady=20)
        self.board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas with a "Card" look (Shadow effect via borders)
        self.canvas = tk.Canvas(self.board_frame, width=650, height=650, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True)
        self.draw_board_grid()
        self.draw_assets() # The magic happens here

        # --- RIGHT: CONTROL CENTER ---
        self.panel = tk.Frame(self.root, bg="white", width=400)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        # 1. Header
        lbl_title = tk.Label(self.panel, text="GAME CONTROL", font=("Helvetica", 16, "bold"), bg="white", fg="#333")
        lbl_title.pack(pady=(20, 10))

        # 2. Controls
        ctrl_frame = tk.LabelFrame(self.panel, text="AI Strategy", bg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        ctrl_frame.pack(fill=tk.X, padx=20)
        
        self.algo_var = tk.StringVar(value="BFS")
        modes = [("BFS (Shortest)", "BFS"), ("DFS (Explorer)", "DFS"), ("A* (Smart)", "A*")]
        for text, val in modes:
            tk.Radiobutton(ctrl_frame, text=text, variable=self.algo_var, value=val, bg="white", activebackground="white").pack(anchor="w")

        # 3. Action Buttons
        btn_frame = tk.Frame(self.panel, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.btn_run = tk.Button(btn_frame, text="▶ RUN AI SOLVER", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                                 relief=tk.FLAT, padx=10, pady=8, command=self.run_visual_search)
        self.btn_run.pack(fill=tk.X, pady=5)
        
        self.btn_comp = tk.Button(btn_frame, text="📊 COMPARE ALL", bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                                  relief=tk.FLAT, padx=10, pady=8, command=self.run_comparison)
        self.btn_comp.pack(fill=tk.X, pady=5)

        # 4. Logs
        self.log_lbl = tk.Label(self.panel, text="Ready to play...", bg="#f0f0f0", fg="#555", height=2, relief=tk.SUNKEN)
        self.log_lbl.pack(fill=tk.X, padx=20, pady=10)

        # 5. Graphs
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(3.5, 4.5))
        self.fig.patch.set_facecolor('white')
        self.chart = FigureCanvasTkAgg(self.fig, self.panel)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.update_charts({'BFS':0, 'DFS':0, 'A*':0}, {'BFS':0, 'DFS':0, 'A*':0})

    # ==========================================
    #  ADVANCED GRAPHICS GENERATION
    # ==========================================
    def get_coords(self, pos):
        """Converts board number (1-100) to pixel (x,y) with Zig-Zag logic"""
        row = (pos - 1) // 10
        col = (pos - 1) % 10
        if row % 2 == 1: col = 9 - col
        x = col * 65 + 32.5
        y = (9 - row) * 65 + 32.5
        return x, y

    def draw_board_grid(self):
        """Draws a chessboard-style grid with modern typography"""
        for i in range(10):
            for j in range(10):
                x1, y1 = j*65, i*65
                x2, y2 = x1+65, y1+65
                color = THEME["board_bg_1"] if (i+j)%2==0 else THEME["board_bg_2"]
                
                # Tile
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ddd")
                
                # Number Logic
                row_idx = 9 - i
                if row_idx % 2 == 0: num = row_idx*10 + j + 1
                else: num = row_idx*10 + (9-j) + 1
                
                # Styled Text
                self.canvas.create_text(x1+10, y1+15, text=str(num), font=("Arial", 9, "bold"), fill="#aaa")

    def draw_curved_snake(self, start, end):
        """Draws a procedurally generated Snake with Bezier curves"""
        sx, sy = self.get_coords(start)
        ex, ey = self.get_coords(end)
        
        # Control points for "S" curve
        cx1 = (sx + ex) / 2 + 40
        cy1 = (sy + ey) / 2
        cx2 = (sx + ex) / 2 - 40
        cy2 = (sy + ey) / 2
        
        # 1. Shadow (for depth)
        self.canvas.create_line(sx, sy, cx1, cy1, cx2, cy2, ex, ey, smooth=True, width=12, fill="#aaa")
        # 2. Body
        self.canvas.create_line(sx, sy, cx1, cy1, cx2, cy2, ex, ey, smooth=True, width=10, fill=THEME["snake_body"], capstyle=tk.ROUND)
        # 3. Pattern (Stripes)
        self.canvas.create_line(sx, sy, cx1, cy1, cx2, cy2, ex, ey, smooth=True, width=2, fill=THEME["snake_outline"], dash=(2, 4))
        
        # 4. Head (at Start)
        self.canvas.create_oval(sx-10, sy-10, sx+10, sy+10, fill=THEME["snake_outline"])
        self.canvas.create_oval(sx-4, sy-4, sx-1, sy-1, fill="white") # Eye 1
        self.canvas.create_oval(sx+1, sy-4, sx+4, sy-1, fill="white") # Eye 2
        self.canvas.create_line(sx, sy+5, sx, sy+12, fill="red", width=2) # Tongue

    def draw_3d_ladder(self, start, end):
        """Draws a realistic ladder with perspective"""
        sx, sy = self.get_coords(start)
        ex, ey = self.get_coords(end)
        
        # Main Rails
        self.canvas.create_line(sx-8, sy, ex-8, ey, width=4, fill=THEME["ladder_wood"])
        self.canvas.create_line(sx+8, sy, ex+8, ey, width=4, fill=THEME["ladder_wood"])
        
        # Rungs (Steps) - Calculated mathematically along the vector
        steps = int(math.hypot(ex-sx, ey-sy) / 20)
        for i in range(steps):
            t = i / steps
            rx = sx + (ex-sx)*t
            ry = sy + (ey-sy)*t
            # Shadow for 3D effect
            self.canvas.create_line(rx-8, ry+2, rx+8, ry+2, width=3, fill=THEME["ladder_shadow"])
            self.canvas.create_line(rx-8, ry, rx+8, ry, width=3, fill=THEME["ladder_wood"])

    def draw_assets(self):
        # Draw all Snakes and Ladders
        for start, end in self.game.ladders.items():
            self.draw_3d_ladder(start, end)
        for start, end in self.game.snakes.items():
            self.draw_curved_snake(start, end)
            
        # Player Token (Hidden initially)
        self.token = self.canvas.create_oval(-20, -20, 0, 0, fill=THEME["player_1"], outline="white", width=2)
        self.token_glow = self.canvas.create_oval(-20, -20, 0, 0, outline=THEME["highlight"], width=3, state='hidden')

    # ==========================================
    #  ANIMATIONS & GAMEPLAY
    # ==========================================
    def animate_move(self, path):
        """Smooth slide animation"""
        for pos in path:
            tx, ty = self.get_coords(pos)
            
            # 1. Move Token Smoothly (Interpolation)
            cur_coords = self.canvas.coords(self.token)
            cur_x, cur_y = (cur_coords[0]+cur_coords[2])/2, (cur_coords[1]+cur_coords[3])/2
            
            steps = 5
            dx = (tx - cur_x) / steps
            dy = (ty - cur_y) / steps
            
            for _ in range(steps):
                self.canvas.move(self.token, dx, dy)
                self.canvas.update()
                time.sleep(0.01)
            
            # Snap to grid to be precise
            self.canvas.coords(self.token, tx-10, ty-10, tx+10, ty+10)
            self.root.update()
            time.sleep(0.1)

    def run_visual_search(self):
        algo = self.algo_var.get()
        self.log_lbl.config(text=f"🤖 Computing {algo} Path...", bg="#FFF3E0")
        self.root.update()
        
        # Run Algorithm
        start_time = time.time()
        if algo == "BFS": path, nodes = self.ai.bfs_search(1, 100)
        elif algo == "DFS": path, nodes = self.ai.dfs_search(1, 100)
        else: path, nodes = self.ai.a_star_search(1, 100)
        duration = time.time() - start_time
        
        if not path:
            messagebox.showerror("Error", "No path found!")
            return
            
        # Reset Token
        sx, sy = self.get_coords(1)
        self.canvas.coords(self.token, sx-10, sy-10, sx+10, sy+10)
        
        # Animate
        self.animate_move(path)
        
        # Update Log
        self.log_lbl.config(text=f"✅ {algo}: {len(path)-1} moves | {nodes} nodes | {duration:.4f}s", bg="#E8F5E9")

    def run_comparison(self):
        self.log_lbl.config(text="📊 Running Benchmark...", bg="#E3F2FD")
        self.root.update()
        
        nodes_data = {}
        len_data = {}
        
        for algo in ['BFS', 'DFS', 'A*']:
            if algo == "BFS": p, n = self.ai.bfs_search(1, 100)
            elif algo == "DFS": p, n = self.ai.dfs_search(1, 100)
            else: p, n = self.ai.a_star_search(1, 100)
            nodes_data[algo] = n
            len_data[algo] = len(p)
            
        self.update_charts(nodes_data, len_data)
        self.log_lbl.config(text="Benchmark Complete!", bg="#E8F5E9")

    def update_charts(self, nodes, lengths):
        self.ax1.clear()
        self.ax2.clear()
        
        colors = ['#FF7043', '#42A5F5', '#66BB6A']
        names = list(nodes.keys())
        
        # Chart 1: Nodes Explored (Efficiency)
        self.ax1.bar(names, list(nodes.values()), color=colors)
        self.ax1.set_title("Computational Cost (Nodes Explored)", fontsize=8)
        self.ax1.tick_params(axis='both', labelsize=8)
        
        # Chart 2: Path Length (Optimality)
        self.ax2.bar(names, list(lengths.values()), color=colors)
        self.ax2.set_title("Solution Quality (Moves to Win)", fontsize=8)
        self.ax2.tick_params(axis='both', labelsize=8)
        
        self.fig.tight_layout()
        self.chart.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperSnakeGUI(root)
    root.mainloop()