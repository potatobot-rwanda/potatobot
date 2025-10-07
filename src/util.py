import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
from typing import List, Any, Tuple
import getpass
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

def load_openai_api_key():
    load_dotenv(
        dotenv_path=os.path.join(os.path.dirname(__file__), ".env")
    )

    print(os.path.exists(os.path.join(os.path.dirname(__file__), ".env")))
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        API_KEY = getpass.getpass("Enter your OPENAI_API_KEY: ")

    return API_KEY

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

# https://python.langchain.com/v0.1/docs/modules/callbacks/
# custom langchain callback to log llm details
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
