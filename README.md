# PotatoBot

<img src="https://github.com/potatobot-rwanda/potatobot/blob/main/chatbot/static/potatobot.png" width="250" style="float:left">

This is the PotatoBot, a chatbot that can help farmers in Rwanda with information about: "When should I spray my potatoes"?

## Table of Contents

* [Getting started](#getting-started)
  + [Local development setup](#local-development-setup)
* [Technical Architecture](#technical-architecture)
  + [Repository File and Folder Structure](#repository-file-and-folder-structure)
  + [Technologies used in the chatbot](#technologies-used-in-the-chatbot)
* [Notes on chatbot development](#notes-on-chatbot-development)
  + [Running the chatbot from console](#running-the-chatbot-from-console)
  + [Logfiles](#logfiles)
  + [Caching](#caching)
* [License](#license)

## Getting started

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
cd chatbot
python api.py
```

**6.In a new terminal, start the Streamlit app:**
```
cd chatbot
streamlit run app.py
```

The application will be available at:
- Streamlit Interface: http://localhost:8502
- FastAPI: http://localhost:8000

## Technical Architecture

### Repository File and Folder Structure

```
.
├── chatbot/
│   ├── app.py          # Streamlit frontend
│   ├── api.py          # FastAPI backend
│   ├── animalbot.py    # Core chatbot logic
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
cd chatbot
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
