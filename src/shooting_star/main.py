from typing import TypedDict, cast

# from shooting_star.anidb import AniDBClient
from shooting_star.anilist import AniListClient, RelationGraph
from shooting_star.formatter import AnimeCard, RelationCard


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
    response = []
    while True:
        anilist = AniListClient(mock=False)
        print("What do you want")
        print("[1] Search by title")
        print("[2] Get an info card (id needed)")
        print("[3] Get relations (id needed)")
        print("[q] Exit")
        user_input = input("> ")

        match user_input:
            case "1": #search
                input_title = input("Enter title: ")
                input_amount = input("Enter max amount of responses (default = 5): ").strip()
                if input_amount == "":
                    response = anilist.search(input_title)
                else: 
                    response = anilist.search(input_title, int(input_amount))

                print(response)

            case "2": #anime card
                input_anime_id = input("Enter id (leave empty if the first response is what you are looking for): ").strip()
                if input_anime_id != "":
                    anime_id = int(input_anime_id)
                elif response:
                    anime_id = response[0]['id']
                else:
                    print("Seach for an anime first or provide an ID")
                    continue

                data = cast(AnimeData, anilist.get_anime(anime_id))
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
            case "3": #relations
                pass
            case "q":
                break
            case "t":
                r_card = RelationCard(
                    title="Some Name",
                    format="Movie",
                    episodes=59,
                    year=2222,
                )

                for line in r_card._build_card_body():
                    print(line)
            case _:
                pass

    # response = anilist.search("Gundam", 5)
    # print(response)
    # relations = anilist.get_relations(response[0]['id'])
    # print("-----------------")
    # print(relations)
    # print("-----------------")
    # graph = anilist.build_graph(response[0]["id"])
    # print(graph)
    # id = response[0]['id']
    # data = cast(AnimeData, anilist.get_anime(21268))
    # card = AnimeCard(
    #     title=data["title"]["english"],
    #     format=data["format"],
    #     episodes=data["episodes"],
    #     year=data["seasonYear"],
    #     status=data["status"],
    #     score=data["averageScore"],
    #     studio=data["studios"]["nodes"][0]["name"],
    #     genre=", ".join(data["genres"]),
    #     description=data["description"],
    # )
    # card.render()


if __name__ == "__main__":
    main()
