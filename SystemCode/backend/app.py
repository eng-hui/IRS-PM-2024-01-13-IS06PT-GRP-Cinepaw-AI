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
    session_key: str = None



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

@app.post("/chat_test")
async def chat_test(input: ChatInput, background_tasks:BackgroundTasks):
    print(input)
    text = input.text
    history = input.history
    history = assemble_history_message(history)
    chat_result = chat(text, history)

    logger.info(chat_result)
    json_dump = json.dumps(chat_result)
    try:
        result = json.loads(json.loads(json_dump))
    except:
        result = json.loads(json_dump)

    # check intent
    intents = result.get("intents", [])
    if "expression" in intents:
        background_tasks.add_task(preference_inteprete, text=text, history=history)

    text = result["reply"]
    movies = result.get("movies")
    logger.info(movies)

    blocks = []
    if movies is not None:
        for x in movies:
            title = x.get("title")
            if title:
                movie = query_movie_db(title)
                movie["block_type"] = "movie"
                blocks.append(movie)
    
    logger.info(blocks)
    msg = await construct_result(text, blocks=blocks)
    return msg


@app.post("/chat_input")
def chat_input(input: ChatInput):
    session_key = input.session_key
    text = input.text
    history = input.history
    history = [{"content": x["content"], "role": x["role"]} for x in history]
    text = chat(text, history, template="bear.jinja2")
    logger.info(text)
    result = json.loads(text)
    text = result["reply"]
    query = result.get("search")
    background_tasks.add_task(post_to_zendesk, result=result)

@app.get("/consume_messgae/<session_key>")
async def consume_message_api(session_key):
    msg = consume_chat_message(session_key)
    return msg

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

def input_parse(input: ChatInput):
    pass


def reply_construct():
    pass

def assemble_history_message(raw_history):
    result = []
    for x in raw_history:
        tmp = {"content": x["content"], "role": x["role"]}

        rec_movies = "Recommend Movies: "
        for b in x.get("blocks", []):
            if b["block_type"] == "movie":
                rec_movies += f"<Movie: {b['title']}> "
        
        tmp["content"] = x["content"] +"\n===\n" + rec_movies
        result.append(tmp)
    return result