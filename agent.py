from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

from prompts import qa_prompt
from tools import get_contract_information_tool, get_risk_log_tool
import os

# ---- Config via env or pass params -----------------------------------
load_dotenv()

LLM_MODEL  = "google/gemini-2.0-flash-001"
API_KEY    = os.getenv("OPENROUTER_API_KEY")
API_BASE   = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
TEMPERATURE = 0.2

# ----------------------------------------------------------------------
def build_agent(retriever, get_session_history):
    """
    Returns:
        memory (RunnableWithMessageHistory) – main chat interface
    """
    tool_fn = get_contract_information_tool(retriever)
    tools   = [tool_fn, get_risk_log_tool()]

    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=API_KEY,
        base_url=API_BASE,
        temperature=TEMPERATURE,
    )

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=qa_prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
    )

    memory = RunnableWithMessageHistory(
        executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return memory
