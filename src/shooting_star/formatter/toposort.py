# Thank you, Chirag Agarwal from GeeksforGeeks for explaining Kahn's algorithm

from collections import deque


def topoSort(adj: dict[int, list[int]]) -> list[int]:

    indegree = {}
    for key, _ in adj.items():
        indegree[key] = 0

    order = []
    queue = deque()

    for _, neighbors in adj.items():
        for next_node in neighbors:
            indegree[next_node] += 1

    for node in sorted(indegree):
        if indegree[node] == 0:
            queue.append(node)

    while queue:
        top = queue.popleft()
        order.append(top)
        for next_node in sorted(adj[top]):
            indegree[next_node] -= 1
            if indegree[next_node] == 0:
                queue.append(next_node)

    return order
