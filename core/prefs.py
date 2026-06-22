"""
core/prefs.py
=============
Leitura e gravação de user_prefs.json (email lembrado, tema, etc.).
Módulo sem dependências de UI — pode ser importado por qualquer camada.
"""

import json
from pathlib import Path

_FILE = Path(__file__).parent.parent / "user_prefs.json"


def load() -> dict:
    try:
        if _FILE.exists():
            return json.loads(_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save(data: dict):
    try:
        _FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def get_pref(key: str, default=None):
    return load().get(key, default)


def set_pref(key: str, value):
    data = load()
    data[key] = value
    save(data)


def delete_pref(key: str):
    data = load()
    data.pop(key, None)
    save(data)
