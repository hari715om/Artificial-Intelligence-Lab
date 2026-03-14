import heapq
import tkinter as tk

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
    avail = []
    for t in tasks:
        if t not in completed and all(dep in completed for dep in tasks[t]['deps']):
            avail.append(t)
    return avail


class SchedulerGUI:

    def __init__(self, root):

        self.root = root
        root.title("AI Task Scheduler Visualization (A* vs Greedy)")
        root.geometry("900x600")

        self.canvas = tk.Canvas(root, width=850, height=420, bg="white")
        self.canvas.pack(pady=10)

        controls = tk.Frame(root)
        controls.pack()

        self.astar_btn = tk.Button(controls, text="Run A*", width=15, command=self.start_astar)
        self.astar_btn.grid(row=0, column=0, padx=10)

        self.greedy_btn = tk.Button(controls, text="Run Greedy", width=15, command=self.start_greedy)
        self.greedy_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = tk.Button(controls, text="Reset", width=15, command=self.reset)
        self.reset_btn.grid(row=0, column=2, padx=10)

        self.info = tk.Label(root, text="Select Algorithm", font=("Arial", 12))
        self.info.pack(pady=5)

        self.legend = tk.Label(
            root,
            text="Green = Completed   |   Yellow = Available   |   Red = Blocked",
            font=("Arial", 10)
        )
        self.legend.pack()

        self.node_positions = {}
        self.draw_graph()

        self.reset()

    def draw_graph(self):

        positions = {

            'A': (425, 50),

            'B': (200, 150),
            'C': (425, 150),
            'D': (650, 150),

            'E': (150, 260),
            'F': (325, 260),
            'G': (525, 260),
            'H': (725, 260),

            'I': (325, 360),
            'J': (525, 360)
        }

        self.node_positions = positions

        for task, data in tasks.items():

            for dep in data['deps']:

                x1, y1 = positions[dep]
                x2, y2 = positions[task]

                self.canvas.create_line(x1, y1 + 20, x2, y2 - 20, arrow=tk.LAST, width=2)

        for task, (x, y) in positions.items():

            self.canvas.create_oval(
                x - 25, y - 25, x + 25, y + 25,
                fill="#dddddd",
                outline="black",
                width=2,
                tags=task
            )

            label = f"{task}\n({tasks[task]['duration']})"

            self.canvas.create_text(x, y, text=label, font=("Arial", 10, "bold"))

    def reset(self):

        for task in tasks:
            self.canvas.itemconfig(task, fill="#dddddd")

        self.info.config(text="Select Algorithm")

        self.pq = []
        self.visited = set()

        self.completed = []
        self.total_time = 0

    def update_nodes(self, completed):

        for task in tasks:

            if task in completed:
                color = "#6dd66d"

            elif any(dep not in completed for dep in tasks[task]['deps']):
                color = "#ff8c8c"

            else:
                color = "#ffd966"

            self.canvas.itemconfig(task, fill=color)

    def start_astar(self):

        self.reset()

        start = (0, [], 0)
        heapq.heappush(self.pq, start)

        self.algorithm = "astar"

        self.step()

    def start_greedy(self):

        self.reset()

        self.algorithm = "greedy"

        self.step()

    def step(self):

        if self.algorithm == "astar":

            if not self.pq:
                return

            f, completed, g = heapq.heappop(self.pq)

            state = tuple(completed)

            if state in self.visited:
                self.root.after(700, self.step)
                return

            self.visited.add(state)

            self.update_nodes(completed)

            if len(completed) == len(tasks):

                self.info.config(
                    text=f"A* Finished | Order: {completed} | Total Time: {g}"
                )
                return

            for task in available_tasks(completed):

                new_completed = completed + [task]

                new_cost = g + tasks[task]['duration']

                h = heuristic(new_completed)

                f_new = new_cost + h

                heapq.heappush(self.pq, (f_new, new_completed, new_cost))

            self.root.after(900, self.step)

        else:

            if len(self.completed) == len(tasks):

                self.info.config(
                    text=f"Greedy Finished | Order: {self.completed} | Total Time: {self.total_time}"
                )
                return

            avail = available_tasks(self.completed)

            next_task = min(avail, key=lambda x: tasks[x]['duration'])

            self.completed.append(next_task)

            self.total_time += tasks[next_task]['duration']

            self.update_nodes(self.completed)

            self.info.config(
                text=f"Greedy Running | Completed: {self.completed} | Time: {self.total_time}"
            )

            self.root.after(900, self.step)


root = tk.Tk()
app = SchedulerGUI(root)
root.mainloop()