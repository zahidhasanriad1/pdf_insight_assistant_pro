from __future__ import annotations

from pathlib import Path
import re
import uuid


def new_doc_id() -> str:
    return uuid.uuid4().hex


def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9._()\s]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:180] if len(name) > 180 else name


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
