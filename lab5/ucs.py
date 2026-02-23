import heapq
import networkx as nx
import matplotlib.pyplot as plt

def uniform_cost_search(graph, start, goal):
    priority_queue = [(0, start)]
    
    visited = {start: (0, None)}

    while priority_queue:
        current_cost, current_node = heapq.heappop(priority_queue)
        
        if current_node == goal:
            print(f"Goal '{goal}' reached! Total Cost: {current_cost}")
            return current_cost, reconstruct_path(visited, start, goal)
        
        if current_cost > visited[current_node][0]:
            continue
            
        for neighbor, weight in graph.get(current_node, []):
            total_cost = current_cost + weight
            
            if neighbor not in visited or total_cost < visited[neighbor][0]:
                visited[neighbor] = (total_cost, current_node)
                heapq.heappush(priority_queue, (total_cost, neighbor))
                
    return None, None

def reconstruct_path(visited, start, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = visited[current][1]
    
    path.reverse()
    return path

def visualize_graph(graph, path=None):
    G = nx.DiGraph()
    
    for node, edges in graph.items():
        for neighbor, cost in edges:
            G.add_edge(node, neighbor, weight=cost)
            
    pos = nx.spring_layout(G, seed=42) 
    
    plt.figure(figsize=(10, 7))
    
    nx.draw(G, pos, 
            with_labels=True, 
            node_color='lightblue', 
            node_size=2000, 
            font_size=12, 
            font_weight='bold', 
            edge_color='gray',
            arrowsize=20)
    
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, 
                               edgelist=path_edges, 
                               edge_color='red', 
                               width=2.5,
                               arrowsize=20)
        plt.title(f"Uniform Cost Search Path: {' -> '.join(path)}")
    else:
        plt.title("Uniform Cost Search Visualization")
        
    plt.show()

graph = {
    'S': [('A', 1), ('B', 5)],
    'A': [('B', 2), ('G', 10)],
    'B': [('G', 2)],
    'C': [('G', 3)],  
    'G': []
}

if __name__ == "__main__":
    start_node = 'S'
    goal_node = 'G'
    
    cost, path = uniform_cost_search(graph, start_node, goal_node)
    
    if path:
        print(f"Least cost path: {' -> '.join(path)} (Cost: {cost})")
        # 3. Visualize Result
        visualize_graph(graph, path)
    else:
        print(f"No path found from {start_node} to {goal_node}")
        visualize_graph(graph, None)