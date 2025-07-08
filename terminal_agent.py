import logging, textwrap
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory

from agent import build_agent

# ---- init ------------------------------------------------------------
load_dotenv()
BASE_DIR   = Path(__file__).parent
CHROMA_DIR = BASE_DIR / "chroma_db"

# === Logging setup ===
LOG_PATH = BASE_DIR / "agent.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logging.info("🔄 Session started.")

emb = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")
# emb = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")

db  = Chroma(embedding_function=emb, persist_directory=str(CHROMA_DIR))
retriever = db.as_retriever()

# Simple in-memory store
_store = {}
def get_session_history(sid): return _store.setdefault(sid, ChatMessageHistory())

chat_agent = build_agent(retriever, get_session_history)

# ---- REPL ------------------------------------------------------------
print("\n🧑‍⚖️ Contract Guardian – ask me (type 'exit' to quit)\n")

try:
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        result = chat_agent.invoke(
            {"input": q},
            config={"configurable": {"session_id": "demo"}},
        )
        answer = result["output"].strip()
        steps  = result["intermediate_steps"]

        print("\n" + answer + "\n")

        # Log user + final answer
        logging.info("USER: %s", q)
        logging.info("ANSWER: %s", answer)

        # Extract citations + log tool calls
        cites = []
        for action, output in steps:
            logging.info("TOOL_CALL: %s", action.tool)
            logging.info("TOOL_INPUT: %s", action.tool_input)
            logging.info("TOOL_OUTPUT: %.200s", output.replace("\n", " "))
            if action.tool == "search_contracts" and output != "NO_MATCH":
                snippets = output.split("\n---\n")
                cites.extend(snippets)

        if cites:
            print("#### 🔎 Sources")
            for line in cites:
                short = textwrap.shorten(line, 160, placeholder="…")
                print(f"* {short}")
            print()

except KeyboardInterrupt:
    print("\n👋 Exiting.")
finally:
    logging.info("🔚 Session ended.")
