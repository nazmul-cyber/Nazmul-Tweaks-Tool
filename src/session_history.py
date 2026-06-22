"""Track last applied tweaks / installed apps for revert."""

import json
from datetime import datetime
from pathlib import Path

SESSION_PATH = Path.home() / ".nazmul-tweaks-tool" / "last_sessions.json"


def _load_all() -> dict:
    if not SESSION_PATH.exists():
        return {}
    try:
        data = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_last_session(kind: str, items: list[dict]) -> None:
    if not items or kind not in ("tweak", "app"):
        return
    data = _load_all()
    data[kind] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "items": items,
    }
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_last_session(kind: str) -> dict | None:
    entry = _load_all().get(kind)
    if not entry or not entry.get("items"):
        return None
    return entry


def clear_last_session(kind: str) -> None:
    data = _load_all()
    if kind in data:
        del data[kind]
        if data:
            SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        elif SESSION_PATH.exists():
            SESSION_PATH.unlink(missing_ok=True)


def has_last_session(kind: str) -> bool:
    return get_last_session(kind) is not None