from collections import deque

def find_shortest_path(graph, start, goal):
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    visited = set([start])
    while queue:
        current_node, path = queue.popleft()
        for neighbor in graph.get_neighbors(current_node):
            if neighbor == goal:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []

def bfs_distance(graph, start, goal):
    if start == goal:
        return 0
    queue = deque([(start, 0)])
    visited = set([start])
    while queue:
        current, dist = queue.popleft()
        for neighbor in graph.get_neighbors(current):
            if neighbor == goal:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return float('inf')