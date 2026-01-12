import time
from typing import Dict, Any, Optional


class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any):
        self._cache[key] = {"value": value, "expiry": time.time() + self.ttl}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None

        item = self._cache[key]
        if time.time() > item["expiry"]:
            del self._cache[key]
            return None

        return item["value"]

    def clear(self):
        self._cache.clear()
