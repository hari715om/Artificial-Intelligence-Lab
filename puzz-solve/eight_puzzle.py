import tkinter as tk
import random
import heapq
from PIL import Image, ImageTk

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GRID = 3
IMAGE_SIZE = 300
TILE_SIZE = IMAGE_SIZE // GRID
DELAY = 350


class ImagePuzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Sliding Puzzle")
        self.root.configure(bg="#eef2f6")

        self.board = []
        self.moves = 0
        self.solving = False

        self.images = {}
        self.load_and_slice_image()

        # -------- CARD --------
        self.card = tk.Frame(root, bg="white", padx=20, pady=20)
        self.card.pack(padx=30, pady=30)

        tk.Label(
            self.card, text="Image Puzzle",
            font=("Segoe UI", 20, "bold"),
            bg="white"
        ).pack(pady=(0, 10))

        self.status = tk.Label(
            self.card, text="Moves: 0",
            font=("Segoe UI", 12),
            bg="white"
        )
        self.status.pack(pady=5)

        self.board_frame = tk.Frame(self.card, bg="white")
        self.board_frame.pack(pady=10)

        self.message = tk.Label(
            self.card, text="",
            font=("Segoe UI", 11),
            fg="#16a34a",
            bg="white"
        )
        self.message.pack(pady=6)

        controls = tk.Frame(self.card, bg="white")
        controls.pack(pady=10)

        self.restart_btn = tk.Button(
            controls, text="Restart",
            width=10, bg="#4f46e5", fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.reset
        )
        self.restart_btn.pack(side="left", padx=6)

        self.solve_btn = tk.Button(
            controls, text="Auto Solve",
            width=10, bg="#0ea5e9", fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.auto_solve
        )
        self.solve_btn.pack(side="left", padx=6)

        self.reset()

    # -------- IMAGE PROCESSING --------
    def load_and_slice_image(self):
        img = Image.open("download (4).png")
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE))

        num = 1
        for r in range(GRID):
            for c in range(GRID):
                if num == 9:
                    self.images[0] = None
                    continue
                crop = img.crop((
                    c * TILE_SIZE,
                    r * TILE_SIZE,
                    (c + 1) * TILE_SIZE,
                    (r + 1) * TILE_SIZE
                ))
                self.images[num] = ImageTk.PhotoImage(crop)
                num += 1

    # -------- RESET --------
    def reset(self):
        self.solving = False
        self.moves = 0
        self.status.config(text="Moves: 0")
        self.message.config(text="")
        self.enable_buttons()
        self.board = self.generate_board()
        self.render()

    # -------- RENDER --------
    def render(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        for i, val in enumerate(self.board):
            r, c = divmod(i, GRID)

            if val == 0:
                tile = tk.Label(
                    self.board_frame,
                    width=8, height=4,
                    bg="#eef2f6"
                )
            else:
                tile = tk.Button(
                    self.board_frame,
                    image=self.images[val],
                    command=lambda x=i: self.move(x),
                    borderwidth=0
                )

            tile.grid(row=r, column=c, padx=4, pady=4)

    # -------- MOVE --------
    def move(self, index):
        if self.solving:
            return

        empty = self.board.index(0)
        if not self.adjacent(index, empty):
            return

        self.swap(index, empty)
        self.increment_move()
        self.render()

        if tuple(self.board) == GOAL:
            self.message.config(text="🎉 Puzzle Solved!")

    def increment_move(self):
        self.moves += 1
        self.status.config(text=f"Moves: {self.moves}")

    # -------- AUTO SOLVER --------
    def auto_solve(self):
        if self.solving:
            return

        self.solving = True
        self.disable_buttons()
        path = self.a_star(tuple(self.board))
        self.animate(path, 1)

    def animate(self, path, step):
        if step >= len(path):
            self.solving = False
            self.enable_buttons()
            self.message.config(text="🤖 Auto Solved!")
            return

        self.board = list(path[step])
        self.increment_move()
        self.render()
        self.root.after(DELAY, lambda: self.animate(path, step + 1))

    # -------- A* SEARCH --------
    def a_star(self, start):
        pq = []
        heapq.heappush(pq, (0, start))
        came = {}
        g = {start: 0}

        while pq:
            _, cur = heapq.heappop(pq)
            if cur == GOAL:
                return self.reconstruct(came, cur)

            for nxt in self.neighbors(cur):
                cost = g[cur] + 1
                if nxt not in g or cost < g[nxt]:
                    g[nxt] = cost
                    f = cost + self.manhattan(nxt)
                    heapq.heappush(pq, (f, nxt))
                    came[nxt] = cur

        return []

    def reconstruct(self, came, cur):
        path = [cur]
        while cur in came:
            cur = came[cur]
            path.append(cur)
        return path[::-1]

    # -------- HELPERS --------
    def manhattan(self, state):
        dist = 0
        for i, v in enumerate(state):
            if v == 0:
                continue
            gi = GOAL.index(v)
            r1, c1 = divmod(i, GRID)
            r2, c2 = divmod(gi, GRID)
            dist += abs(r1 - r2) + abs(c1 - c2)
        return dist

    def neighbors(self, state):
        idx = state.index(0)
        r, c = divmod(idx, GRID)
        res = []

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID and 0 <= nc < GRID:
                ni = nr * GRID + nc
                lst = list(state)
                lst[idx], lst[ni] = lst[ni], lst[idx]
                res.append(tuple(lst))
        return res

    def adjacent(self, i, j):
        r1, c1 = divmod(i, GRID)
        r2, c2 = divmod(j, GRID)
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def swap(self, i, j):
        self.board[i], self.board[j] = self.board[j], self.board[i]

    def generate_board(self):
        while True:
            arr = list(GOAL)
            random.shuffle(arr)
            if self.solvable(arr) and tuple(arr) != GOAL:
                return arr

    def solvable(self, arr):
        inv = 0
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] and arr[j] and arr[i] > arr[j]:
                    inv += 1
        return inv % 2 == 0

    def disable_buttons(self):
        self.restart_btn.config(state="disabled")
        self.solve_btn.config(state="disabled")

    def enable_buttons(self):
        self.restart_btn.config(state="normal")
        self.solve_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    ImagePuzzle(root)
    root.mainloop()
