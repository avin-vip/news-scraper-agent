import json
import os

STATE_FILE = "state.json"
MAX_SEEN_IDS = 10_000


def _load() -> set:
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, IOError):
        return set()


def _flush(seen: set) -> None:
    ids = list(seen)
    if len(ids) > MAX_SEEN_IDS:
        ids = ids[-MAX_SEEN_IDS:]
    with open(STATE_FILE, "w") as f:
        json.dump(ids, f)


_seen_ids: set = _load()


def is_seen(news_id: str) -> bool:
    return str(news_id) in _seen_ids


def mark_seen(news_id: str) -> None:
    _seen_ids.add(str(news_id))
    _flush(_seen_ids)
