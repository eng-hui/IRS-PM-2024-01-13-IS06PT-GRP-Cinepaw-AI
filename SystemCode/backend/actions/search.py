import os
TMDB_API_KEY = os.getenv("TMDB_API")


def query_movie_db(title):
    import urllib.parse
    title = title
    urllib.parse.quote(title)
    query = f"&query={title}"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    url = TMBD_QUERY_API + query
    re = requests.get(url, headers=headers).json()
    return re.get("results")[0]