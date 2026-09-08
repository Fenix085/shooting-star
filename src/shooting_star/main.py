from shooting_star.anidb import AniDBClient
from shooting_star.anilist import AniListClient

def main():
    anilist = AniListClient(mock=True)

    print(anilist.search("Bebop", 2))

    
if __name__ == "__main__":
    main()