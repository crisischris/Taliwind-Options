import importlib

import tailwind_options.config as config_mod
from tailwind_options.config import Config, ScannerOpts


def test_defaults():
    c = Config()
    assert c.gainer_min_gain_pct == 500.0
    assert c.gainer_cache_floor_pct == 100.0
    assert c.gainer_put.max_cost_pct == 0.05
    assert c.gainer_put.max_iv == 2.00
    assert c.gainer_put.min_oi == 10
    assert c.gainer_put.min_dte == 60
    assert c.gainer_put.max_dte == 1000


def test_scanner_opts_is_frozen_dataclass():
    c = Config()
    assert isinstance(c.gainer_put, ScannerOpts)
    assert isinstance(c.trend_call, ScannerOpts)
    assert isinstance(c.broken_mom, ScannerOpts)
    assert isinstance(c.val_gravity, ScannerOpts)
    assert isinstance(c.breakout, ScannerOpts)
    assert isinstance(c.squeeze, ScannerOpts)
    assert isinstance(c.rotation, ScannerOpts)
    assert isinstance(c.dram, ScannerOpts)
    assert isinstance(c.space, ScannerOpts)


def test_env_override_min_gain(monkeypatch):
    monkeypatch.setenv("GAINER_MIN_GAIN_PCT", "300")
    reloaded = importlib.reload(config_mod)
    assert reloaded.Config().gainer_min_gain_pct == 300.0


def test_env_override_scanner_opts(monkeypatch):
    monkeypatch.setenv("GAINER_MIN_GAIN_PCT", "200")
    monkeypatch.setenv("GAINER_CACHE_FLOOR_PCT", "50")
    monkeypatch.setenv("GAINER_PUT_MAX_COST_PCT", "0.10")
    monkeypatch.setenv("GAINER_PUT_MAX_IV", "1.50")
    monkeypatch.setenv("GAINER_PUT_MIN_OI", "5")
    monkeypatch.setenv("GAINER_PUT_MIN_DTE", "30")
    monkeypatch.setenv("GAINER_PUT_MAX_DTE", "500")
    reloaded = importlib.reload(config_mod)
    c = reloaded.Config()
    assert c.gainer_min_gain_pct == 200.0
    assert c.gainer_cache_floor_pct == 50.0
    assert c.gainer_put.max_cost_pct == 0.10
    assert c.gainer_put.max_iv == 1.50
    assert c.gainer_put.min_oi == 5
    assert c.gainer_put.min_dte == 30
    assert c.gainer_put.max_dte == 500


def test_types():
    c = Config()
    assert isinstance(c.gainer_min_gain_pct, float)
    assert isinstance(c.gainer_put.min_oi, int)
    assert isinstance(c.gainer_put.min_dte, int)
    assert isinstance(c.gainer_put.max_cost_pct, float)
