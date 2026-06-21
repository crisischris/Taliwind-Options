from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from lambda_handler import _InvocationLogger, handler
from tailwind_options.report import _write_manifest_to_s3, write_theme_report_to_s3
from tests.conftest import make_call_signal, make_signal

# alias for tests that use the old private name
_write_theme_report_to_s3 = lambda signals, s3, bucket, ts, page, theme, log=None: \
    write_theme_report_to_s3(signals, s3, bucket, ts, page, theme)


class _NoSuchKey(Exception):
    pass


def _make_s3(responses: dict | None = None):
    """Build a mock S3 client. responses maps Key → list (manifest content)."""
    mock_s3 = MagicMock()
    mock_s3.exceptions.NoSuchKey = _NoSuchKey
    responses = responses or {}

    def get_object(Bucket, Key):
        if Key in responses:
            return {"Body": MagicMock(read=lambda: json.dumps(responses[Key]).encode())}
        raise _NoSuchKey("no such key")

    mock_s3.get_object.side_effect = get_object
    return mock_s3


@contextmanager
def _patch_all_scanners(
    gainer=None,
    broken=None,
    valuation=None,
    ai=None,
    breakout=None,
    squeeze=None,
    rotation=None,
    dram=None,
    space=None,
):
    """Patch all 9 scanner classes to return the given signal lists."""
    with patch("tailwind_options.sources.gainer_puts.GainerPutScanner") as MockGainer, \
         patch("tailwind_options.sources.broken_momentum.BrokenMomentumScanner") as MockBroken, \
         patch("tailwind_options.sources.valuation_gravity.ValuationGravityScanner") as MockValuation, \
         patch("tailwind_options.sources.trend_calls.TrendCallScanner") as MockTrend, \
         patch("tailwind_options.sources.breakout_calls.BreakoutCallScanner") as MockBreakout, \
         patch("tailwind_options.sources.short_squeeze_calls.ShortSqueezeCallScanner") as MockSqueeze, \
         patch("tailwind_options.sources.sector_rotation_calls.SectorRotationCallScanner") as MockRotation, \
         patch("tailwind_options.sources.dram_memory_calls.DramMemoryCallScanner") as MockDram, \
         patch("tailwind_options.sources.space_calls.SpaceCallScanner") as MockSpace, \
         patch("tailwind_options.call_universe.get_tickers", return_value=[]):
        MockGainer.return_value.check.return_value = gainer or []
        MockBroken.return_value.check.return_value = broken or []
        MockValuation.return_value.check.return_value = valuation or []
        MockTrend.return_value.check.return_value = ai or []
        MockBreakout.return_value.check.return_value = breakout or []
        MockSqueeze.return_value.check.return_value = squeeze or []
        MockRotation.return_value.check.return_value = rotation or []
        MockDram.return_value.check.return_value = dram or []
        MockSpace.return_value.check.return_value = space or []
        yield


# ── _InvocationLogger ─────────────────────────────────────────────────────────

def test_invocation_logger_prefixes_message():
    base_logger = logging.getLogger("test")
    adapter = _InvocationLogger(base_logger, {"inv_id": "abc-123"})
    msg, kwargs = adapter.process("hello world", {})
    assert msg == "[abc-123] hello world"
    assert kwargs == {}


def test_invocation_logger_preserves_kwargs():
    base_logger = logging.getLogger("test")
    adapter = _InvocationLogger(base_logger, {"inv_id": "xyz"})
    msg, kwargs = adapter.process("msg", {"extra": "data"})
    assert "[xyz]" in msg
    assert kwargs == {"extra": "data"}


# ── handler ───────────────────────────────────────────────────────────────────

def _make_context(request_id="test-req-001"):
    ctx = MagicMock()
    ctx.aws_request_id = request_id
    return ctx


def test_handler_no_signals():
    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client"):
            with _patch_all_scanners():
                result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert result["body"] == "no signals"


def test_handler_with_put_signals():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with _patch_all_scanners(gainer=signals):
                result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert "mean-reversion puts" in result["body"]


def test_handler_with_call_signals():
    signals = [make_call_signal("TSLA", term="short")]
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with _patch_all_scanners(ai=signals):
                result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert "ai-momentum calls" in result["body"]


def test_handler_returns_500_on_exception():
    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client"):
            with patch(
                "tailwind_options.sources.gainer_puts.GainerPutScanner",
                side_effect=RuntimeError("boom"),
            ):
                result = handler({}, _make_context())

    assert result["statusCode"] == 500
    assert result["body"] == "error"


def test_handler_filters_untriggered_signals():
    triggered = make_signal("AAPL")
    untriggered = make_signal("TSLA")
    untriggered.triggered = False  # type: ignore[assignment]
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with _patch_all_scanners(gainer=[triggered, untriggered]):
                result = handler({}, _make_context())

    assert "1 mean-reversion puts" in result["body"]


def test_handler_uses_request_id_in_log(caplog):
    with caplog.at_level(logging.INFO):
        with patch.dict("os.environ", {"REPORTS_BUCKET": "bucket"}):
            with patch("lambda_handler.boto3.client"):
                with _patch_all_scanners():
                    handler({}, _make_context("my-unique-id"))

    assert any("my-unique-id" in r.message for r in caplog.records)


def test_handler_one_scanner_failure_does_not_block_others():
    """A scanner that raises should not prevent other scanners from writing reports."""
    good_signal = make_signal("AAPL", term="short")
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with _patch_all_scanners(gainer=good_signal) as _:
                # Override broken_momentum to raise after initial setup
                with patch("tailwind_options.sources.broken_momentum.BrokenMomentumScanner") as MockBroken:
                    MockBroken.return_value.check.side_effect = RuntimeError("scanner crashed")
                    with _patch_all_scanners(gainer=[good_signal]):
                        result = handler({}, _make_context())

    assert result["statusCode"] == 200


# ── _write_theme_report_to_s3 ─────────────────────────────────────────────────

def test_write_theme_report_puts_report_object():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_theme_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", "puts", "mean-reversion", log)

    put_calls = mock_s3.put_object.call_args_list
    keys = [c.kwargs["Key"] for c in put_calls]
    assert any("puts/mean-reversion/put-scan-" in k and ".json" in k for k in keys)
    assert any(k == "puts/mean-reversion/manifest.json" for k in keys)


def test_write_theme_report_calls_report_object():
    signals = [make_call_signal("TSLA", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_theme_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", "calls", "ai-momentum", log)

    keys = [c.kwargs["Key"] for c in mock_s3.put_object.call_args_list]
    assert any("calls/ai-momentum/call-scan-" in k and ".json" in k for k in keys)
    assert any(k == "calls/ai-momentum/manifest.json" for k in keys)


def test_write_theme_report_updates_existing_manifest():
    signals = [make_signal("AAPL", term="short")]
    existing = [{"id": "put-scan-old", "generated_at": "2025-12-31_09-31"}]
    mock_s3 = _make_s3({"puts/mean-reversion/manifest.json": existing})
    log = MagicMock()

    _write_theme_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", "puts", "mean-reversion", log)

    manifest_call = next(
        c for c in mock_s3.put_object.call_args_list
        if c.kwargs["Key"] == "puts/mean-reversion/manifest.json"
    )
    written = json.loads(manifest_call.kwargs["Body"])
    assert len(written) == 2
    assert written[0]["id"] == "put-scan-2026-01-01_09-31"
    assert written[1]["id"] == "put-scan-old"


def test_write_theme_report_sets_content_type():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_theme_report_to_s3(signals, mock_s3, "bucket", "2026-01-01_09-31", "puts", "mean-reversion", log)

    for c in mock_s3.put_object.call_args_list:
        assert c.kwargs["ContentType"] == "application/json"


# ── _write_manifest_to_s3 ─────────────────────────────────────────────────────

def test_write_manifest_creates_when_missing():
    mock_s3 = _make_s3()
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/mean-reversion/manifest.json", "put-scan-001", {"tickers_flagged": 1}, "ts")
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/mean-reversion/manifest.json")
    written = json.loads(call.kwargs["Body"])
    assert len(written) == 1
    assert written[0]["id"] == "put-scan-001"


def test_write_manifest_prepends_to_existing():
    existing = [{"id": "put-scan-old", "generated_at": "ts-old"}]
    mock_s3 = _make_s3({"puts/mean-reversion/manifest.json": existing})
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/mean-reversion/manifest.json", "put-scan-new", {"tickers_flagged": 2}, "ts-new")
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/mean-reversion/manifest.json")
    written = json.loads(call.kwargs["Body"])
    assert written[0]["id"] == "put-scan-new"
    assert written[1]["id"] == "put-scan-old"


def test_write_manifest_sets_cache_control():
    mock_s3 = _make_s3()
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/mean-reversion/manifest.json", "put-scan-001", {"tickers_flagged": 1}, "ts")
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/mean-reversion/manifest.json")
    assert call.kwargs["CacheControl"] == "no-store"


def test_write_manifest_deduplicates():
    existing = [{"id": "put-scan-2026-01-01_09-31", "generated_at": "2026-01-01_09-31"}]
    mock_s3 = _make_s3({"puts/mean-reversion/manifest.json": existing})
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/mean-reversion/manifest.json", "put-scan-2026-01-01_09-31", {"tickers_flagged": 1}, "2026-01-01_09-31")
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/mean-reversion/manifest.json")
    written = json.loads(call.kwargs["Body"])
    assert len(written) == 1
