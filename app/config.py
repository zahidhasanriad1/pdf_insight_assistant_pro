from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        return int(raw)
    except ValueError as e:
        raise RuntimeError(f"Invalid int for {name}: {raw}") from e


def _must_get(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val


@dataclass(frozen=True)
class AppConfig:
    app_env: str = os.getenv("APP_ENV", "dev")
    data_dir: Path = Path(os.getenv("DATA_DIR", "data"))
    default_model: str = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    fallback_model: str = os.getenv("FALLBACK_MODEL", "llama-3.3-70b-versatile")
    max_upload_mb: int = _get_int("MAX_UPLOAD_MB", 25)

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"


def load_config() -> AppConfig:
    _must_get("GROQ_API_KEY")
    return AppConfig()
