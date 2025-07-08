from pathlib import Path
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
