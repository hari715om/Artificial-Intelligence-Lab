from pyamaze import maze, agent, COLOR
from collections import deque

def BFS(m):
    start = (m.rows, m.cols)
    
    frontier = deque()
    frontier.append(start)
    
    explored = [start]
    
    bfsPath = {}
    
    while len(frontier) > 0:
        currCell = frontier.popleft()
        
        if currCell == (1, 1):
            break
        
        for d in 'ESNW':
            if m.maze_map[currCell][d] == 1:
                if d == 'E':
                    childCell = (currCell[0], currCell[1] + 1)
                elif d == 'W':
                    childCell = (currCell[0], currCell[1] - 1)
                elif d == 'N':
                    childCell = (currCell[0] - 1, currCell[1])
                elif d == 'S':
                    childCell = (currCell[0] + 1, currCell[1])
                
                if childCell in explored:
                    continue
                
                frontier.append(childCell)
                explored.append(childCell)
                bfsPath[childCell] = currCell
    
    fwdPath = {}
    cell = (1, 1)
    while cell != start:
        fwdPath[bfsPath[cell]] = cell
        cell = bfsPath[cell]
        
    return fwdPath

if __name__ == '__main__':
    m = maze(15, 15)
    m.CreateMaze(loopPercent=100, theme=COLOR.light)
    
    path = BFS(m)
    
    a = agent(m, footprints=True, filled=True, color=COLOR.blue)
    m.tracePath({a: path})
    
    m.run()