# PotatoBot

This is the PotatoBot.


## Local Development Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
CHAT_AI_ACCESS_KEY=your_api_key_here
```

4. Start the FastAPI server:
```bash
cd chatbot
uvicorn chatbot_api:app --host 0.0.0.0 --port 8001 --reload
```

5. In a new terminal, start the Streamlit app:
```bash
cd chatbot
streamlit run chatbot_ui.py
```

The application will be available at:
- Chatbot User Interface Streamlit Interface: http://localhost:8000
- FastAPI: http://localhost:8001

## Features

- Dynamically switches between duck and fox personalities
- Uses LLMs from chat-ai.academiccloud.de
- Logs conversation history and classification details

## Running Locally

To run the chatbot locally without Docker:

1. Make sure you have Python 3.8+ installed
2. Create a `.env` file in the project root with your API key
3. Run:
   ```bash
   cd ..  # Go to project root
   python -m chatbot.animalbot
   ```

For Docker-based deployment, see the main project README.

## Helpful Commands

### Docker Compose Commands

Run a single instance with default settings:
```bash
docker compose -p animalbot up -d
```

Run multiple instances with custom ports:
```bash
# Instance 1
API_PORT=8003 UI_PORT=8504 API_BASE_URL=http://localhost docker compose -p animalbot1 up -d

# Instance 2
API_PORT=8005 UI_PORT=8506 API_BASE_URL=http://localhost docker compose -p animalbot2 up -d
```

Use current directory name as project name:
```bash
API_PORT=8003 UI_PORT=8504 API_BASE_URL=http://localhost docker compose -p $(basename "$PWD") up -d
```

### Viewing Logs

View logs from a specific instance:
```bash
docker logs $(docker ps -qf "name=animalbot_animalbot")
```

Follow logs in real-time:
```bash
docker logs -f $(docker ps -qf "name=animalbot_animalbot")
```

### Managing Containers

Stop a specific instance:
```bash
docker compose -p animalbot1 down
```

Rebuild and restart after code changes:
```bash
docker compose -p animalbot build --no-cache
docker compose -p animalbot up -d
```

List all running instances:
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```