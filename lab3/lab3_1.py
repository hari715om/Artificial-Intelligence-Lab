from collections import deque

maze = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
]

start = (0, 0)
end = (4, 4)

def bfs_solve(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    queue = deque([(start, [start])]) 
    visited = set([start])

    while queue:
        (r, c), path = queue.popleft() 

        if (r, c) == end:
            return path  

        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                queue.append(((nr, nc), path + [(nr, nc)]))
                visited.add((nr, nc))
    return None

def dfs_solve(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    stack = [(start, [start])] 
    visited = set([start])

    while stack:
        (r, c), path = stack.pop() 

        if (r, c) == end:
            return path

        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                stack.append(((nr, nc), path + [(nr, nc)]))
                visited.add((nr, nc))
    return None

print("BFS Path:", bfs_solve(maze, start, end))
print("DFS Path:", dfs_solve(maze, start, end))