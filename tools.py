from pathlib import Path
import json, datetime
from langchain.tools import Tool

def get_contract_information_tool(retriever):
    """
    Returns a LangChain Tool named 'search_contracts' that the LLM can call.
    """

    def _search(query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return "NO_MATCH"
        snippets = []
        for d in docs[:4]:
            fname   = Path(d.metadata.get("source", "doc")).name
            snippet = d.page_content.replace("\n", " ")
            snippets.append(f"**{fname}** :: {snippet}")
        return "\n---\n".join(snippets)

    return Tool(
        name="search_contracts",
        func=_search,
        description=(
            "Look up Egyptian-law or contract clauses relevant to a query. "
            "Returns up to 4 excerpts."
        ),
    )

LOG_FILE = Path("risk_events.jsonl")

def _log_risk(event: str, detail_md: str):
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "event": event,
        "detail_md": detail_md,
    }
    LOG_FILE.write_text(
        (LOG_FILE.read_text() if LOG_FILE.exists() else "") +
        json.dumps(entry, ensure_ascii=False) + "\n"
    )

# tools.py
def get_risk_log_tool():
    def log_and_echo(md: str) -> str:
        _log_risk("HIGH_RISK", md)
        return md                    
    return Tool(
        name="log_risk_event",
        func=log_and_echo,
        description=(
            "Call when the action is HIGH RISK. "
            "Pass a concise Markdown summary that cites clauses. "
            "The tool records the event and returns the same summary."
        ),
    )

