from dataclasses import dataclass
from rich import box
from rich.table import Table
from rich.console import Console


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
