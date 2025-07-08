---
# Contract Guardian ⚖️

AI legal‑risk companion for Egyptian construction projects. It bundles a **Streamlit** chat UI, a **LangChain** agent that calls Gemini‑Flash through **OpenRouter**, and a persisted **Chroma** vector store of Egyptian Civil Code & sample contract clauses.
---

## 🚀 Quick start

```bash
# 1 – clone
 git clone https://github.com/Youssef-Malek2004/contract_guardian.git
 cd contract_guardian
F
# 2 – create .env (keep secrets outside images!) Make sure your .env looks like this
OPENAI_API_KEY=YOUR-OPENROUTER-API-KEY
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
TOKENIZERS_PARALLELISM=false

# 3 – build local image (≈2–4 min first time)
 docker build -t contract_guardian .

# 4 – run
 docker run -p 8501:8501 --env-file .env contract_guardian
```

Open [**http://localhost:8501**](http://localhost:8501) – ask questions like “CEO wants me to hide the delay…” The answer arrives in Markdown with cited clauses.
---

## 🚚 Just pull the prebuilt image

```bash
 docker pull youssefmalek/contract_guardian:latest
 docker run -p 8501:8501 --env-file .env youssefmalek/contract_guardian:latest
```

---

## 📁 Repository layout (concise)

| Path                     | Purpose                                                                  |
| ------------------------ | ------------------------------------------------------------------------ |
| `app.py`                 | Streamlit chat interface (Markdown answers + sources)                    |
| `agent.py`               | Builds LangChain _tool‑calling_ agent (`search_contracts` tool)          |
| `ingest.py`              | Loads `data/`, splits, embeds with **E5‑small‑v2**, writes **Chroma** DB |
| `chroma_db/`             | Persisted vector store (\~40 MB) baked into image                        |
| `data/`                  | Sample contract clause & Civil Code excerpts                             |
| `terminal_agent.py`      | CLI REPL alternative (logs to `agent.log`)                               |
| `.streamlit/config.toml` | Turns off file watcher noise from PyTorch                                |
| `Dockerfile`             | Multi‑stage build → final runtime image ≈ 350 MB                         |
| `.dockerignore`          | Excludes `.env`, caches, logs, test artifacts                            |

**Logs**: agent thought & tool output stream to `agent.log` (tail it with `tail -f agent.log`).

---

## 🛠 Tech stack & tools

- **Embeddings:** `intfloat/e5-small-v2` (fast, 120 MB)
- **LLM backend:** Gemini‑Flash via OpenRouter
- **RAG stack:** Chroma vector DB + LangChain `RetrieverTool`
- **Agent:** LangChain agent‑executor with single `search_contracts` tool
- **UI:** Streamlit (markdown output)
- **Container:** Python 3.12‑slim multi‑stage build; no secrets baked

---

## 💡 Customization

- Put additional contract PDFs/TXT in `data/`, rerun `python ingest.py`, rebuild image.
- Swap embedding model in `ingest.py` & `agent.py` if you need Arabic/Egyptian dialect recall.
- Mount `chroma_db` instead of baking it:
  ```bash
  docker run -p 8501:8501 -v $(pwd)/chroma_db:/app/chroma_db --env-file .env contract_guardian
  ```

---

Made with 🏗️ ⚖️ and ☕ by **Youssef Malek**.
