import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import math
import random
import heapq
from collections import deque
from PIL import Image, ImageTk, ImageOps # pip install pillow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
#  THEME CONFIGURATION
# ==========================================
THEME = {
    "bg": "#f0f2f5",           
    "panel": "#ffffff",
    "text_dark": "#333333",
    "text_light": "#757575",
    "accent": "#6200ea",       # Deep Purple
    "highlight": "#00c853",    # Green for active elements
    "dice_bg": "#212121",
    "dice_fg": "#ffeb3b"
}

# ==========================================
#  GAME ENGINE (Exact Rules)
# ==========================================
class GameEngine:
    def __init__(self):
        self.board_size = 100
        
        # --- HARDCODED LOGIC FROM YOUR REQUEST ---
        self.snakes = {
            96: 42, 
            94: 71, 
            75: 32, 
            47: 16, 
            37: 3, 
            26: 10
        }
        
        self.ladders = {
            4: 56, 
            12: 50, 
            14: 55, 
            54: 88, 
            41: 79
            # Note: The image also shows a ladder at 22, 
            # but we are strictly following your list.
        }

    def get_next_positions(self, current_pos):
        moves = []
        for dice in range(1, 7):
            next_pos = current_pos + dice
            
            # Apply Snake/Ladder Logic
            if next_pos in self.snakes: 
                next_pos = self.snakes[next_pos]
            elif next_pos in self.ladders: 
                next_pos = self.ladders[next_pos]
                
            if next_pos <= self.board_size:
                moves.append(next_pos)
        return moves

    def reverse_engineer_dice(self, current, next_spot):
        """Calculates which dice roll (1-6) resulted in the move"""
        for dice in range(1, 7):
            temp = current + dice
            if temp in self.snakes: temp = self.snakes[temp]
            elif temp in self.ladders: temp = self.ladders[temp]
            
            if temp == next_spot:
                return dice
        return 1

# ==========================================
#  AI SOLVER ALGORITHMS
# ==========================================
class AI:
    def __init__(self, engine):
        self.engine = engine

    def bfs(self):
        queue = deque([(1, [1])])
        visited = {1}
        nodes_explored = 0
        while queue:
            curr, path = queue.popleft()
            nodes_explored += 1
            if curr == 100: return path, nodes_explored
            
            for nxt in self.engine.get_next_positions(curr):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return [], nodes_explored

    def dfs(self):
        stack = [(1, [1])]
        visited = {1}
        nodes_explored = 0
        while stack:
            curr, path = stack.pop()
            nodes_explored += 1
            if curr == 100: return path, nodes_explored
            
            for nxt in reversed(self.engine.get_next_positions(curr)):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append((nxt, path + [nxt]))
        return [], nodes_explored

    def a_star(self):
        pq = [(0, 1, [1])]
        g_score = {1: 0}
        nodes_explored = 0
        while pq:
            _, curr, path = heapq.heappop(pq)
            nodes_explored += 1
            if curr == 100: return path, nodes_explored
            
            tentative_g = g_score[curr] + 1
            for nxt in self.engine.get_next_positions(curr):
                if nxt not in g_score or tentative_g < g_score[nxt]:
                    g_score[nxt] = tentative_g
                    # Heuristic: Distance to 100 / Max Move (6)
                    f = tentative_g + (100 - nxt) / 6
                    heapq.heappush(pq, (f, nxt, path + [nxt]))
        return [], nodes_explored

# ==========================================
#  MINIMAL GUI DASHBOARD
# ==========================================
class SnakeLadderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake & Ladder AI | Context Aware")
        self.root.geometry("1100x700")
        self.root.configure(bg=THEME["bg"])
        
        self.engine = GameEngine()
        self.ai = AI(self.engine)
        self.bg_image = None
        
        self.setup_layout()
        
        # Try to auto-load "snake_board.jpg" if it exists
        try:
            self.load_image_file("snake_board.jpg")
        except:
            pass # Wait for manual upload

    def setup_layout(self):
        # 1. Main Container
        main_frame = tk.Frame(self.root, bg=THEME["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 2. Left Side: The Board
        self.board_panel = tk.Frame(main_frame, bg="white", bd=5, relief=tk.FLAT)
        self.board_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.board_panel, width=650, height=650, bg="white", highlightthickness=0)
        self.canvas.pack(anchor=tk.CENTER, expand=True)

        # 3. Right Side: Refined Dashboard
        self.dash_panel = tk.Frame(main_frame, bg=THEME["panel"], width=350)
        self.dash_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        self.dash_panel.pack_propagate(False) # Fixed width

        self.build_dashboard()

    def build_dashboard(self):
        # Header
        tk.Label(self.dash_panel, text="GAME CONTROLLER", font=("Helvetica", 14, "bold"), 
                 bg=THEME["panel"], fg=THEME["text_dark"]).pack(pady=(25, 10))

        # --- SECTION 1: SETUP ---
        setup_frame = tk.LabelFrame(self.dash_panel, text="Setup", bg=THEME["panel"], fg=THEME["text_light"], padx=15, pady=10)
        setup_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Button(setup_frame, text="📂 Load Board Image", command=self.upload_image, 
                  bg="#eceff1", fg=THEME["text_dark"], relief=tk.FLAT).pack(fill=tk.X)

        # --- SECTION 2: AI CONTROLS ---
        ctrl_frame = tk.LabelFrame(self.dash_panel, text="Simulation", bg=THEME["panel"], fg=THEME["text_light"], padx=15, pady=10)
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)

        # Algorithm Selection
        tk.Label(ctrl_frame, text="Algorithm:", bg=THEME["panel"], fg=THEME["text_dark"]).pack(anchor="w")
        self.algo_var = tk.StringVar(value="BFS")
        algo_menu = ttk.Combobox(ctrl_frame, textvariable=self.algo_var, values=["BFS", "DFS", "A*"], state="readonly")
        algo_menu.pack(fill=tk.X, pady=(0, 10))

        # Speed Control (larger = slower)
        tk.Label(ctrl_frame, text="Animation Speed:", bg=THEME["panel"], fg=THEME["text_dark"]).pack(anchor="w")
        self.speed_var = tk.DoubleVar(value=2.0)
        # Range 0.5 (fast) -> 10 (slow) — resolution 0.5
        tk.Scale(ctrl_frame, from_=0.5, to=10, orient=tk.HORIZONTAL, variable=self.speed_var,
                 bg=THEME["panel"], highlightthickness=0, showvalue=True, resolution=0.5).pack(fill=tk.X)
        btn_frame = tk.Frame(ctrl_frame, bg=THEME["panel"])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="▶ START", command=self.run_simulation, 
                  bg=THEME["accent"], fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, padx=10).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        tk.Button(btn_frame, text="📊 COMPARE", command=self.run_comparison, 
                  bg="#546e7a", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, padx=10).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # --- SECTION 3: LIVE STATUS ---
        status_frame = tk.Frame(self.dash_panel, bg=THEME["panel"])
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Dice Visual
        self.dice_lbl = tk.Label(status_frame, text="🎲", font=("Arial", 36), bg=THEME["dice_bg"], fg=THEME["dice_fg"], width=3)
        self.dice_lbl.pack(side=tk.LEFT)
        
        # Text Info
        self.status_text = tk.StringVar(value="Ready to play")
        tk.Label(status_frame, textvariable=self.status_text, bg=THEME["panel"], fg=THEME["text_dark"], 
                 wraplength=180, justify=tk.LEFT).pack(side=tk.LEFT, padx=10)

        # --- SECTION 4: ANALYTICS ---
        self.fig, self.ax = plt.subplots(figsize=(3, 2.5))
        self.fig.patch.set_facecolor(THEME["panel"])
        self.ax.set_facecolor("#fafafa")
        
        self.chart = FigureCanvasTkAgg(self.fig, self.dash_panel)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.reset_chart()

    def reset_chart(self):
        self.ax.clear()
        self.ax.set_title("Performance Metrics", fontsize=8)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.text(0.5, 0.5, "Run Comparison\nto see data", ha='center', fontsize=8, color="#999")
        self.chart.draw()

    # ==========================================
    #  VISUAL LOGIC (COORDINATES)
    # ==========================================
    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            self.load_image_file(path)

    def load_image_file(self, path):
        img = Image.open(path)
        img = img.resize((650, 650), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.status_text.set("Board Loaded.\nLogic Applied.")

    def get_coords(self, pos):
        """
        Maps 1-100 to Canvas (x,y) based on your specific image.
        Image Layout:
        Row 0 (Bottom): 1 (Left) -> 10 (Right)
        Row 1: 11 (Right) -> 20 (Left)
        """
        if pos < 1: pos = 1
        if pos > 100: pos = 100
        
        idx = pos - 1
        row = idx // 10
        col = idx % 10
        
        # Zig-Zag Logic
        if row % 2 == 1: # Odd rows (11-20, 31-40) go Right -> Left
            col = 9 - col
            
        # Canvas Calculation
        # row 0 is bottom (y=650), row 9 is top (y=0)
        x = col * 65 + 32.5
        y = (9 - row) * 65 + 32.5
        
        return x, y

    # ==========================================
    #  SIMULATION
    # ==========================================
    def run_simulation(self):
        if not self.bg_image:
            messagebox.showwarning("Warning", "Please load the board image first!")
            return

        algo = self.algo_var.get()
        self.status_text.set(f"Computing {algo}...")
        self.root.update()

        if algo == "BFS": path, nodes = self.ai.bfs()
        elif algo == "DFS": path, nodes = self.ai.dfs()
        else: path, nodes = self.ai.a_star()

        if not path:
            self.status_text.set("No path found!")
            return

        # Store path and nodes for display after animation
        self.last_path = path
        self.last_nodes = nodes

        # Start non-blocking animation and update status when finished
        self.animate_token(path, on_complete=lambda: self.show_path_summary(path, nodes))

    def animate_token(self, path, on_complete=None):
        # Non-blocking animation using `after` so UI remains responsive
        self.canvas.delete("token")
        self.canvas.delete("path_visited")  # Clear previous path visualization

        token = self.canvas.create_oval(0,0,0,0, fill=THEME["highlight"], outline="white", width=2, tags="token")

        # Draw light circles for all cells in the path
        for pos in path:
            x, y = self.get_coords(pos)
            self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="#e0e0e0", outline="#999999", width=1, tags="path_visited")
        
        # Place start at start
        sx, sy = self.get_coords(path[0])
        self.canvas.coords(token, sx-12, sy-12, sx+12, sy+12)
        self.canvas.tag_raise("token")  # Ensure token is on top
        self.root.update()

        # Internal recursive animator
        def animate_segment(idx):
            if idx >= len(path)-1:
                # animation finished - keep the path visible and show summary
                if on_complete:
                    on_complete()
                return

            curr, nxt = path[idx], path[idx+1]
            dice_val = self.engine.reverse_engineer_dice(curr, nxt)
            self.dice_lbl.config(text=str(dice_val))

            start_x, start_y = self.get_coords(curr)
            end_x, end_y = self.get_coords(nxt)

            steps = 15

            # Delay mapping: larger slider value => slower animation
            # base step delay in ms
            base_step_ms = 20

            def step_move(s):
                t = s / steps
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                self.canvas.coords(token, cur_x-12, cur_y-12, cur_x+12, cur_y+12)
                self.canvas.update()

                if s < steps:
                    delay = max(2, int(base_step_ms * self.speed_var.get()))
                    self.canvas.after(delay, lambda: step_move(s+1))
                else:
                    # Snap to final
                    self.canvas.coords(token, end_x-12, end_y-12, end_x+12, end_y+12)
                    snap_delay = max(10, int(200 * self.speed_var.get()))
                    self.canvas.after(snap_delay, lambda: animate_segment(idx+1))

            step_move(0)

        # Start after a short pause to show the initial position
        self.canvas.after(300, lambda: animate_segment(0))

    def show_path_summary(self, path, nodes):
        """Display path and statistics after animation completes"""
        # Format path as string
        path_str = " → ".join(map(str, path))
        
        # Truncate if too long for display
        if len(path_str) > 100:
            path_str = path_str[:97] + "..."
        
        summary = f"Done!\nMoves: {len(path)-1}\nNodes: {nodes}\n\nPath:\n{path_str}"
        self.status_text.set(summary)

    def run_comparison(self):
        self.status_text.set("Benchmarking...")
        self.root.update()
        
        data = {}
        for algo in ["BFS", "DFS", "A*"]:
            if algo == "BFS": _, n = self.ai.bfs()
            elif algo == "DFS": _, n = self.ai.dfs()
            else: _, n = self.ai.a_star()
            data[algo] = n
            
        self.ax.clear()
        colors = ['#FF7043', '#42A5F5', '#66BB6A']
        bars = self.ax.bar(data.keys(), data.values(), color=colors)
        self.ax.set_title("Computational Cost (Nodes Explored)", fontsize=9)
        self.ax.tick_params(labelsize=8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)

        self.chart.draw()
        self.status_text.set("Comparison Complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeLadderApp(root)
    root.mainloop()