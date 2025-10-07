import getpass
import os
from enum import Enum
import json
from typing import List, Any, Dict, Tuple
from multiprocessing import Lock
import concurrent.futures
import logging
from logging.handlers import RotatingFileHandler
import requests

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI

from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

from util import init_logging, load_openai_api_key, CustomCallback

API_KEY = load_openai_api_key()
NLU_API_URL = os.environ.get("NLU_API_URL", "http://localhost:8001")

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
                "id": "potato_variety",
                "description": "Which potato variety does the farmer use?",
                "value": None
            },
        ]

        prompt =  open("prompts/generate_answer.txt").read()
        self.generate_answer_chain = PromptTemplate.from_template(prompt) | self.llm | StrOutputParser()

    # fill one of the slots with a value
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

    def ner(self, user_message : str, chat_history : List[str]) -> List[Dict[str, Any]]:
        response = requests.post(
            f"{NLU_API_URL}/api/ner",
            json={
                "user_message": user_message,
                "chat_history": chat_history
            },
            timeout=10
        )
        ner_results = response.json().get("ner_results")
        for r in ner_results:
            self.fill_slot(r["entity_class"], r["surface_value"])

        return ner_results
        
    # main chat pipeline
    # present result to the user
    def get_response(self, user_message : str, chat_history : List[str]):

        self.ner(user_message, chat_history)
        
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