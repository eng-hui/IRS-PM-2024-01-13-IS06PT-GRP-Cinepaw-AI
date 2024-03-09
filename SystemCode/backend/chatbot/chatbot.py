
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def bear_chat(text, history):
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