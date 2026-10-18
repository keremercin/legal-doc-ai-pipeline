from typing import Any

APP_VERSION = "0.5.0"


def api_response(*, data: Any = None, status: str = "ok", error: Any = None, latency_ms: int | None = None) -> dict:
    return {
        "status": status,
        "data": data if data is not None else {},
        "meta": {"app_version": APP_VERSION, "latency_ms": latency_ms},
        "error": error,
    }
