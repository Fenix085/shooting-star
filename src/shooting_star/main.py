from shooting_star.anidb import AniDBClient
from shooting_star.anilist import AniListClient

def main():
    anilist = AniListClient(mock=True)

    response = anilist.search("Stein", 2)
    print(response)
    relations = anilist.get_relations(response[0]['id'])
    print("-----------------")
    print(relations)
    print("-----------------")
    graph = anilist.build_graph(response[0]["id"])
    print(graph)

    
if __name__ == "__main__":
    main()