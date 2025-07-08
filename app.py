import os, textwrap, logging
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory

from agent import build_agent

st.set_page_config(page_title="Contract Guardian", page_icon="⚖️")

# ─── Env & logging ────────────────────────────────────────────────────
load_dotenv()
LOG_PATH = Path(__file__).parent / "agent.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logging.info("Streamlit session started.")

# ─── Vector store & agent init (run once per session) ─────────────────
@st.cache_resource(show_spinner="Loading embeddings & agent…")
def init_agent():
    CHROMA_DIR = Path(__file__).parent / "chroma_db"

    emb = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")
    # emb = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")
    
    db  = Chroma(embedding_function=emb, persist_directory=str(CHROMA_DIR))

    _store = {}  # -> {session_id: ChatMessageHistory}

    def get_session_history(sid: str):
        return _store.setdefault(sid, ChatMessageHistory())

    agent = build_agent(db.as_retriever(), get_session_history)
    return agent

chat_agent = init_agent()

# ─── Streamlit UI ------------------------------------------------------
st.title("Contract Guardian")
st.markdown(
    "Ask anything about your **construction contract** or **Egyptian Civil Code**. "
    "The agent will cite relevant clauses."
)

# Keep chat history in Streamlit session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role, content = msg
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(content)  # already Markdown

# Input box
user_input = st.chat_input("Type your question…")

if user_input:
    # Log user input immediately
    logging.info("USER: %s", user_input)

    # Append user message to session history
    st.session_state.messages.append(("user", user_input))
    st.markdown(f"**You:** {user_input}")

    # Call agent
    result = chat_agent.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": "streamlit"}},
    )

    answer = result["output"].strip()
    steps  = result.get("intermediate_steps", [])

    # Log final answer
    logging.info("ANSWER: %s", answer)

    # Collect tool calls + log them
    citations = []
    for action, output in steps:
        logging.info("TOOL_CALL: %s", action.tool)
        logging.info("TOOL_INPUT: %s", action.tool_input)
        logging.info("TOOL_OUTPUT: %.200s", output.replace("\n", " "))
        if action.tool == "search_contracts" and output != "NO_MATCH":
            citations.extend(output.split("\n---\n"))

    # Build Markdown answer + sources
    md_answer = answer
    if citations:
        md_answer += "\n\n#### 🔎 Sources\n"
        for snip in citations:
            short = textwrap.shorten(snip, 160, placeholder="…")
            md_answer += f"* {short}\n"

    # Show answer & save to chat history
    st.markdown(md_answer)
    st.session_state.messages.append(("assistant", md_answer))

else:
    logging.info("USER: [empty input submitted]")
