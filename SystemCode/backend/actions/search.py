import os
import requests
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from utils import logger
TMDB_API_KEY = os.getenv("TMDB_API")
POSTER_URL = "https://media.themoviedb.org/t/p/w440_and_h660_face"
TMBD_QUERY_API = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
mnames = ['movie_id','title','genres']
# movies = pd.read_csv('../experiments/datasets/ml-1m/movies.dat',sep='::',header=None,names=mnames,encoding="unicode_escape")
movies = pd.read_csv("../experiments/datasets/ml-25m/movies.csv")
movies["movie_id"] = movies["movieId"]
lbe = LabelEncoder()
movies["raw_genres"] = movies["genres"].copy()
movies["genres"] = movies["genres"].apply(lambda x:x.split("|")[0])
movies["genres"] = lbe.fit_transform(movies["genres"]) + 1

def query_tmdb(title):
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
    if len(re.get("results"))>0:
        return re.get("results")[0]
    else:
        return None

import difflib
def get_smilar_score(s_1, s_2):
    return difflib.SequenceMatcher(None, s_1, s_2).quick_ratio()

def convert_tmdb_to_mvlen(tmdb_title):
    mvlen_result = movies[movies["title"].apply(lambda x:tmdb_title.lower() in x.lower())]
    if len(mvlen_result) > 0:
        mvlen_result["score"] = mvlen_result["title"].apply(lambda x:get_smilar_score(tmdb_title.lower(), x.lower()))
        mvlen_result = mvlen_result.sort_values("score", ascending=False)
        return mvlen_result.iloc[0]
    else:
        return None

def movie_id_to_genre(movie_id):
    logger.info(movie_id)
    logger.info(movies["movie_id"])
    genres_id = movies[movies["movie_id"].apply(int)==int(movie_id)]["genres"].tolist()[0]
    return genres_id

def mvlen_filter_search(filters):
    m = movies.copy()
    if filters.get("title"):
        m = m[m["title"].str.contains(filters.get("title"))]
    
    if filters.get("genres"):
        m = m[m["raw_genres"].str.contains(filters.get("genres"))]
    return m
    