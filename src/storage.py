import json
import os
import sys
import time
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HISTORY_FILE = os.path.join(BASE_DIR, "clipboard_history.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "window_hotkey": "ctrl+shift+v",
    "window_geometry": "600x400+200+100",
    "theme": "dark",
    "max_history": 500,
    "paste_mode": "type",
}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(items):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

def add_item(text):
    items = load_history()
    if not text.strip():
        return items
    if items and items[0]["value"] == text:
        return items
    items.insert(0, {
        "value": text,
        "pinned": False,
        "timestamp": time.time(),
        "date": datetime.now().isoformat(),
    })
    if len(items) > 500:
        items = items[:500]
    save_history(items)
    return items

def remove_item(index):
    items = load_history()
    if 0 <= index < len(items):
        if not items[index]["pinned"]:
            items.pop(index)
            save_history(items)
    return items

def toggle_pin(index):
    items = load_history()
    if 0 <= index < len(items):
        items[index]["pinned"] = not items[index]["pinned"]
        save_history(items)
    return items

def clear_unpinned():
    items = load_history()
    items = [i for i in items if i.get("pinned", False)]
    save_history(items)
    return items

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k in DEFAULT_SETTINGS:
                    data.setdefault(k, DEFAULT_SETTINGS[k])
                if data.get("window_geometry", "").startswith("800x600"):
                    data["window_geometry"] = "600x400+200+100"
                    save_settings(data)
                return data
        except Exception:
            return dict(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
