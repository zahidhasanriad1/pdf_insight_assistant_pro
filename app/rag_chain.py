from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

from app.prompts import get_prompt
from app.memory import get_history


@dataclass(frozen=True)
class RAGSettings:
    model: str
    fallback_model: str
    prompt_version: str = "v1"
    temperature: float = 0.2


def _history_factory(doc_id: str, session_id: str):
    return get_history(doc_id, session_id)


def build_rag_chain(settings: RAGSettings):
    prompt = get_prompt(settings.prompt_version)
    parser = StrOutputParser()

    def _make_llm(model_name: str):
        return ChatGroq(model=model_name, temperature=settings.temperature)

    llm = None
    try:
        llm = _make_llm(settings.model)
    except Exception:
        llm = _make_llm(settings.fallback_model)

    base = prompt | llm | parser

    chain = RunnableWithMessageHistory(
        base,
        lambda session_id: _history_factory(session_id.split("::")[0], session_id.split("::")[1]),
        input_messages_key="question",
        history_messages_key="history",
    )
    return chain


def format_context(docs) -> str:
    blocks = []
    for i, d in enumerate(docs):
        page = d.metadata.get("page", None)
        src = d.metadata.get("source", "")
        tag = f"chunk={i} source={src} page={page}"
        blocks.append(f"<<{tag}>>\n{d.page_content}")
    return "\n\n".join(blocks)


def docs_to_sources(docs, max_chars: int = 220):
    sources = []
    for d in docs:
        page = d.metadata.get("page", None)
        snippet = (d.page_content or "").strip().replace("\n", " ")
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."
        sources.append(
            {
                "page": page,
                "source": d.metadata.get("source", None),
                "snippet": snippet,
            }
        )
    return sources
