import requests

from ..common.ratelimiter import RateLimiter

class AniListClient():
    def __init__(self, mock = False) -> None:
        self.mock = mock
        self.url = "https://graphql.anilist.co"
        self.limiter = RateLimiter(min_interval=0.7)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "shooting-star/0.1 (https://github.com/Fenix085/shooting-star)",
            "Accept": "application/json",
        })

    def _request(self, query, variables):
        self.limiter.wait()
        response = self.session.post(
          self.url,
          json={'query': query, 'variables': variables},
        )
        response.raise_for_status()
        data = response.json()
        if data.get('errors'):
          message = data['errors'][0].get('message', 'AniList request failed')
          raise RuntimeError(f'AniList request failed ({response.status_code}): {message}')
        
        return data['data']

    def search(self, name, limit = 5):
        if self.mock:
            return self._mock_search(name, limit)
        query = '''
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
        '''

        variables = {
            'name': name,
            'limit': limit,
        }


        return self._request(query, variables)['Page']['media']

    def get_anime(self, id):
        pass

    def get_relations(self, id):
        pass

    def build_graph(self, id):
        pass

    def _mock_search(self, name, limit):
        """API is down, so here we go"""
        data = [
            {'id': 1, 'title': {'romaji': 'Cowboy Bebop', 'english': 'Cowboy Bebop'}},
            {'id': 5, 'title': {'romaji': 'Cowboy Bebop: Tengoku no Tobira', 'english': "Cowboy Bebop: Knockin' on Heaven's Door"}},
            {'id': 17, 'title': {'romaji': 'Shelter', 'english': 'Shelter'}},
        ]
        return [d for d in data if name.lower() in d['title']['romaji'].lower()][:limit]
