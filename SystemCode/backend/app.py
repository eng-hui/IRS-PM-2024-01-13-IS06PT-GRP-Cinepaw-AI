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

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


app = FastAPI()


POSTER_URL = "https://media.themoviedb.org/t/p/w440_and_h660_face"
TMBD_QUERY_API = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
TMDB_API_KEY = os.getenv("TMDB_API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get("/")
async def index():
    return {"hello": "world"}


class ChatInput(BaseModel):
    text: str
    history: List = []


@app.post("/chat_test")
async def chat_test(input: ChatInput):
    text = input.text
    history = input.history
    history = [{"content": x["content"], "role": x["role"]} for x in history]
    text = chat(text, history)
    logger.info(text)
    result = json.loads(text)
    text = result["reply"]
    query = result.get("search")

    
    timestamp = int(datetime.datetime.now().timestamp()*1000)
    # no search action
    if (query is None) or (len(query)==0):
        tmp = {
            "content": text,
            "createAt": timestamp,
            "extra": {},
            "id": "2",
            "meta": {
                "avatar": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                "title": "cinebear",
            },
            "role": "assistant",
            "updateAt": timestamp,
        }
        messages = tmp
        return messages
    else:

        title = query["title"]
        movie = query_movie_db(title)
        logger.info(query)
        text = f"""{text}"""
        tmp = {
            "content": text,
            "createAt": timestamp,
            "extra": {},
            "id": "2",
            "image":{POSTER_URL+movie["poster_path"]},
            "meta": {
                "avatar": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                "title": "cinebear",
            },
            "role": "assistant",
            "updateAt": timestamp,
        }
        return tmp


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
    logger.info(re)
    return re.get("results")[0]

def input_parse(input: ChatInput):
    pass
