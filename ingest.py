"""
Ingest all text/PDF files in ./data,
embed with intfloat/e5-small-v2,
and persist to ./chroma_db for later retrieval.

Run once:
  python ingest.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ──────────────────────────────── Paths ────────────────────────────────
load_dotenv()
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# ──────────────────────────────── 1️⃣ Load ─────────────────────────────
docs = []
if not DATA_DIR.exists():
    raise SystemExit(f"⚠  No ./data folder found at {DATA_DIR}.")

for fp in DATA_DIR.rglob("*"):
    if fp.is_file():
        if fp.suffix.lower() in {".txt", ".md"}:
            docs.extend(TextLoader(str(fp)).load())
        elif fp.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(fp)).load())

if not docs:
    raise SystemExit(f"⚠  No text or PDF files found in {DATA_DIR} – add contract/law files first.")

print(f"📄  Loaded {len(docs)} raw documents.")

# ──────────────────────────────── 2️⃣ Split ─────────────────────────────
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
splits   = splitter.split_documents(docs)

print(f"✂️  Split into {len(splits)} chunks.")

# ──────────────────────────────── 3️⃣ Embed & store ──────────────────────
emb = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")

CHROMA_DIR.mkdir(exist_ok=True)

vectordb = Chroma.from_documents(
    documents=splits,
    embedding=emb,
    persist_directory=str(CHROMA_DIR)
)

print(f"✅  Ingest complete – {len(splits):,} chunks saved to {CHROMA_DIR}/")
