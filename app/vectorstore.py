from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    from langchain_community.embeddings import HuggingFaceEmbeddings


def build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_faiss_index(docs, index_path: Path) -> None:
    embeddings = build_embeddings()
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(str(index_path))


def load_faiss_index(index_path: Path) -> FAISS:
    embeddings = build_embeddings()
    return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
