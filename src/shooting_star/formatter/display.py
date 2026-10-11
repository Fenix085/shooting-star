from dataclasses import dataclass
from rich import box
from rich.table import Table
from rich.console import Console


from .toposort import topoSort
from .columncommander import decide_columns, adj_reverser


@dataclass
class AnimeCard:
    title: str
    format: str
    episodes: int
    year: int
    status: str
    score: float
    studio: str
    genre: str
    description: str

    def _build_card_body(self):
        table = Table(
            min_width=24,
            box=box.DOUBLE_EDGE,
            show_header=False,
            show_lines=True,
        )
        table.add_column(max_width=48, justify="left")
        table.add_row(f"{self.title}")
        table.add_row(
            f"{self.format} - {self.episodes} episodes · {self.year} · {self.status} · ★ {self.score / 10:.1f}"
        )
        table.add_row(f"{self.description}")
        table.add_row(f"{self.genre}")
        table.add_row(f"{self.studio}")
        return table

    def render(self):
        console = Console()
        console.print(self._build_card_body())


CARD_WIDTH = 35
LEFT = (CARD_WIDTH - 1) // 2
RIGHT = CARD_WIDTH // 2


@dataclass
class RelationCard:
    id: int
    title: str
    format: str
    episodes: int
    year: int

    def _build_card_body(self) -> list[str]:
        title = self.title[:CARD_WIDTH]
        year = self.year or "NDA"
        label = f"id: {self.id}"

        line1 = "┌" + "─" * CARD_WIDTH + "┐"
        line2 = "│" + f"{title:^{CARD_WIDTH}}" + "│"
        line3 = "├" + "─" * LEFT + "┬" + "─" * RIGHT + "┤"
        line4 = (
            "│"
            + f"{self.format} - {self.episodes}".center(LEFT)
            + "│"
            + f"{year:^{RIGHT}}"
            + "│"
        )
        line5 = "├" + "─" * LEFT + "┴" + "─" * RIGHT + "┤"
        line6 = "│" + f"{label:^{CARD_WIDTH}}" + "│"
        line7 = "└" + "─" * CARD_WIDTH + "┘"

        return [line1, line2, line3, line4, line5, line6, line7]


COLUMN_WIDTH = CARD_WIDTH + 4


def _find_last_nodes_by_column(
    topo_sorted: list[int], columns: dict[int, int]
) -> dict[int, int]:
    return {columns[node]: node for node in topo_sorted}


def _build_column_segment(active: bool) -> str:
    if active:
        return "|" + " " * (COLUMN_WIDTH - 1)
    return " " * COLUMN_WIDTH


def _build_fork_row(
    parent_col: int, child_cols: list[int], active: set[int], to_the_right: bool = True
) -> str:
    if not child_cols:
        return ""

    child_cols = sorted(set(child_cols))
    last_col = max(parent_col, child_cols[-1])
    fork_columns = set(child_cols)
    row = []

    for column in range(last_col + 1):
        if to_the_right:
            if column < parent_col:
                row.append(_build_column_segment(column in active))
                continue

            if column == parent_col:
                row.append("├" + "─" * (COLUMN_WIDTH - 1))
            elif column in fork_columns:
                if column == child_cols[-1]:
                    row.append("┐" + " " * (COLUMN_WIDTH - 1))
                else:
                    row.append("┬" + "─" * (COLUMN_WIDTH - 1))
            else:
                if column in active:
                    row.append("┼" + "─" * (COLUMN_WIDTH - 1))
                else:
                    row.append("─" * COLUMN_WIDTH)
        else:
            if column < parent_col:
                row.append(_build_column_segment(column in active))
                continue

            if column == parent_col:
                row.append("├" + "─" * (COLUMN_WIDTH - 1))
            elif column in fork_columns:
                if column == child_cols[0]:
                    row.append("┘" + " " * (COLUMN_WIDTH - 1))
                else:
                    row.append("┴" + "─" * (COLUMN_WIDTH - 1))
            else:
                if column in active:
                    row.append("┼" + "─" * (COLUMN_WIDTH - 1))
                else:
                    row.append("─" * COLUMN_WIDTH)

    return "".join(row)


def _build_prefix(column: int, active_columns: set[int]) -> str:
    return "".join(
        _build_column_segment(index in active_columns) for index in range(column)
    )


def _activate_node_columns(
    node: int,
    column: int,
    adj: dict[int, list[int]],
    columns: dict[int, int],
    active_columns: set[int],
) -> None:
    active_columns.add(column)
    active_columns.update(columns[child] for child in adj[node])


def _build_suffix(column: int, active_columns: set[int]) -> str:
    last_column = max(active_columns)
    return "".join(
        _build_column_segment(index in active_columns)
        for index in range(column + 1, last_column + 1)
    )


def _build_connector(active_columns: set[int]) -> str:
    return "".join(
        _build_column_segment(index in active_columns)
        for index in range(max(active_columns) + 1)
    )


def _build_relation_card(node: int, nodes: dict) -> RelationCard:
    data = nodes[node]
    return RelationCard(
        id=data["id"],
        title=data["title"]["romaji"],
        format=data["format"],
        episodes=data["episodes"],
        year=data["year"],
    )


def _render_card(card: RelationCard, prefix: str, suffix: str) -> None:
    body = card._build_card_body()
    for index, line in enumerate(body):
        marker = "* " if index == len(body) // 2 else "| "
        print(f"{prefix}{marker}{line}{suffix}")


def _render_node(
    node: int,
    nodes: dict,
    adj: dict[int, list[int]],
    columns: dict[int, int],
    active_columns: set[int],
) -> None:
    column = columns[node]
    prefix = _build_prefix(column, active_columns)
    _activate_node_columns(node, column, adj, columns, active_columns)
    suffix = _build_suffix(column, active_columns)
    _render_card(_build_relation_card(node, nodes), prefix, suffix)


def render_graph(nodes: dict, adj: dict, current: int | None) -> None:
    if current is None:
        return

    topo_sorted = topoSort(adj)
    columns = decide_columns(topo_sorted, adj, current, nodes)
    parents = adj_reverser(adj)
    active_columns = set()

    last_in_column = _find_last_nodes_by_column(topo_sorted, columns)

    for node in topo_sorted:
        parent_cols = []
        column = columns[node]
        children = adj[node]
        for parent in parents.get(node, []):
            if columns[parent] != column:
                parent_cols.append(columns[parent])

        if parent_cols:
            print(
                _build_fork_row(column, parent_cols, active_columns, to_the_right=False)
            )

        _render_node(node, nodes, adj, columns, active_columns)

        child_cols = []
        for child in children:
            if columns[child] != column:
                child_cols.append(columns[child])

        if child_cols:
            print(_build_fork_row(column, child_cols, active_columns))

        if last_in_column[column] != node:
            print(_build_connector(active_columns))
        else:
            active_columns.discard(column)

    print("adj:", adj)
    print("topo:", topo_sorted)
    print("columns:", columns)
