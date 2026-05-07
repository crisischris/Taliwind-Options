from __future__ import annotations

import logging
import pickle
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).parent.parent / ".cache"


def _path(key: str) -> Path:
    return _CACHE_DIR / date.today().isoformat() / f"{key}.pkl"


def get(key: str) -> Any | None:
    p = _path(key)
    if not p.exists():
        return None
    try:
        with open(p, "rb") as f:
            logger.debug("Cache hit: %s", key)
            return pickle.load(f)
    except Exception as e:
        logger.warning("Cache read failed for %s: %s", key, e)
        return None


def set(key: str, value: Any) -> None:
    p = _path(key)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(p, "wb") as f:
            pickle.dump(value, f)
        logger.debug("Cached: %s", key)
    except Exception as e:
        logger.warning("Cache write failed for %s: %s", key, e)
