########################
# 1️⃣  Build stage
########################
FROM python:3.12-slim AS builder

# Speed up, shrink wheels
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# --- install deps
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# --- copy source & build vector DB
COPY . .
RUN python ingest.py           

# Optional: keep ONLY the model weights, wipe HF metadata to save ~50 MB
RUN find /root/.cache/huggingface -type f -name "*.json" -delete

########################
# 2️⃣  Runtime stage
########################
FROM python:3.12-slim   

WORKDIR /app

# copy python site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copy *only* runtime artefacts (code + chroma_db + data)
COPY --from=builder /app/app.py             /app/app.py
COPY --from=builder /app/agent.py           /app/agent.py
COPY --from=builder /app/prompts.py         /app/prompts.py
COPY --from=builder /app/tools.py           /app/tools.py
COPY --from=builder /app/chroma_db          /app/chroma_db
COPY --from=builder /app/data               /app/data
COPY --from=builder /app/.streamlit         /app/.streamlit

# ─── Streamlit config
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "app.py"]
