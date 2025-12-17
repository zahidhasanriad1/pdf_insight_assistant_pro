from __future__ import annotations

from typing import Dict, Tuple

from langchain_community.chat_message_histories import ChatMessageHistory


_store: Dict[Tuple[str, str], ChatMessageHistory] = {}


def get_history(doc_id: str, session_id: str) -> ChatMessageHistory:
    key = (doc_id, session_id)
    if key not in _store:
        _store[key] = ChatMessageHistory()
    return _store[key]
