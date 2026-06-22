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
    if kind == "tweak":
        record_applied_tweaks(items, data)
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_applied_tweaks(items: list[dict], data: dict | None = None) -> None:
    """Remember every tweak applied on this PC (survives app restarts)."""
    if not items:
        return
    store = data if data is not None else _load_all()
    hist = {entry["id"]: entry for entry in store.get("tweak_history", []) if entry.get("id")}
    now = datetime.now().isoformat(timespec="seconds")
    for item in items:
        tid = item.get("id")
        if not tid:
            continue
        hist[tid] = {
            "id": tid,
            "name": item.get("name", tid),
            "last_applied": now,
        }
    store["tweak_history"] = list(hist.values())
    if data is None:
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        SESSION_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def ensure_history_migrated() -> None:
    """Import last tweak batch into history for users who tweaked before v1.0.7."""
    data = _load_all()
    if data.get("tweak_history"):
        return
    last = data.get("tweak")
    if last and last.get("items"):
        record_applied_tweaks(last["items"], data)
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_applied_tweak_history() -> list[dict]:
    ensure_history_migrated()
    return list(_load_all().get("tweak_history", []))


def has_applied_tweak_history() -> bool:
    return bool(get_applied_tweak_history())


def clear_tweak_history() -> None:
    data = _load_all()
    if "tweak_history" in data:
        del data["tweak_history"]
        if data:
            SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        elif SESSION_PATH.exists():
            SESSION_PATH.unlink(missing_ok=True)


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