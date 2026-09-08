from shooting_star.anidb import AniDBClient

def main():
    with AniDBClient() as client:
        client.encrypt()
        client.auth()
        print(client.command("MYLIST aid=1"))  

if __name__ == "__main__":
    main()