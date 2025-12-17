from __future__ import annotations
from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    status: str
    doc_id: str
    filename: str
    chunks: int

class AskRequest(BaseModel):
    doc_id: str
    session_id: str = "default"
    question: str
    top_k: int = 5
    language: str = Field("bn", description="bn or en")

class AskResponse(BaseModel):
    answer: str
    sources: list
