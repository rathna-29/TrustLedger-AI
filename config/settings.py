"""Environment-driven configuration for TrustLedger-AI.

Loads settings from the process environment with sensible defaults, so the
same codebase runs identically in dev, CI and production. Never hardcode
secrets here -- read them from the environment or a .env file (see
.env.example at the repo root).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = os.environ.get("TRUSTLEDGER_DB", str(BASE_DIR / "app.db"))


class Settings:
    """Bag of resolved runtime settings."""

    def __init__(self) -> None:
        self.flask_port = int(os.environ.get("FLASK_PORT", "5000"))
        self.flask_debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
        self.db_path = DB_FILE
        self.jwt_secret = os.environ.get(
            "JWT_SECRET", "trustledger-demo-secret-change-me"
        )
        self.llm_api_key = os.environ.get("LLM_API_KEY", "")
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")


settings = Settings()
