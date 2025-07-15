from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from potatobot import PotatoBot, LogWriter, init_logging
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

log_writer = LogWriter()

init_logging()

# CORS für lokale Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary für Session-spezifische Agenten
session_agents: Dict[str, PotatoBot] = {}

class ChatMessage(BaseModel):
    message: str
    chat_history: List[str] = []
    session_id: str

class ChatResponse(BaseModel):
    response: str
    log_message: Dict[str, Any]

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        # Prüfen ob eine Session-ID existiert, sonst neue erstellen
        if chat_message.session_id not in session_agents:
            session_agents[chat_message.session_id] = PotatoBot()
        
        agent = session_agents[chat_message.session_id]
        response, log_message = agent.get_response(
            chat_message.message, 
            chat_message.chat_history
        )
        log_writer.write(log_message)
        return ChatResponse(
            response=response,
            log_message=log_message
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 