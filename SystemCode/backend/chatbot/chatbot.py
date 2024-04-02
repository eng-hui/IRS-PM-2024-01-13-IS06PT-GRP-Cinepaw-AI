import os
from openai import OpenAI,AzureOpenAI
# from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader, Template, meta, select_autoescape
from utils import logger
import json
from chatbot.previouschat import store_previouschat,retrieve_previouschats 

# get template from relative path for debug mode
file_location = os.path.abspath(__file__)
templates_folder = os.path.join(os.path.dirname(file_location),"..","templates")    

jinja_env = Environment(
    loader=FileSystemLoader(templates_folder), autoescape=select_autoescape()
)



backend = os.environ.get("DEFAULT_LLM_ENDPOINT") or "openai"

if backend == "openai":
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    client_chat = client.chat.completions.create
elif backend == "azure_openai":
    client = AzureOpenAI(
        azure_endpoint = os.environ.get("OPENAI_API_ENDPOINT"), 
        api_key= os.environ.get("OPENAI_API_KEY"),  
        api_version="2024-02-15-preview"
    )
    print(os.environ.get("OPENAI_API_ENDPOINT"),os.environ.get("OPENAI_API_KEY"))
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
    elif backend=="azure_openai":
        model_name = "gpt-35-turbo"
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



def chat(text, history, template="bear.jinja2",appendchat_template="appendchat.jinja2", prevchat_template="prevchat.jinja2"):
    logger.info(history)
    template = jinja_env.get_template(template)
    userinput = text

    template_text = template.render(text=userinput)

    # search top N historical results 
    prevchats_results = retrieve_previouschats(userinput,n_results=5)
    if len(prevchats_results["documents"]) > 0 and prevchats_results["documents"][0]!=[]:
        # merge history to template_text(current query) as content
        appendchat_template = jinja_env.get_template(appendchat_template)
        # append previous chat to current chat
        template_text = template.render(text="".join(prevchats_results["documents"][0]) +"\n =========== \n Answer current query:" + userinput)

    chat_completion = client.chat.completions.create(
        messages=history
        +[
            {
                "role": "user",
                "content": template_text,
            }
        ],
        model=os.environ.get("DEFAULT_MODEL") or "gpt-3.5-turbo",
    )
    output_text = chat_completion.dict()["choices"][0]["message"]["content"]
    # fix null values
    output_text = output_text.replace("null","[]")
    # convert and embed current enquiry + reply as previous chat then store to vector db for future retrieval
    reply = json.loads(output_text)["reply"]
    prevchat_template = jinja_env.get_template(prevchat_template)
    prevchat = prevchat_template.render(text=userinput, reply=reply)
    store_previouschat(prevchat)

    return output_text