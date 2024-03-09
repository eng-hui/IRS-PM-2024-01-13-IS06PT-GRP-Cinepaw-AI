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

from utils import logger

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


app = FastAPI()


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
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are cinebear, a happy bear who love movies and love to share with friends",
            }
        ]
        + history
        + [
            {
                "role": "user",
                "content": text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    text = chat_completion.dict()["choices"][0]["message"]["content"]
    timestamp = int(datetime.datetime.now().timestamp())
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
    return tmp


def input_parse(input: ChatInput):
    pass
