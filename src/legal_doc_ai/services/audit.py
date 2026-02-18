from collections import deque
from datetime import datetime, timezone
from threading import Lock


class AuditService:
    """In-memory audit trail for API actions (ring buffer)."""

    def __init__(self, max_items: int = 500) -> None:
        self._events: deque[dict] = deque(maxlen=max_items)
        self._lock = Lock()

    def log(self, action: str, status: str, metadata: dict | None = None) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "status": status,
            "metadata": metadata or {},
        }
        with self._lock:
            self._events.appendleft(event)

    def list_events(self, limit: int = 50) -> list[dict]:
        lim = max(1, min(limit, 200))
        with self._lock:
            return list(self._events)[:lim]
