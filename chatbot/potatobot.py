import getpass
import os
from enum import Enum
import json
from typing import List, Any, Dict, Tuple
from multiprocessing import Lock
import concurrent.futures
import logging
from logging.handlers import RotatingFileHandler

from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI

from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

from dotenv import load_dotenv

POTATOBOT_API_URL = os.environ.get("POTATOBOT_API_URL", "http://localhost:8000")

def init_logging(console_level = logging.WARNING, file_level = logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
)

# Get API key from environment variable or prompt the user
load_dotenv("../.env")
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    API_KEY = getpass.getpass("Enter your OPENAI_API_KEY: ")

# custom langchain callback to log llm details
# https://python.langchain.com/v0.1/docs/modules/callbacks/
class CustomCallback(BaseCallbackHandler):

    def __init__(self):
        self.messages = {}

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> Any:
        self.messages["on_llm_start_prompts"] = prompts
        self.messages["on_llm_start_kwargs"] = kwargs

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:

        llm_generation = []
        for gen in response.generations:
            for gen2 in gen:
                llm_generation.append({
                    "text": gen2.text,
                    "generation_info": gen2.generation_info
                })

        self.messages["on_llm_end_response"] = llm_generation
        self.messages["on_llm_end_kwargs"] = kwargs

class PotatoBot:

    def __init__(self):

        # Initialize LLM using OpenAI-compatible API

        # Set custom base URL and API key directly in the ChatOpenAI initialization
        # Use the api_key that was determined outside of the class
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6,
            logprobs=True,
            openai_api_key=API_KEY,
        )

        self.slots = [
            {
                "id": "last_spray_date",
                "description": "When did the farmer last spray his or her potatoes?",
                "value": None
            },
            {
                "id": "location",
                "description": "What is the location of the farm?",
                "value": None
            },
            {
                "id": "plant_date",
                "description": "When did the farmer plant his potatoes?",
                "value": None
            },
            {
                "id": "potato_variety",
                "description": "Which potato variety does the farmer use?",
                "value": None
            },
        ]

        prompt =  open("prompts/generate_answer.txt").read()
        self.generate_answer_chain = PromptTemplate.from_template(prompt) | self.llm | StrOutputParser()

    # fill one of the slots with a predefined value
    def fill_slot(self, slot_id : str, slot_value : str):
        found = False
        for slot in self.slots:
            if slot["id"] == slot_id:
                found = True
                slot["value"] = slot_value
        assert found

    # get slot value
    def get_slot_value(self, slot_id : str):
        for slot in self.slots:
            if slot["id"] == slot_id:
                found = True
                return slot["value"]
            
        raise Exception(f"cannot find slot_id \"{slot_id}\"")

    # main chat pipeline
    # present result to the user
    def get_response(self, user_message : str, chat_history : List[str]):
        chat_history_str : str = "\n".join(chat_history)

        
        # are all slots filled?
        all_slots_filled = True
        for slot in self.slots:
            if slot["value"] is None:
                all_slots_filled = False
                break

        if all_slots_filled:
            api_results = "All slots filled. Please instruct the user to spray his potatoes in three days."
        else:
            api_results = ""

        response_callback = CustomCallback()
        chatbot_response = self.generate_answer_chain.invoke(
            {
                "user_message": user_message, 
                "chat_history": chat_history_str,
                "knowledge_base": json.dumps(self.slots, indent=4),
                "api_results": api_results
            },
            {
                "callbacks": [response_callback], 
                "stop_sequences": ["\n"]
            },
        )

        log_message = {
            "user_message": str(user_message),
            "chatbot_response": str(chatbot_response),
            "slots": self.slots,
            "answer_generation_llm_details": {
                key: value for key, value in response_callback.messages.items()
            },
            # "nlu_details": nlu_log_messages
        }

        return chatbot_response, log_message

# Write to the json logfile
class LogWriter:

    def __init__(self):
        self.conversation_logfile = "conversation.jsonp"
        if os.path.exists(self.conversation_logfile):
            os.remove(self.conversation_logfile)
        self.lock = Lock()

    # helper function to make sure json encoding the data will work
    def make_json_safe(self, value):
        if type(value) == list:
            return [self.make_json_safe(x) for x in value]
        elif type(value) == dict:
            return {key: self.make_json_safe(value) for key, value in value.items()}
        try:
            json.dumps(value)
            return value
        except TypeError as e:
            return str(value)

    def write(self, log_message):
        with self.lock:
            with open(self.conversation_logfile, "a") as f:
                f.write(json.dumps(self.make_json_safe(log_message)))
                f.write("\n")
                f.close()

# chat with the bot using the console
def console_chatloop():
    agent = PotatoBot()
    chat_history = []
    log_writer = LogWriter()

    while True:
        user_message = input("User: ")
        if user_message.lower() in ["quit", "exit", "bye"]:
            print("Goodbye!")
            break

        chatbot_response, log_message = agent.get_response(user_message, chat_history)
        print("Bot: " + chatbot_response)

        chat_history.extend("User: " + user_message)
        chat_history.extend("Bot: " + chatbot_response)

        log_writer.write(log_message)

# debug function - send a static dialog to the chatbot and get the answer
# use this for developing the chatbot
def static_dialog():

    logging.info("starting static dialog")

    agent : PotatoBot = PotatoBot()
    chat_history : List[str] = []
    log_writer : LogWriter= LogWriter()

    user_messages : List[str] = [
        "hello",
        "I sprayed my potatoes last saturday.",
        "Musanze, Northern Province",
        "My potatoes are 8 weeks old",
        "Ndamira"
    ]

    for user_message in user_messages:
        print("User: " + user_message)
        chatbot_response, log_message = agent.get_response(user_message, chat_history)
        print("Bot: " + chatbot_response)

        chat_history.append("User: " + user_message)
        chat_history.append("Bot: " + chatbot_response)

        log_writer.write(log_message)

if __name__ == "__main__":
    logger = init_logging()
    static_dialog()

    # console_chatloop()
