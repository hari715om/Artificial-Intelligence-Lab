import heapq

tasks = {
    'A': {'duration': 3, 'deps': []},
    'B': {'duration': 2, 'deps': ['A']},
    'C': {'duration': 4, 'deps': ['A']},
    'D': {'duration': 2, 'deps': ['A']},
    'E': {'duration': 5, 'deps': ['B']},
    'F': {'duration': 3, 'deps': ['B', 'C']},
    'G': {'duration': 4, 'deps': ['C']},
    'H': {'duration': 2, 'deps': ['D']},
    'I': {'duration': 3, 'deps': ['E', 'F']},
    'J': {'duration': 4, 'deps': ['G', 'H']}
}

def heuristic(completed):
    remaining = [tasks[t]['duration'] for t in tasks if t not in completed]
    return sum(remaining)

def available_tasks(completed):
    available = []
    for task in tasks:
        if task not in completed:
            if all(dep in completed for dep in tasks[task]['deps']):
                available.append(task)
    return available

def astar_scheduler():
    start_state = (0, [], 0)

    pq = []
    heapq.heappush(pq, start_state)

    visited = set()

    while pq:
        f_cost, completed, g_cost = heapq.heappop(pq)

        state = tuple(completed)

        if state in visited:
            continue

        visited.add(state)

        if len(completed) == len(tasks):
            return completed, g_cost

        for task in available_tasks(completed):
            new_completed = completed + [task]
            new_cost = g_cost + tasks[task]['duration']

            h = heuristic(new_completed)
            f_new = new_cost + h

            heapq.heappush(pq, (f_new, new_completed, new_cost))

def greedy_scheduler():
    completed = []
    total_time = 0

    while len(completed) < len(tasks):
        avail = available_tasks(completed)
        next_task = min(avail, key=lambda x: tasks[x]['duration'])

        completed.append(next_task)
        total_time += tasks[next_task]['duration']

    return completed, total_time

astar_order, astar_time = astar_scheduler()
greedy_order, greedy_time = greedy_scheduler()

print("A* Optimal Schedule")
print("Order:", astar_order)
print("Total Time:", astar_time)

print("\nGreedy Schedule")
print("Order:", greedy_order)
print("Total Time:", greedy_time)