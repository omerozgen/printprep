"""Tiny i18n helper for the PrintPrep CLI.

Strings live in `printprep/locales/<code>.json`. The active language is
resolved once at import-time (so that Click `help=` decorators see the
right text):

1. `PRINTPREP_LANG` environment variable (e.g. `en`, `tr`, `zh`).
2. `locale.getlocale()` — first two chars (`tr_TR.UTF-8` → `tr`).
3. Fall back to `en`.

Missing keys fall back to English so half-translated locales still work.
"""

from __future__ import annotations

import json
import locale
import os
from pathlib import Path
from typing import Any, Dict

SUPPORTED = (
    "en", "tr", "zh", "es", "fr", "de", "ru", "ja", "ko",
    "pt", "ar", "hi", "bn", "pa", "jv",
)

_LOCALES_DIR = Path(__file__).parent / "locales"
_dict: Dict[str, str] = {}
_fallback: Dict[str, str] = {}
_current = "en"


def _detect() -> str:
    env = os.environ.get("PRINTPREP_LANG", "").strip().lower()
    if env in SUPPORTED:
        return env
    try:
        sys_locale = locale.getlocale()[0] or ""
    except Exception:
        sys_locale = ""
    base = sys_locale.split("_")[0].lower() if sys_locale else ""
    if base in SUPPORTED:
        return base
    return "en"


def _load(code: str) -> Dict[str, str]:
    p = _LOCALES_DIR / f"{code}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def t(key: str, **params: Any) -> str:
    """Translate `key` and interpolate `{name}` placeholders from kwargs.

    Falls back to English, then to the literal key, if nothing matches.
    """
    s = _dict.get(key) or _fallback.get(key) or key
    if not params:
        return s
    try:
        return s.format(**params)
    except (KeyError, IndexError, ValueError):
        return s


def current() -> str:
    return _current


def set_language(code: str) -> None:
    """Override the active language. Mostly useful for tests."""
    global _dict, _current
    if code not in SUPPORTED:
        code = "en"
    _dict = _load(code) or _load("en")
    _current = code


_fallback = _load("en")
set_language(_detect())
