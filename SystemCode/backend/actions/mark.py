"""
Intepret user's preference and mark
"""

from chatbot import chat
from utils import logger


def preference_inteprete(text, history):
    result = chat(text, history, template="preference.jinja2")
    logger.info("preference_inteprete:")
    return result

def mark_preference_score(movie, score):
    pass

def watched(movie, when=None):
    pass
