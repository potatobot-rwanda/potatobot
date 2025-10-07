# PotatoBot

<img src="https://github.com/potatobot-rwanda/potatobot/blob/main/chatbot/static/potatobot.png" width="250" style="float:left">

This is the PotatoBot, a chatbot that can help farmers in Rwanda with information about: "When should I spray my potatoes"?

## Table of Contents

[Table of Contents](#table-of-contents)

[Getting started](#getting-started)

- [Reading list](#reading-list)
- [Local development setup](#local-development-setup)
  
[Technical Architecture](#technical-architecture)

- [Repository File and Folder Structure](#repository-file-and-folder-structure)
- [Technologies used in the chatbot](#technologies-used-in-the-chatbot)

[Notes on chatbot development](#notes-on-chatbot-development)
- [Running the chatbot from console](#running-the-chatbot-from-console)
- [Logfiles](#logfiles)
- [Caching](#caching)

[License](#license)


## Getting started

### Reading list

* [What is Agentic AI?](https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents)
* LangChain Tutorials
  * [Chat models and prompts](https://python.langchain.com/docs/tutorials/llm_chain/): Build a simple LLM application with [prompt templates](https://python.langchain.com/docs/concepts/prompt_templates/) and [chat models](https://python.langchain.com/docs/concepts/chat_models/).
  * [Extraction: Extract structured data from text and other unstructured media using chat models and few-shot examples.](https://python.langchain.com/docs/tutorials/extraction/)
* [Introduction to StreamLit](https://docs.streamlit.io/get-started/fundamentals/main-concepts)
* [FastAPI - First Steps](https://fastapi.tiangolo.com/tutorial/first-steps)

### Local development setup

**1. Prerequisites**

* Install Python 3.11 or higher.
* Acquire your OpenAI API Key.
* Install Git

**2. Fork and clone the GitHub repository**

* One member of your group should fork this repository to his or her account.
* Then, you can git clone this repository.
* We assume for the remaining installation steps that you opened a shell inside of the cloned repository.

**3. Setup local environment and install Python dependencies**

Create environment
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

**4. Setup OpenAI API Key**

Create a `.env` file in the project root and paste your API Key. The file should have this content:

```
OPENAI_API_KEY=your_api_key_here
```

**5. Start the FastAPI server:**
```
cd src
python chatbot_api.py
```

**6.In a new terminal, start the Streamlit app:**
```
cd src
streamlit run chatbot_ui.py
```

The application will be available at:
- Streamlit Interface: http://localhost:8502
- FastAPI: http://localhost:8000

## Technical Architecture

### Architecture High-Level Overview

<img src="https://github.com/potatobot-rwanda/potatobot/blob/main/images/architecture-high-level-overview.drawio.png" width="700" style="float:left">

The image shows the architecture of the chatbot.

1. The user accesses the chatbot via the webbrowser.
2. The docker container chatbot is maintained by the chatbot team.
3. The NGINX reverse proxy maps the different ports of the user interface and the chat interface to one single server on port 80 to prevent [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS) issues.
4. The user interface is hosted by the streamlit app. It runs on port 8000.
5. When the user sends a message, the message is sent to the Chatbot HTTP API. This runs on port 8001.
6. The chatbot API calls the PotatoBot. The PotatoBot handles the chatbot logic and the answer generation.
7. The PotatoBot uses Large Language Models hosted by OpenAI to generate the answer.
8. The AI Models docker container is maintained by the AI-models team.
9. The PotatoBot accesses the AI models via AI Models HTTP API, which runs on port 8002.
10. The entity recognition models detect locations, temporal expressions and potato varieties in the text. By default, they also use OpenAIs Large Language Models for the detection.
11. The Location Linking service helps to link the location as mentioned in the user's message to the database.
12. The Potato Detector links the potato variety as mentioned in the user's message to the database.
13. Temporal Expression Normalization converts dates mentioned in the text (e.g. three days ago) to a specific date (22.7.2025).

### Repository File and Folder Structure

```
.
├── src/
├────── prompts/            # Chatbot prompts
│   ├── webapp.py       # Streamlit frontend
│   ├── chatbot_api.py  # FastAPI backend that wraps an HTTP API around the chatbot
│   ├── potatobot.py    # Chatbot logic
│   └── Dockerfile      # Docker configuration
├── data/               # Data directory
├── requirements.txt    # Python dependencies
├── compose.yml         # Docker Compose configuration
└── .env               # Environment variables (not in git)
```

### Technologies used in the chatbot

- The frontend is built with Streamlit
- The backend uses FastAPI
- The chatbot logic is in `potatobot.py`
- Docker configuration is in `Dockerfile` and `compose.yml`

## Notes on chatbot development

### Running the chatbot from console

You can run chatbot also without the web browser based graphical user interface. You can run `potatobot.py` directly from the console:

```
cd src
python potatobot.py
```

You can find two types of console interfaces in `potatobot.py`:

* `static_dialog()` runs a static dialog. So it automatically sends one or more messages to the chatbot. This is useful for debugging the chatbot.
* `console_chatloop()` lets you chat in the console.

You can activate the function by changing the code in the `if __name__ == "__main__":` section of `potatobot.py`.

### Logfiles

The chatbot produces two logfiles:

* `app.log` contains technical logs
* `conversation.jsonp` contains detailed information about the chatbot, the NLU, the LLMs and more in a machine readable format. It stores one each user message, chatbot answer and related information as a JSON object, one object per line. 

### Caching

To save money / OpenAI LLM credits, the system uses a cache. If you execute the same LLM request a second time, it will be loaded from cache, instead of from the OpenAI API. The cache is stored in `.langchain.db`. You can delete the file to reset the cache.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
