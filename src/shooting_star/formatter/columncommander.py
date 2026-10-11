def decide_columns(
    topo_order: list[int],
    adj: dict[int, list[int]],
    current: int | None,
    nodes: dict | None = None,
) -> dict[int, int]:
    if current is None:
        raise Exception("current is None")

    columns = {}
    next_column = 1

    columns[current] = 0

    parents = adj_reverser(adj)

    def release_year(node: int) -> int:
        year = (nodes or {}).get(node, {}).get("year")
        return year if year is not None else 9999

    # Keep a shared sequel on the earliest chronological line.
    primary_parent = {
        node: min(node_parents, key=lambda parent: (release_year(parent), parent))
        for node, node_parents in parents.items()
    }

    # One child continues a parent's column; later children are branches.
    primary_child = {
        parent: min(children, key=lambda child: (release_year(child), child))
        for parent, children in adj.items()
        if children
    }

    ancestor = primary_parent.get(current)
    while ancestor is not None:
        columns[ancestor] = 0
        ancestor = primary_parent.get(ancestor)

    for node in topo_order:
        if node in columns:
            continue
        node_parents = parents.get(node, [])

        if len(node_parents) == 0:
            columns[node] = next_column
            next_column += 1
        else:
            parent = primary_parent[node]
            if primary_child.get(parent) == node:
                columns[node] = columns[parent]
            else:
                columns[node] = next_column
                next_column += 1

    return columns


def adj_reverser(adj: dict[int, list[int]]) -> dict[int, list[int]]:
    result = {}
    for node, neighbors in adj.items():
        for el in neighbors:
            result.setdefault(el, []).append(node)

    return result
