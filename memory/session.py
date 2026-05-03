import time
import threading
from typing import Optional


class SessionStore:
    def __init__(self, max_history: int = 10, ttl: int = 3600):
        self._store: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._max_history = max_history
        self._ttl = ttl

    def _get_or_create(self, session_id: str) -> dict:
        with self._lock:
            if session_id not in self._store:
                self._store[session_id] = {
                    "history": [],
                    "profile": None,
                    "last_access": time.time(),
                }
            session = self._store[session_id]
            session["last_access"] = time.time()
            return session

    def add_exchange(self, session_id: str, user_msg: str, assistant_msg: str):
        session = self._get_or_create(session_id)
        session["history"].append({
            "user": user_msg,
            "assistant": assistant_msg,
            "timestamp": time.time(),
        })
        if len(session["history"]) > self._max_history:
            session["history"] = session["history"][-self._max_history:]

    def get_history(self, session_id: str, last_n: int = 3) -> list[dict]:
        session = self._get_or_create(session_id)
        return session["history"][-last_n:]

    def set_profile(self, session_id: str, profile_data: dict):
        session = self._get_or_create(session_id)
        session["profile"] = profile_data

    def get_profile(self, session_id: str) -> Optional[dict]:
        session = self._get_or_create(session_id)
        return session["profile"]

    def cleanup_expired(self):
        now = time.time()
        with self._lock:
            expired = [
                sid for sid, s in self._store.items()
                if now - s["last_access"] > self._ttl
            ]
            for sid in expired:
                del self._store[sid]


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
