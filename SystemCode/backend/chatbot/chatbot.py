import os
from openai import OpenAI,AzureOpenAI
# from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader, Template, meta, select_autoescape
from utils import logger
from chatbot.message import produce_chat_message
from db import get_redis_conn
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



def chat(text, history, template="bear.jinja2",appendchat_template="appendchat.jinja2", prevchat_template="prevchat.jinja2", **kwargs):
    logger.info(history)
    template = jinja_env.get_template(template)
    userinput = text

    template_text = template.render(text=userinput, **kwargs)

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
        response_format = response_format,
        model=os.environ.get("DEFAULT_MODEL") or "gpt-4-turbo-preview",
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

class Chatbot(object):
    def __init__(self, session_key):
        self.session_key = session_key
        self._redis = get_redis_conn()

    def chat(self, text, history=None, require_json=True, template="bear.jinja2",appendchat_template="appendchat.jinja2", prevchat_template="prevchat.jinja2", **kwargs):
        if require_json:
            response_format = {"type": "json_object"}
        else:
            response_format = {"type": "text"}

        if history is None:
            history = self.get_status("history")

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
            response_format = response_format,
            model=os.environ.get("DEFAULT_MODEL") or "gpt-4-turbo-preview",
        )
        # fix null values
        if require_json:
            output_text = chat_completion.dict()["choices"][0]["message"]["content"]
            output_text = output_text.replace("null","[]")
            output_text  = json.loads(output_text)
            
            # convert and embed current enquiry + reply as previous chat then store to vector db for future retrieval
            reply = output_text.get("reply")
            prevchat_template = jinja_env.get_template(prevchat_template)
            prevchat = prevchat_template.render(text=userinput, reply=reply)
            store_previouschat(prevchat)
        else:
            output_text  = chat_completion.dict()["choices"][0]["message"]["content"]

        return output_text

    # def chat(self, text, history=None, require_json=True, template="bear.jinja2", **kwargs):
        # if require_json:
        #     response_format = {"type": "json_object"}
        # else:
        #     response_format = {"type": "text"}

        # if history is None:
        #     history = self.get_status("history")

    #     logger.info(history)
    #     template = jinja_env.get_template(template)
    #     text = template.render(text=text, **kwargs)
    #     logger.info(text)
    #     chat_completion = client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": "you are cinebear, a happy bear who love movies and love to share with friends",
    #             }
    #         ]
    #         + history
    #         + [
    #             {
    #                 "role": "system",
    #                 "content": text,
    #             }
    #         ],
    #         response_format = response_format,
    #         model=os.environ.get("DEFAULT_MODEL") or "gpt-4-turbo-preview",
    #     )
        # if require_json:
        #     result = json.loads(chat_completion.dict()["choices"][0]["message"]["content"])
        # else:
        #     result = chat_completion.dict()["choices"][0]["message"]["content"]
    #     return result
    
    def rerank(self, text, history=None, candidate_set=None, user_history=None):
        result = self.chat(
            text=text, 
            history=history, 
            template="rerank.jinja2",
            candidate_set=candidate_set, 
            user_history=user_history
        )
        logger.info(result)
        return result

    def send_message(self, text, blocks=None, debug=None):
        result = _construct_result(text, blocks)
        produce_chat_message(result, self.session_key)
        return result

    def add_history(self, text, role, blocks=None):
        status = get_status()
        if blocks is None:
            status["history"].append({"content":text, "role":role})
        else:
            # to do add block to text
            status["history"].append({"content":text, "role":role})
        self.set_status(status)

    def update_status(self, key, value):
        status = self.get_status()
        status["key"] = value
        self.set_status(status_dict=status)

    def get_status(self, key=None):
        status = json.loads(self._redis.get(f"cinepaw:{self.session_key}"))
        if key is None:
            return status
        else:
            return status.get(key)

    def set_status(self, status_dict):
        s = json.dumps(status_dict)
        self._redis.set(self.session_key, s)

    def _construct_result(self, text, blocks=None):
        timestamp = int(datetime.datetime.now().timestamp()*1000)
        tmp = {
            "content": text,
            "createAt": timestamp,
            "extra": {},
            "id": str(timestamp),
            "meta": {
                "avatar": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                "title": "emily",
            },
            "role": "assistant",
            "updateAt": timestamp,
        }
        if (blocks is not None) and (len(blocks)>0):
            tmp["blocks"] = blocks
        return tmp
