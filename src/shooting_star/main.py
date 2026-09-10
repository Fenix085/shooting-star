from typing import TypedDict, cast

# from shooting_star.anidb import AniDBClient
from shooting_star.anilist import AniListClient
from shooting_star.formatter import AnimeCard


class AnimeData(TypedDict):
    title: dict[str, str]
    format: str
    episodes: int
    seasonYear: int
    status: str
    averageScore: float
    studios: dict
    genres: list[str]
    description: str


def main():
    anilist = AniListClient(mock=True)

    # response = anilist.search("Stein", 2)
    # print(response)
    # relations = anilist.get_relations(response[0]['id'])
    # print("-----------------")
    # print(relations)
    # print("-----------------")
    # graph = anilist.build_graph(response[0]["id"])
    # print(graph)

    data = cast(AnimeData, anilist.get_anime(9253))
    card = AnimeCard(
        title=data["title"]["english"],
        format=data["format"],
        episodes=data["episodes"],
        year=data["seasonYear"],
        status=data["status"],
        score=data["averageScore"],
        studio=data["studios"]["nodes"][0]["name"],
        genre=", ".join(data["genres"]),
        description=data["description"],
    )
    card.render()


if __name__ == "__main__":
    main()
