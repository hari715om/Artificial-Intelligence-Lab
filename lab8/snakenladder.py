import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
import random
from collections import deque
import heapq
from typing import Dict, List, Tuple
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# CORE GAME LOGIC
# ==========================================

class SnakeLadderGame:
    def __init__(self, board_size: int, snakes: Dict[int, int], ladders: Dict[int, int]):
        self.board_size = board_size
        self.snakes = snakes
        self.ladders = ladders

    def get_next_positions(self, current_pos: int) -> List[int]:
        """Returns possible next positions from current position after dice roll (1-6)."""
        positions = []
        for dice in range(1, 7):  # dice values 1-6
            next_pos = current_pos + dice
            
            # Check for Snake or Ladder
            if next_pos in self.snakes:
                next_pos = self.snakes[next_pos]
            elif next_pos in self.ladders:
                next_pos = self.ladders[next_pos]
            
            # Ensure we don't go off board
            if next_pos <= self.board_size:
                positions.append(next_pos)
        return positions

# ==========================================
# AI AGENT (The Brains)
# ==========================================

class GameAI:
    def __init__(self, game: SnakeLadderGame):
        self.game = game

    def bfs_search(self, start: int, target: int) -> Tuple[List[int], int]:
        """
        Breadth-First Search: Guarantees the Shortest Path (Minimum Dice Rolls).
        """
        queue = deque([(start, [start])])
        visited = {start}
        nodes_explored = 0

        while queue:
            current_pos, path = queue.popleft()
            nodes_explored += 1

            if current_pos == target:
                return path, nodes_explored

            for next_pos in self.game.get_next_positions(current_pos):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        return [], nodes_explored

    def dfs_search(self, start: int, target: int) -> Tuple[List[int], int]:
        """
        Depth-First Search: Explores deep paths first. Often inefficient for this game.
        """
        stack = [(start, [start])]
        visited = {start}
        nodes_explored = 0

        while stack:
            current_pos, path = stack.pop()
            nodes_explored += 1

            if current_pos == target:
                return path, nodes_explored

            # Reversed to simulate left-to-right expansion often used in trees
            for next_pos in reversed(self.game.get_next_positions(current_pos)):
                if next_pos not in visited:
                    visited.add(next_pos)
                    stack.append((next_pos, path + [next_pos]))
        return [], nodes_explored

    def heuristic(self, pos: int, target: int) -> float:
        """A* Heuristic: Minimum possible rolls to finish = (distance / 6)"""
        return (target - pos) / 6

    def a_star_search(self, start: int, target: int) -> Tuple[List[int], int]:
        """
        A* Search: Uses heuristics to find the path faster than BFS in complex graphs.
        """
        # Priority Queue stores: (f_score, current_pos, path)
        pq = [(self.heuristic(start, target), start, [start])]
        g_score = {start: 0}  # Cost from start to node
        visited = set()
        nodes_explored = 0

        while pq:
            _, current_pos, path = heapq.heappop(pq)
            
            if current_pos in visited:
                continue
            visited.add(current_pos)
            nodes_explored += 1

            if current_pos == target:
                return path, nodes_explored

            # Cost to move is always 1 (one dice roll)
            tentative_g = g_score[current_pos] + 1

            for next_pos in self.game.get_next_positions(current_pos):
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    g_score[next_pos] = tentative_g
                    f_score = tentative_g + self.heuristic(next_pos, target)
                    heapq.heappush(pq, (f_score, next_pos, path + [next_pos]))
        
        return [], nodes_explored

# ==========================================
# GUI (The Visualization)
# ==========================================

class SnakeLadderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake and Ladder AI Solver - Innovation Project")
        self.root.geometry("1100x700")

        # Game Config
        self.board_size = 100
        self.grid_size = 10
        self.cell_size = 60
        
        # --- GAME DATA ---
        self.snakes = {
            16: 6, 47: 26, 49: 11, 56: 53, 
            62: 19, 64: 60, 87: 24, 93: 73, 
            95: 75, 98: 78
        }
        self.ladders = {
            1: 38, 4: 14, 9: 31, 21: 42, 
            28: 84, 36: 44, 51: 67, 71: 91, 
            80: 100
        }

        # Stats Storage
        self.stats = {
            'BFS': {'nodes': [], 'path_len': []}, 
            'DFS': {'nodes': [], 'path_len': []}, 
            'A*':  {'nodes': [], 'path_len': []}
        }

        # Initialize Logic
        self.game = SnakeLadderGame(self.board_size, self.snakes, self.ladders)
        self.ai = GameAI(self.game)

        self.setup_ui()
        self.create_board()

    def setup_ui(self):
        # Main Layout
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(expand=True, fill=tk.BOTH)

        # Left: Board
        self.board_frame = tk.Frame(self.main_container, bg="white", bd=2, relief=tk.SUNKEN)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Right: Controls & Stats
        self.right_panel = tk.Frame(self.main_container)
        self.right_panel.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 1. Controls
        self.control_frame = tk.LabelFrame(self.right_panel, text="AI Controls", font=("Arial", 12, "bold"))
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(self.control_frame, text="Select Algorithm:").pack(anchor=tk.W, padx=5)
        self.algorithm_var = tk.StringVar(value="BFS")
        
        btn_frame = tk.Frame(self.control_frame)
        btn_frame.pack(fill=tk.X)
        
        for algo in ["BFS", "DFS", "A*"]:
            tk.Radiobutton(btn_frame, text=algo, variable=self.algorithm_var, value=algo).pack(side=tk.LEFT, padx=10)

        self.btn_run = tk.Button(self.control_frame, text="▶ Start Visualization", bg="#4CAF50", fg="white", command=self.start_search)
        self.btn_run.pack(pady=5, fill=tk.X, padx=5)

        self.btn_compare = tk.Button(self.control_frame, text="📊 Compare All Algorithms", bg="#2196F3", fg="white", command=self.run_comparison)
        self.btn_compare.pack(pady=5, fill=tk.X, padx=5)

        self.speed_var = tk.DoubleVar(value=1.0)
        tk.Scale(self.control_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, label="Animation Speed", variable=self.speed_var).pack(fill=tk.X, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.control_frame, textvariable=self.status_var, fg="blue").pack(pady=5)

        # 2. Stats
        self.stats_frame = tk.LabelFrame(self.right_panel, text="Performance Metrics")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.setup_stats_plots()

    def setup_stats_plots(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(4, 5))
        self.fig.patch.set_facecolor('#f0f0f0')
        self.stats_canvas = FigureCanvasTkAgg(self.fig, master=self.stats_frame)
        self.stats_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update_stats_plots()

    def update_stats_plots(self):
        self.ax1.clear()
        self.ax2.clear()
        
        algos = ['BFS', 'DFS', 'A*']
        # Use existing data or 0 if empty
        nodes = [np.mean(self.stats[a]['nodes']) if self.stats[a]['nodes'] else 0 for a in algos]
        paths = [np.mean(self.stats[a]['path_len']) if self.stats[a]['path_len'] else 0 for a in algos]

        # Plot 1: Efficiency (Nodes Explored)
        self.ax1.bar(algos, nodes, color=['#FF9999', '#66B2FF', '#99FF99'])
        self.ax1.set_title('Computational Cost (Nodes Explored)', fontsize=9)
        
        # Plot 2: Optimality (Path Length)
        self.ax2.bar(algos, paths, color=['#FF9999', '#66B2FF', '#99FF99'])
        self.ax2.set_title('Solution Quality (Path Length)', fontsize=9)
        
        self.fig.tight_layout()
        self.stats_canvas.draw()

    def create_board(self):
        self.board_canvas = tk.Canvas(self.board_frame, width=600, height=600, bg="white")
        self.board_canvas.pack()

        # Draw Grid
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = (self.grid_size - 1 - i) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Checkboard color
                color = "#E8E8E8" if (i + j) % 2 == 0 else "white"
                
                # Calculate Board Number (Zig-Zag)
                if i % 2 == 0: # Even rows (0, 2, 4...) go Left to Right
                    num = i * 10 + j + 1
                else:          # Odd rows (1, 3, 5...) go Right to Left
                    num = i * 10 + (9 - j) + 1

                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ccc")
                self.board_canvas.create_text((x1+x2)/2, (y1+y2)/2, text=str(num), font=('Arial', 10, 'bold'), fill="#aaa")

        self.draw_snakes_and_ladders()
        self.token = self.board_canvas.create_oval(0,0,0,0, fill="gold", outline="black", width=2)
        # Hide token initially
        self.board_canvas.coords(self.token, -20, -20, -10, -10)

    def get_coords(self, position):
        """Converts board position (1-100) to Canvas (x, y)"""
        if position < 1: position = 1
        if position > 100: position = 100
        
        # 0-indexed logic
        idx = position - 1
        row = idx // 10
        col = idx % 10

        # Zig-Zag logic for columns
        if row % 2 == 1:
            col = 9 - col
            
        # Coordinates
        x = col * self.cell_size + self.cell_size // 2
        y = (9 - row) * self.cell_size + self.cell_size // 2
        return x, y

    def draw_snakes_and_ladders(self):
        # Draw Snakes (Red)
        for start, end in self.snakes.items():
            sx, sy = self.get_coords(start)
            ex, ey = self.get_coords(end)
            self.board_canvas.create_line(sx, sy, ex, ey, fill="#FF5252", width=4, arrow=tk.LAST, smooth=True)
            self.board_canvas.create_oval(sx-5, sy-5, sx+5, sy+5, fill="red") # Head

        # Draw Ladders (Green)
        for start, end in self.ladders.items():
            sx, sy = self.get_coords(start)
            ex, ey = self.get_coords(end)
            self.board_canvas.create_line(sx, sy, ex, ey, fill="#4CAF50", width=4, arrow=tk.LAST)
            self.board_canvas.create_oval(sx-5, sy-5, sx+5, sy+5, fill="green") # Base

    def move_token_visual(self, path):
        """Animates the token moving along the path."""
        for i in range(len(path)):
            pos = path[i]
            x, y = self.get_coords(pos)
            r = 15 # radius
            self.board_canvas.coords(self.token, x-r, y-r, x+r, y+r)
            self.board_canvas.update()
            
            delay = 0.5 / self.speed_var.get()
            time.sleep(delay)

    def start_search(self):
        algo = self.algorithm_var.get()
        self.status_var.set(f"Running {algo}...")
        self.root.update()

        path, nodes = [], 0
        if algo == "BFS":
            path, nodes = self.ai.bfs_search(1, 100)
        elif algo == "DFS":
            path, nodes = self.ai.dfs_search(1, 100)
        elif algo == "A*":
            path, nodes = self.ai.a_star_search(1, 100)

        if not path:
            messagebox.showerror("Error", "No path found!")
            return

        self.status_var.set(f"Done! Path Len: {len(path)} | Nodes: {nodes}")
        self.move_token_visual(path)

    def run_comparison(self):
        self.status_var.set("Running comparison...")
        self.root.update()

        # Run each 5 times to get average
        for algo in ['BFS', 'DFS', 'A*']:
            temp_nodes = []
            temp_paths = []
            for _ in range(5):
                if algo == 'BFS': p, n = self.ai.bfs_search(1, 100)
                elif algo == 'DFS': p, n = self.ai.dfs_search(1, 100)
                elif algo == 'A*': p, n = self.ai.a_star_search(1, 100)
                temp_nodes.append(n)
                temp_paths.append(len(p))
            
            self.stats[algo]['nodes'] = temp_nodes
            self.stats[algo]['path_len'] = temp_paths

        self.update_stats_plots()
        self.status_var.set("Comparison Complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeLadderGUI(root)
    root.mainloop()