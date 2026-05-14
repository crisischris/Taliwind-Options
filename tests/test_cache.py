from __future__ import annotations

import pickle
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import indicators.cache as cache_mod
from indicators import cache


# ── helpers ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def tmp_cache(tmp_path, monkeypatch):
    """Redirect all cache I/O to a temp directory."""
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp_path)
    return tmp_path


# ── _path ────────────────────────────────────────────────────────────────────

def test_path_uses_today_and_key(tmp_path):
    p = cache_mod._path("my_key")
    assert p == tmp_path / date.today().isoformat() / "my_key.pkl"


# ── get ──────────────────────────────────────────────────────────────────────

def test_get_miss_returns_none():
    assert cache.get("nonexistent") is None


def test_get_hit_returns_value(tmp_path):
    p = cache_mod._path("test_key")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(pickle.dumps({"hello": "world"}))
    assert cache.get("test_key") == {"hello": "world"}


def test_get_corrupt_file_returns_none(tmp_path):
    p = cache_mod._path("bad_key")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"not valid pickle")
    result = cache.get("bad_key")
    assert result is None


def test_get_various_types(tmp_path):
    for val in [42, [1, 2, 3], "string", None]:
        cache.set(f"key_{id(val)}", val)
        assert cache.get(f"key_{id(val)}") == val


# ── set ──────────────────────────────────────────────────────────────────────

def test_set_creates_file():
    cache.set("new_key", 123)
    p = cache_mod._path("new_key")
    assert p.exists()
    assert pickle.loads(p.read_bytes()) == 123


def test_set_write_error_is_swallowed(tmp_path, monkeypatch):
    def bad_open(*a, **kw):
        raise OSError("disk full")
    monkeypatch.setattr("builtins.open", bad_open)
    cache.set("fail_key", "value")  # should not raise


def test_set_overwrites_existing():
    cache.set("ow_key", "first")
    cache.set("ow_key", "second")
    assert cache.get("ow_key") == "second"


# ── lambda cache dir ─────────────────────────────────────────────────────────

def test_lambda_env_uses_tmp(monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "my-fn")
    import importlib
    reloaded = importlib.reload(cache_mod)
    assert str(reloaded._CACHE_DIR) == "/tmp/.cache"
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    importlib.reload(cache_mod)


def test_local_env_uses_project_root(monkeypatch):
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    import importlib
    reloaded = importlib.reload(cache_mod)
    assert ".cache" in str(reloaded._CACHE_DIR)
    assert "/tmp" not in str(reloaded._CACHE_DIR)
