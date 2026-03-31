import json
import os
import time
import uuid
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEBUG_LOG_PATH = "/Users/parthshende/Desktop/indian trader/.cursor/debug-f2e783.log"
_DEBUG_SESSION_ID = "f2e783"


def _debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": _DEBUG_SESSION_ID,
        "runId": "pre-fix",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
        "id": f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
    }
    try:
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, default=str) + "\n")
    except Exception:
        pass


class RenderApiSettings(BaseSettings):
    APP_NAME: str = "Indian Trader Signal Ingest API"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    SIGNAL_API_KEY: str = ""
    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "indian_trader"
    MONGODB_SIGNALS_COLLECTION: str = "signals"

    ALLOWED_ORIGINS: str = Field(default="*")
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> List[str]:
        raw = (self.ALLOWED_ORIGINS or "").strip()
        # region agent log
        _debug_log(
            "H3",
            "settings.py:allowed_origins",
            "parse_allowed_origins_raw",
            {"raw_value": raw[:200]},
        )
        # endregion
        if not raw:
            return ["*"]
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass
        return [item.strip() for item in raw.split(",") if item.strip()]


# region agent log
_debug_log(
    "H1",
    "settings.py:module_load",
    "raw_allowed_origins_env",
    {"is_set": "ALLOWED_ORIGINS" in os.environ, "raw_value": os.getenv("ALLOWED_ORIGINS", "<unset>")[:200]},
)
# endregion

try:
    # region agent log
    _debug_log("H4", "settings.py:settings_init", "settings_init_start", {})
    # endregion
    settings = RenderApiSettings()
    # region agent log
    _debug_log("H4", "settings.py:settings_init", "settings_init_success", {"allowed_origins": settings.allowed_origins})
    # endregion
except Exception as exc:
    # region agent log
    _debug_log(
        "H2",
        "settings.py:settings_init",
        "settings_init_error",
        {"error_type": type(exc).__name__, "error_message": str(exc)[:400]},
    )
    # endregion
    raise
