import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from IPython.display import HTML
import numpy as np

# -------- Grid --------
grid = [
    ['S', '.', '.', '#', '1'],
    ['#', '#', '.', '#', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '#', '#', '#', '2'],
    ['.', '.', '.', 'E', '.']
]

ROWS, COLS = len(grid), len(grid[0])

# Locate start, goals, exit
goals = {}
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == 'S':
            start = (r, c)
        elif grid[r][c].isdigit():
            goals[(r, c)] = int(grid[r][c])
        elif grid[r][c] == 'E':
            exit_pos = (r, c)

goal_list = list(goals.keys())
goal_index = {g: i for i, g in enumerate(goal_list)}
ALL_COLLECTED = (1 << len(goal_list)) - 1

moves = [(0,1),(1,0),(0,-1),(-1,0)]

def neighbors(r, c):
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != '#':
            yield nr, nc

# -------- BFS --------
def bfs_multi_goal():
    q = deque([(start[0], start[1], 0, [start])])
    visited = set()

    while q:
        r, c, mask, path = q.popleft()
        if (r, c, mask) in visited:
            continue
        visited.add((r, c, mask))

        if (r, c) in goal_index:
            mask |= (1 << goal_index[(r, c)])

        if (r, c) == exit_pos and mask == ALL_COLLECTED:
            return path

        for nr, nc in neighbors(r, c):
            q.append((nr, nc, mask, path + [(nr, nc)]))

path = bfs_multi_goal()

# -------- Visualization --------
grid_numeric = np.zeros((ROWS, COLS))
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == '#':
            grid_numeric[r][c] = 0  # wall
        elif grid[r][c] == 'S':
            grid_numeric[r][c] = 1  # start
        elif grid[r][c] == 'E':
            grid_numeric[r][c] = 2  # exit
        elif grid[r][c].isdigit():
            grid_numeric[r][c] = 3  # goal
        else:
            grid_numeric[r][c] = 4  # free

fig, ax = plt.subplots(figsize=(5,5))
collected_goals = set()

def update(frame):
    ax.clear()
    r, c = path[frame]

    if (r, c) in goals:
        collected_goals.add((r, c))

    display_grid = grid_numeric.copy()
    for g in goals:
        if g in collected_goals:
            display_grid[g[0]][g[1]] = 5  # collected goal

    ax.imshow(display_grid, cmap="tab10")
    ax.scatter(c, r, s=150, marker='o')  # robot

    ax.set_title("BFS: Multi-Goal Robot Navigation")
    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.grid(True)

anim = animation.FuncAnimation(fig, update, frames=len(path), interval=600, repeat=False)
HTML(anim.to_jshtml())