import os
import requests
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from utils import logger
import chromadb
chroma_client = chromadb.PersistentClient(path="../experiments/chroma_data")

file_location = os.path.abspath(__file__)
exp_folder = os.path.join(os.path.dirname(file_location),"..","..","experiments")    

TMDB_API_KEY = os.getenv("TMDB_API")
POSTER_URL = "https://media.themoviedb.org/t/p/w440_and_h660_face"
TMBD_QUERY_API = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
mnames = ['movie_id','title','genres']
# movies = pd.read_csv('../experiments/datasets/ml-1m/movies.dat',sep='::',header=None,names=mnames,encoding="unicode_escape")
movies = pd.read_csv(os.path.join(exp_folder,"datasets","ml-25m","xdf.csv"))
if "movieId" in movies:
    movies["movie_id"] = movies["movieId"]
lbe = LabelEncoder()
movies["raw_genres"] = movies["genres"].copy()
movies["genres"] = movies["genres"].apply(lambda x:x.split("|")[0])
movies["genres"] = lbe.fit_transform(movies["genres"]) + 1

def query_tmdb_detail(id):
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
    re = requests.get(url, headers=headers)
    logger.info(re.json())
    return re.json()


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
    mvlen_result = movies[movies["title"].apply(lambda x:tmdb_title.lower() in str(x).lower())]
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

    if filters.get("actors"):
        m = m[m["tag"].str.lower().str.contains(filters.get("actors").lower())]
    
    #tmp
    m = m[m["year"]>1980]
    return m
    

def chroma_movie_query(query):
    collection = chroma_client.get_or_create_collection("movie_rec_25m_text_emb")
    logger.info(query)
    df = pd.DataFrame(collection.query(query_texts=[query], n_results=50)["metadatas"][0])
    logger.info(df)
    return df[["movie_id", "title", "hot", "grade"]].sort_values(["hot", "grade"], ascending=False)