import streamlit as st
import requests
import json
import uuid
import os

# Konfiguration der Seite
st.set_page_config(page_title="PotatoBot", page_icon="🥔", layout="centered")

# Get API base URL from environment variable or use default
POTATOBOT_API_URL = os.environ.get("POTATOBOT_API_URL", "http://localhost:8000")

print(f"API_URL: {POTATOBOT_API_URL}")

# CSS for styling
st.markdown(
    """
<style>
    /* Streamlit UI Elemente ausblenden */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.bot {
        background-color: #f0f2f6;
    }
    .chat-message .avatar {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .input-container {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding: 1rem 0;
        z-index: 100;
    }

    .logo{
        width: 200px;
        float: right;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Title and description
st.title("🥔 PotatoBot")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""Chat with the PotatoBot.""")

with col2:

    # logo
    st.html(f'<img class="logo" src="{POTATOBOT_API_URL}/static/potatobot.png"/>')


# Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(
                f"""
            <div class="chat-message user">
                <div>👤 <b>You:</b></div>
                <div>{message["content"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="chat-message bot">
                <div>🤖 <b>Bot:</b></div>
                <div>{message["content"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# Eingabefeld in einem Container
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input(
        "Your message:", key=f"user_input_{st.session_state.input_key}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

if user_input and user_input != st.session_state.last_input:
    # Nachricht zum Chat-Verlauf hinzufügen
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.last_input = user_input

    # API-Anfrage senden
    try:
        response = requests.post(
            POTATOBOT_API_URL + "/chat",
            json={
                "message": user_input,
                "chat_history": [msg["role"] + ": " + msg["content"] for msg in st.session_state.messages][0:-1],
                "session_id": st.session_state.session_id,
            },
        )
        print(response)
        print(response.json())
        response_data = response.json()

        # Bot-Antwort zum Chat-Verlauf hinzufügen
        st.session_state.messages.append(
            {"role": "bot", "content": response_data["response"]}
        )

        # Eingabefeld leeren durch Erhöhung des Keys
        st.session_state.input_key += 1
        st.rerun()

    except Exception as e:
        st.error(e)
