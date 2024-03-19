import os
from openai import OpenAI
# from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader, Template, meta, select_autoescape
from utils import logger

jinja_env = Environment(
    loader=FileSystemLoader("templates"), autoescape=select_autoescape()
)


backend = "openai"
if backend == "openai":
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    client_chat = client.chat.completions.create
else:
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

def client_chat(messages, model_name=None):
    if model_name is None:
        pass

    if backend=="openai":
        model_name = "gpt-4"
        result = client.chat.completions.create(
            messages = messages,
            model_name = model_name
        )
    else:
        model_name = "claude-3-opus-20240229"
        result = client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=messages
        )    
    return result    



def chat(text, history, template="bear.jinja2"):
    logger.info(history)
    template = jinja_env.get_template(template)
    text = template.render(text=text)
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
                "role": "system",
                "content": text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    text = chat_completion.dict()["choices"][0]["message"]["content"]
    return text