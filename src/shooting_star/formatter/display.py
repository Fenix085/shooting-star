from dataclasses import dataclass
from rich import box
from rich.table import Table
from rich.console import Console
from io import StringIO


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

WIDTH = 25
LEFT = WIDTH//2
RIGHT = WIDTH//2
@dataclass
class RelationCard:
    title: str
    format: str
    episodes: int
    year: int

    def _build_card_body(self) -> list[str]:
        title = self.title[:WIDTH]
        line1 = "┌" + "─" * WIDTH + "┐"
        line2 = "│" + f"{title:^{WIDTH}}" + "│"
        line3 = "├" + "─" * LEFT + "┬" + "─" * RIGHT + "┤"
        line4 = "│" + f"{self.format} - {self.episodes}".center(LEFT) + "│" + f"{self.year:^{RIGHT}}" + "│"
        line5 = "└" + "─" * LEFT + "┴" + "─" * RIGHT + "┘"
        return [line1, line2, line3, line4, line5]
