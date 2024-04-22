"""
Intepret user's preference and mark
"""

from chatbot import chat
from utils import logger
from actions.search import convert_tmdb_to_mvlen
from db import UserPreference, USER_ID, save_user_preference
import json

def preference_inteprete(text, history):
    result = chat(text, history, template="preference.jinja2", json=True)
    logger.info("=========")
    logger.info("preference_inteprete:")
    logger.info(result)
    result = json.loads(result)
    if result.get("movies"):
        result = result.get("movies")
    if isinstance(result, dict):
        p = result
        title = p.get("title")
        movie = convert_tmdb_to_mvlen(title)
        logger.info(movie)
        if movie is not None:
            u = dict(
                user_id=USER_ID,
                movie_id=int(movie["movie_id"]),
                movie_title=movie["title"],
                quote=p.get("quote"),
                score=p.get("score")
            )
            save_user_preference(u)
    else:
        for p in result:
            title = p.get("title")
            movie = convert_tmdb_to_mvlen(title)
            logger.info(movie)
            if movie is not None:
                u = dict(
                    user_id=USER_ID,
                    movie_id=int(movie["movie_id"]),
                    movie_title=movie["title"],
                    quote=p.get("quote"),
                    score=p.get("score")
                )
                save_user_preference(u)
    return result

def mark_preference_score(movie, score):
    pass

def watched(movie, when=None):
    pass
