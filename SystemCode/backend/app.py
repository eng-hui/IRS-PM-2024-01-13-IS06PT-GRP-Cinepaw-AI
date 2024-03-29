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
from actions import query_movie_db
from db import save_msg, USER_ID
from model import model_recommend

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




async def chat_background(input: ChatInput, background_tasks:BackgroundTasks):
    logger.info(input)
    text = input.text
    history = input.history
    history = assemble_history_message(history)
    chat_result = chat(text, history)

    input_msg = {
        "content": input.text,
        "role":"user",
        "session_key":input.session_key
    }
    save_msg(input_msg)

    logger.info(chat_result)
    result = json.loads(chat_result)

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
    msg["session_key"] = input.session_key
    save_msg(msg)
    produce_chat_message(msg, session_key=input.session_key)
    return "ok"

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
