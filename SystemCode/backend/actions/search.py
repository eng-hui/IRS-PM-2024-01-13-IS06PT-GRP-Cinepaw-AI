import os
import requests
import pandas as pd
from sklearn.preprocessing import LabelEncoder
TMDB_API_KEY = os.getenv("TMDB_API")
POSTER_URL = "https://media.themoviedb.org/t/p/w440_and_h660_face"
TMBD_QUERY_API = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
mnames = ['movie_id','title','genres']
movies = pd.read_csv('../experiments/datasets/ml-1m/movies.dat',sep='::',header=None,names=mnames,encoding="unicode_escape")
#movies = pd.read_csv("../experiments/datasets/ml-25m/movies.csv")
lbe = LabelEncoder()
movies["genres"] = movies["genres"].apply(lambda x:x.split("|")[0])
movies["genres"] = lbe.fit_transform(movies["genres"]) + 1

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


def convert_tmdb_to_mvlen(tmdb_title):
    mvlen_result = movies[movies["title"].apply(lambda x:tmdb_title.lower() in x.lower())]
    if len(mvlen_result) > 0:
        return mvlen_result.iloc[0]
    else:
        return None

def movie_id_to_genre(movie_id):
    genres_id = movies[movies["movie_id"]==movie_id]["genres"].tolist()[0]
    return genres_id
    