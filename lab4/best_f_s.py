GRAPH = {
    'S': ['A', 'B'],
    'A': ['C', 'D'],
    'B': ['E', 'F'],
    'E': ['H'],
    'F': ['I', 'G'],
    'C': [], 'D': [], 'H': [], 'I': [], 'G': []
}

HEURISTICS = {
    'S': 13, 'A': 12, 'B': 4,
    'C': 7,  'D': 3,  'E': 8,
    'F': 2,  'H': 4,  'I': 9,
    'G': 0   
}

def get_neighbors(node):
    return GRAPH.get(node, [])

def best_first_search(start, goal):
    open_list = [[start, HEURISTICS[start]]]
    
    closed_list = []

    print(f"Starting Search from '{start}' to '{goal}'...\n")

    while open_list:
        open_list.sort(key=lambda x: x[1])
        
        print(f"Current OPEN List: {open_list}")

        current_node, current_h = open_list.pop(0)
        
        closed_list.append(current_node)
        
        print(f"Processing Node: {current_node} (Heuristic: {current_h})")

        if current_node == goal:
            print("\nSUCCESS: Goal Found!")
            print(f"Path Traversed: {closed_list}")
            return

        neighbors = get_neighbors(current_node)
        
        for neighbor in neighbors:
            in_open = any(neighbor == item[0] for item in open_list)
            in_closed = neighbor in closed_list
            
            if not in_open and not in_closed:
                h_val = HEURISTICS[neighbor]
                open_list.append([neighbor, h_val])
    
    print("FAILURE: Path not found.")

best_first_search('S', 'G')