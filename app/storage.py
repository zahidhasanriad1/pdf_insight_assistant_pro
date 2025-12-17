from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any

from app.utils import ensure_dir


def write_manifest(index_dir: Path, manifest: Dict[str, Any]) -> None:
    ensure_dir(index_dir)
    path = index_dir / "manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def read_manifest(index_dir: Path) -> Dict[str, Any]:
    path = index_dir / "manifest.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
