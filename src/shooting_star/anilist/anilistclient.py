import requests
from collections import deque

from ..common.ratelimiter import RateLimiter
from .mockdata import MOCK_RESPONSES


class AniListClient:
    def __init__(self, mock=False) -> None:
        self.mock = mock
        self.url = "https://graphql.anilist.co"
        self.limiter = RateLimiter(min_interval=0.7)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "shooting-star/0.1 (https://github.com/Fenix085/shooting-star)",
                "Accept": "application/json",
            }
        )

    def _request(self, query, variables):
        self.limiter.wait()
        response = self.session.post(
            self.url,
            json={"query": query, "variables": variables},
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errors"):
            message = data["errors"][0].get("message", "AniList request failed")
            raise RuntimeError(
                f"AniList request failed ({response.status_code}): {message}"
            )

        return data["data"]

    def search(self, name, limit=5):
        if self.mock:
            return self._mock_search(name, limit)
        query = """
        query ($name: String!, $limit: Int!) {
            Page(perPage: $limit) {
                media(search: $name, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                    }
                }
            }
        }
        """

        variables = {
            "name": name,
            "limit": limit,
        }

        return self._request(query, variables)["Page"]["media"]

    def get_anime(self, aid):
        if self.mock:
            resp = MOCK_RESPONSES.get(aid)
            if resp is None:
                raise RuntimeError(f"Mock: no data for id {aid}")
            return resp["data"]["Media"]

        query = """
        query ($id: Int!) {
            Media(id: $id) {
                id
                title {
                    romaji
                    english
                }
                format
                status
                episodes
                season
                seasonYear
                averageScore
                genres
                description
                studios {
                    nodes {
                        name
                        isAnimationStudio
                    }
                }
            }
        }
        """
        variables = {"id": aid}

        return self._request(query, variables)["Media"]

    def get_relations(self, aid):
        if self.mock:
            resp = MOCK_RESPONSES.get(aid)
            if resp is None:
                raise RuntimeError(f"Mock: no data for id {aid}")
            return resp["data"]

        query = """
        query ($id: Int!) {
            Media(id: $id){
                id
                title {
                    romaji
                    english
                }
                format
                episodes
                seasonYear
                relations {
                    edges {
                        relationType
                        node {
                            id
                            title {
                                romaji
                                english
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            "id": aid,
        }

        return self._request(query, variables)

    def build_graph(self, aid):
        graph = {}
        q = deque([aid])
        visited = set()
        while q:
            current = q.popleft()

            if current in visited:
                continue
            visited.add(current)

            data = self.get_relations(current)["Media"]
            edges = []
            for edge in data["relations"]["edges"]:
                rel_type = edge["relationType"]
                neighbor = edge["node"]
                nid = neighbor["id"]

                edges.append((rel_type, nid))

                if nid not in visited:
                    q.append(nid)

            graph[current] = {
                "title": data["title"],
                "edges": edges,
            }
        return graph

    def _mock_search(self, name, limit):
        """API is down, so here we go."""
        return [
            response["data"]["Media"]
            for response in MOCK_RESPONSES.values()
            if name.lower() in response["data"]["Media"]["title"]["romaji"].lower()
        ][:limit]
