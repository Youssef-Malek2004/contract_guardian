---

# Contract Guardian ⚖️

AI legal‑risk companion for Egyptian construction projects. It bundles a **Streamlit** chat UI, a **LangChain** agent that calls Gemini‑Flash through **OpenRouter**, and a persisted **Chroma** vector store of Egyptian Civil Code & sample contract clauses.

---

## 🚀 Quick start

```bash
# 1 – clone
 git clone https://github.com/YOUR‑ORG/contract_guardian.git
 cd contract_guardian

# 2 – create .env (keep secrets outside images!) Create it with this format

OPENAI_API_KEY=OPENROUTER-API-KEY         # OpenRouter API Key as using Gemini (free version)
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
TOKENIZERS_PARALLELISM=false

# 3 – build local image (≈2–4 min first time)
 docker build -t contract_guardian .

# 4 – run
 docker run -p 8501:8501 --env-file .env contract_guardian
```

Open [**http://localhost:8501**](http://localhost:8501) – ask questions like “CEO wants me to hide the delay…” The answer arrives in Markdown with cited clauses.

## 🚚 Just pull the prebuilt image (Docker-Hub is currently failing with 500s, so if this doesn't work build the image yourself try it like above)

```bash
 docker pull youssefmalek/contract_guardian:latest
 docker run -p 8501:8501 --env-file .env youssefmalek/contract_guardian:latest
```

---

## 📁 Repository layout (concise)

| Path                     | Purpose                                                                  |
| ------------------------ | ------------------------------------------------------------------------ |
| `app.py`                 | Streamlit chat interface (Markdown answers + sources)                    |
| `agent.py`               | Builds LangChain *tool‑calling* agent (`search_contracts` tool)          |
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

* **Embeddings:** `intfloat/e5-small-v2` (fast, 120 MB)
* **LLM backend:** Gemini‑Flash via OpenRouter
* **RAG stack:** Chroma vector DB + LangChain `RetrieverTool`
* * **Agent:** LangChain agent‑executor with two tools
    • `search_contracts` → retrieves relevant contract clauses or Civil Code articles
    • `log_risk_event` → appends a Markdown summary of any high‑risk action to `risk_events.jsonl` for audit purposes
* **UI:** Streamlit (markdown output)
* **Container:** Python 3.12‑slim multi‑stage build; no secrets baked

---

\### 💡 Customization

* Put additional contract PDFs/TXT in `data/`, rerun `python ingest.py`, rebuild image.
* Swap embedding model in `ingest.py` & `agent.py` if you need Arabic/Egyptian dialect recall.
* Mount `chroma_db` instead of baking it:

  ```bash
  docker run -p 8501:8501 -v $(pwd)/chroma_db:/app/chroma_db --env-file .env contract_guardian
  ```

---

## 🧩 Key design choices & known limitations

| Aspect             | Decision                                          | Limitation                                                    |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------------- |
| **Embedding size** | `intfloat/e5‑small‑v2` to stay Docker‑friendly    | Not bilingual; misses purely Arabic clauses                   |
| **Vector store**   | Local Chroma persisted at build                   | Image rebuild required after ingest unless you mount a volume |
| **LLM provider**   | Gemini‑Flash via OpenRouter (free tier)           | 30‑60 sec hard rate‑limit; API subject to fair‑use outages    |
| **Risk logging**   | File‑based `risk_events.jsonl` tool (zero config) | No real‑time email/Slack push until SMTP/webhook configured   |
| **UI**             | Streamlit for one‑file deploy                     | Not mobile‑optimised; single‑user session                     |

---

## 🔗 Replicate locally and extend

1. Clone and run exactly as in **Quick start**.
2. Add PDFs or TXT in `data/` before running if you want extra documents.
3. To switch LLM change `OPENAI_API_BASE` and `OPENAI_API_KEY` in `.env` then rebuild.

---

### 🛠 Tools summary

| Tool                           | Purpose                                                          | Config needed                            |
| ------------------------------ | ---------------------------------------------------------------- | ---------------------------------------- |
| `search_contracts`             | Retrieves up to four contract or Civil Code excerpts from Chroma | none                                     |
| `log_risk_event`               | Appends high‑risk actions to `risk_events.jsonl` for audit       | none                                     |

---

## 🚀 Possible extensions

| Idea                                                 | Value                                                          | Effort                                              |
| ---------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------- |
| **Kafka listener** for project email or Slack events | Flags risky instructions in real time without manual chat      | Medium – add simple Kafka consumer & parse envelope |
| **Automatic email follow‑up** to project officials   | Sends the logged risk summary to PM, Contracts Engineer, Legal | Low – reuse `send_risk_alert` SMTP tool             |
| **Schedule-aware risk scoring**                      | Boost risk if action violates nearing contractual deadline     | Medium – needs project calendar feed                |
| External **PostgreSQL audit DB**                     | Persistent, queryable history across projects                  | Medium – SQLAlchemy layer, change log tool          |

---

Made with 🏗️ ⚖️ and ☕ by **Youssef Malek**.
