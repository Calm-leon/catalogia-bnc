from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from threading import Lock


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


_events: dict[str, deque[datetime]] = defaultdict(deque)
_lock = Lock()


def rate_limit_enabled() -> bool:
    return os.getenv("RATE_LIMIT_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def limit_for_endpoint(endpoint_key: str) -> int:
    if endpoint_key == "pipeline_image":
        return int(os.getenv("RATE_LIMIT_PIPELINE_IMAGE_PER_MINUTE", "5"))
    if endpoint_key == "logs":
        return int(os.getenv("RATE_LIMIT_LOGS_PER_MINUTE", "60"))
    return int(os.getenv("RATE_LIMIT_DEFAULT_PER_MINUTE", "120"))


def window_seconds() -> int:
    return int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


def check_rate_limit(client_key: str, endpoint_key: str) -> RateLimitDecision:
    if not rate_limit_enabled():
        return RateLimitDecision(allowed=True, retry_after_seconds=0)

    limit = max(1, limit_for_endpoint(endpoint_key))
    window = max(1, window_seconds())
    now = datetime.now(timezone.utc)
    floor = now - timedelta(seconds=window)
    bucket_key = f"{endpoint_key}:{client_key}"

    with _lock:
        queue = _events[bucket_key]
        while queue and queue[0] < floor:
            queue.popleft()

        if len(queue) >= limit:
            retry_after = int((queue[0] - floor).total_seconds()) + 1
            return RateLimitDecision(allowed=False, retry_after_seconds=max(1, retry_after))

        queue.append(now)
        return RateLimitDecision(allowed=True, retry_after_seconds=0)


def reset_rate_limit_state() -> None:
    with _lock:
        _events.clear()
