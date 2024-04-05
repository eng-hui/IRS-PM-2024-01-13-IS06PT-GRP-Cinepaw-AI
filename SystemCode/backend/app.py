import datetime
import os
from typing import List

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from pydantic import BaseModel
from chatbot import chat
import json
import requests
from utils import logger
import os
import uuid
from kombu import Connection, Exchange, Queue
from chatbot.message import produce_chat_message, consume_chat_message
from fastapi import BackgroundTasks
from actions.mark import preference_inteprete
from actions import query_tmdb
from db import save_msg, USER_ID
from model import model_recommend, get_user_embedding, load_user_history
from actions.search import mvlen_filter_search, query_tmdb_detail, chroma_movie_query
from actions.search import movies as mvlen
import pandas as pd
from chatbot.chatbot import Chatbot
import chromadb
from scipy.spatial.distance import cdist
import numpy as np

chroma_client = chromadb.PersistentClient(path="../experiments/chroma_data")
collection = chroma_client.get_or_create_collection("movie_rec_25m_0402")

app = FastAPI()

POSTER_URL = "https://media.themoviedb.org/t/p/w440_and_h660_face"
TMBD_QUERY_API = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
TMDB_API_KEY = os.getenv("TMDB_API")
AZURESPEECH_API_KEY = os.getenv("AZURESPEECH_API_KEY")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


class ChatInput(BaseModel):
    text: str
    history: List = []
    session_key: str


@app.get("/init_chat")
async def init_chat():
    session_key = uuid.uuid4().hex
    return {"session_key":session_key}


async def construct_result(text, blocks=None):
    timestamp = int(datetime.datetime.now().timestamp()*1000)
    tmp = {
        "content": text,
        "createAt": timestamp,
        "extra": {},
        "id": str(timestamp),
        "meta": {
            "avatar": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            "title": "cinebear",
        },
        "role": "assistant",
        "updateAt": timestamp,
    }
    if (blocks is not None) and (len(blocks)>0):
        tmp["blocks"] = blocks
    return tmp

# async def chat_search(user_id, text, history):
#     # first recall

#     # recommend by user history
#     recall_result = model_recommend(user_id=user_id, n_results=100)

#     # recommend by query
#     vector_match = await vector_search(query)


#     return recall_result


async def query_recall(text, history):
    chat_result = chat(text, history, json=True, template="query_recall.jinja2")
    filters = json.loads(chat_result)
    logger.info(filters)
    m = mvlen_filter_search(filters)
    return m




async def chat_background(input: ChatInput, background_tasks:BackgroundTasks):
    logger.info(input)
    logger.info("==================input==================")
    logger.info(input)
    logger.info("==================end of input==================")
    text = input.text
    history = input.history
    history = assemble_history_message(history)

    chatbot = Chatbot(session_key=input.session_key)
    chat_result = chatbot.chat(text, history, json=True)

    input_msg = {
        "content": input.text,
        "role":"user",
        "session_key":input.session_key
    }
    save_msg(input_msg)

    logger.info("==================output==================")
    logger.info(chat_result)
    result = chat_result
    logger.info("==================end of output==================")

    # check intent
    intents = result.get("intents", [])
    if "expression" in intents:
        background_tasks.add_task(preference_inteprete, text=text, history=history)

    if ("ask_for_search_or_recommend" in intents) or ("hint_for_search_or_recommend" in intents):
        movies = None
        reply = result["reply"]
        msg = await construct_result(reply)
        produce_chat_message(msg, session_key=input.session_key)

        # hard filter
        user_history = load_user_history(USER_ID)
        filters = chatbot.chat(text, history, require_json=True, template="build_query.jinja2")
        filter_result =  mvlen_filter_search(filters)
        matrix = collection.get(ids=filter_result["movieId"].apply(str).tolist(), include=["embeddings"])
        matrix = np.array(matrix["embeddings"])
        user_emb = get_user_embedding(USER_ID)
        distance = cdist(np.array(user_emb), matrix).min(axis=0)
        filter_result["distance"] = distance
        filter_result = filter_result.sort_values("distance")

        # rec & search
        rec_result = filter_result.head(200)
        logger.info(rec_result)
        # v_result = vector_search(query)
        #filters = chatbot.chat(text, history, require_json=True, template="build_query.jinja2")
        #query = filters.get("query")

        # rec_result = rec_result[rec_result["movie_id"].isin(set(filter_result["movie_id"]))]
        df = rec_result
        # v_result = chroma_movie_query(query)
        # v_result["v_score"] = 0
        # rec_result["v_score"] = 1
        # logger.info(v_result)
        # df = pd.merge(v_result, rec_result[["movie_id", "distance"]], how="left")
        df["movieId"] = df["movie_id"]
        # df["distance"] = df["distance"].fillna(df["distance"].max())
        #df = pd.concat([df, rec_result])
        df = df.sort_values(["hot", "grade"], ascending=False)


        # rank
        # df = pd.merge(df, mvlen[["movieId", "tmdbId"]], on="movieId", how="left")
        # logger.info(df.sort_values(["v_score", "distance"]).head(5))
        # movies = df.sort_values(["v_score", "distance"]).head(5).to_dict(orient="records")
        movies = df.head(5).to_dict(orient="records")
        logger.info(df[["title", "tag", "movieId", "tmdbId"]].head(5))
        rerank_result = chatbot.rerank(text, history,
        candidate_set=df.head(20).to_dict(orient="records"),
        user_history=user_history.head(10).to_dict(orient="records"))


        blocks = []
        # if movies is not None:
        #     for x in movies:
        #         title = x.get("title")
        #         if title:
        #             movie = query_tmdb(title.split("(")[0])
        #             if movie:
        #                 movie["block_type"] = "movie"
        #                 blocks.append(movie)


        # fetch detail from tmdb
        movies = rerank_result.get("movies")
        if movies is not None:
            for x in movies:
                movie = None
                tmdbId = x.get("tmdbId", None)
                if tmdbId is not None:
                    movie = query_tmdb_detail(id=tmdbId)
                else:
                    title = x.get("title")
                    movie = query_tmdb(title.split("(")[0])

                if movie:
                    movie["block_type"] = "movie"
                    blocks.append(movie)
        logger.info(blocks)
        msg = await construct_result(rerank_result.get("reply"), blocks=blocks)
        produce_chat_message(msg, session_key=input.session_key)
        return 
    
        
    text = result["reply"]
    msg = await construct_result(text)
    msg["session_key"] = input.session_key
    save_msg(msg)
    produce_chat_message(msg, session_key=input.session_key)
    return "ok"

@app.get("/get_speech_token")
async def get_speech_token():
    subscription_key = AZURESPEECH_API_KEY
    fetch_token_url = 'https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)
    return access_token
    
def query_movie_db(title):
    import urllib.parse
    urllib.parse.quote(title)
    query = f"&query={title}"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    url = TMBD_QUERY_API + query
    re = requests.get(url, headers=headers).json()
    return re.get("results")[0]

@app.post("/chat_input")
def chat_input(input: ChatInput, background_tasks:BackgroundTasks):
    background_tasks.add_task(chat_background, input=input, background_tasks=background_tasks)

@app.get("/sub_message/{session_key}")
async def consume_message_api(session_key):
    msg = consume_chat_message(session_key)
    timestamp = int(datetime.datetime.now().timestamp()*1000)
    # msg = {
    #     "content": "hello test",
    #     "createAt": timestamp,
    #     "extra": {},
    #     "id": "2",
    #     "meta": {
    #         "avatar": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    #         "title": "cinebear",
    #     },
    #     "role": "assistant",
    #     "updateAt": timestamp,
    # }
    if msg is None:
        result = {"success":False, "detail": "no new message"}
    else:
        result = {"success":True, "msg":msg}
    return result


def assemble_history_message(raw_history):
    result = []
    for x in raw_history:
        tmp = {"content": x["content"], "role": x["role"]}

        rec_movies = "Recommend Movies: "
        for b in x.get("blocks", []):
            if b["block_type"] == "movie":
                rec_movies += f"<Movie: {b['title']} movie_id:{b['id']}> "
        
        tmp["content"] = x["content"] +"\n===\n" + rec_movies
        result.append(tmp)
    return result

@app.get("/recommend")
async def recommend():
    user_id = USER_ID # tmp
    logger.info("hello")
    return model_recommend(user_id)
