import matplotlib.pyplot as plt
import matplotlib.animation as animation
import heapq
from IPython.display import HTML
import numpy as np

# Grid Definition
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

def heuristic(r, c):
    return abs(r - exit_pos[0]) + abs(c - exit_pos[1])

# A* Search
def astar():
    pq = [(0 + heuristic(*start), 0, start[0], start[1], 0, [start])]
    visited = set()

    while pq:
        f, cost, r, c, mask, path = heapq.heappop(pq)
        if (r, c, mask) in visited:
            continue
        visited.add((r, c, mask))

        if (r, c) in goal_index:
            mask |= (1 << goal_index[(r, c)])

        if (r, c) == exit_pos and mask == ALL_COLLECTED:
            return path

        for nr, nc in neighbors(r, c):
            g = cost + 1
            h = heuristic(nr, nc)
            heapq.heappush(pq, (g + h, g, nr, nc, mask, path + [(nr, nc)]))

    return None

path = astar()

# ---------------- COLOR MAP ----------------
color_map = {
    '#': 0,  # wall
    '.': 1,  # free
    'S': 2,  # start
    'E': 3,  # exit
    'G': 4,  # goal collected
    'U': 5   # uncollected goal
}

grid_numeric = np.ones((ROWS, COLS))
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == '#':
            grid_numeric[r][c] = 0
        elif grid[r][c] == 'S':
            grid_numeric[r][c] = 2
        elif grid[r][c] == 'E':
            grid_numeric[r][c] = 3
        elif grid[r][c].isdigit():
            grid_numeric[r][c] = 5
        else:
            grid_numeric[r][c] = 1

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
            display_grid[g[0]][g[1]] = 4

    ax.imshow(display_grid, cmap="tab10")

    # Robot
    ax.scatter(c, r, c="red", s=150, marker="o", label="Robot")

    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.set_title("Multi-Goal Robot Navigation (A*)")
    ax.grid(True)

anim = animation.FuncAnimation(fig, update, frames=len(path), interval=600, repeat=False)
HTML(anim.to_jshtml())