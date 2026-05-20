from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from lambda_handler import _InvocationLogger, _write_manifest_to_s3, _write_report_to_s3, handler
from tests.conftest import make_signal


class _NoSuchKey(Exception):
    pass


def _make_s3(existing_puts: list | None = None, existing_calls: list | None = None):
    """Build a mock S3 client with per-manifest-key responses."""
    mock_s3 = MagicMock()
    mock_s3.exceptions.NoSuchKey = _NoSuchKey

    def get_object(Bucket, Key):
        if Key == "puts/manifest.json" and existing_puts is not None:
            return {"Body": MagicMock(read=lambda: json.dumps(existing_puts).encode())}
        if Key == "calls/manifest.json" and existing_calls is not None:
            return {"Body": MagicMock(read=lambda: json.dumps(existing_calls).encode())}
        raise _NoSuchKey("no such key")

    mock_s3.get_object.side_effect = get_object
    return mock_s3


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
            with patch("tailwind_options.sources.gainer_puts.GainerPutScanner") as MockScanner:
                with patch("tailwind_options.call_universe.get_tickers", return_value=[]):
                    with patch("tailwind_options.sources.trend_calls.TrendCallScanner") as MockCallScanner:
                        MockScanner.return_value.check.return_value = []
                        MockCallScanner.return_value.check.return_value = []
                        result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert result["body"] == "no signals"


def test_handler_with_signals():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with patch("tailwind_options.sources.gainer_puts.GainerPutScanner") as MockScanner:
                with patch("tailwind_options.call_universe.get_tickers", return_value=[]):
                    with patch("tailwind_options.sources.trend_calls.TrendCallScanner") as MockCallScanner:
                        MockScanner.return_value.check.return_value = signals
                        MockCallScanner.return_value.check.return_value = []
                        result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert "1 puts" in result["body"]


def test_handler_returns_500_on_exception():
    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client"):
            with patch("tailwind_options.sources.gainer_puts.GainerPutScanner", side_effect=RuntimeError("boom")):
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
            with patch("tailwind_options.sources.gainer_puts.GainerPutScanner") as MockScanner:
                with patch("tailwind_options.call_universe.get_tickers", return_value=[]):
                    with patch("tailwind_options.sources.trend_calls.TrendCallScanner") as MockCallScanner:
                        MockScanner.return_value.check.return_value = [triggered, untriggered]
                        MockCallScanner.return_value.check.return_value = []
                        result = handler({}, _make_context())

    assert "1 puts" in result["body"]


def test_handler_uses_request_id_in_log(caplog):
    with caplog.at_level(logging.INFO):
        with patch.dict("os.environ", {"REPORTS_BUCKET": "bucket"}):
            with patch("lambda_handler.boto3.client"):
                with patch("tailwind_options.sources.gainer_puts.GainerPutScanner") as MockScanner:
                    with patch("tailwind_options.call_universe.get_tickers", return_value=[]):
                        with patch("tailwind_options.sources.trend_calls.TrendCallScanner") as MockCallScanner:
                            MockScanner.return_value.check.return_value = []
                            MockCallScanner.return_value.check.return_value = []
                            handler({}, _make_context("my-unique-id"))

    assert any("my-unique-id" in r.message for r in caplog.records)


# ── _write_report_to_s3 ───────────────────────────────────────────────────────

def test_write_report_puts_report_object():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_report_to_s3(signals, [], mock_s3, "my-bucket", "2026-01-01_09-31", log)

    put_calls = mock_s3.put_object.call_args_list
    keys = [c.kwargs["Key"] for c in put_calls]
    assert any("puts/put-scan-" in k and ".json" in k for k in keys)
    assert any(k == "puts/manifest.json" for k in keys)


def test_write_report_updates_existing_manifest():
    signals = [make_signal("AAPL", term="short")]
    existing = [{"id": "put-scan-old", "generated_at": "2025-12-31_09-31"}]
    mock_s3 = _make_s3(existing_puts=existing)
    log = MagicMock()

    _write_report_to_s3(signals, [], mock_s3, "my-bucket", "2026-01-01_09-31", log)

    manifest_call = next(
        c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/manifest.json"
    )
    written = json.loads(manifest_call.kwargs["Body"])
    assert len(written) == 2
    assert written[0]["id"] == "put-scan-2026-01-01_09-31"
    assert written[1]["id"] == "put-scan-old"


def test_write_report_deduplicates_manifest():
    signals = [make_signal("AAPL", term="short")]
    existing = [{"id": "put-scan-2026-01-01_09-31", "generated_at": "2026-01-01_09-31"}]
    mock_s3 = _make_s3(existing_puts=existing)
    log = MagicMock()

    _write_report_to_s3(signals, [], mock_s3, "my-bucket", "2026-01-01_09-31", log)

    manifest_call = next(
        c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/manifest.json"
    )
    written = json.loads(manifest_call.kwargs["Body"])
    assert len(written) == 1


def test_write_manifest_creates_when_missing():
    mock_s3 = _make_s3()
    log = MagicMock()
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/manifest.json", "put-scan-001", {"tickers_flagged": 1}, "ts", log)
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/manifest.json")
    written = json.loads(call.kwargs["Body"])
    assert len(written) == 1
    assert written[0]["id"] == "put-scan-001"


def test_write_manifest_prepends_to_existing():
    existing = [{"id": "put-scan-old", "generated_at": "ts-old"}]
    mock_s3 = _make_s3(existing_puts=existing)
    log = MagicMock()
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/manifest.json", "put-scan-new", {"tickers_flagged": 2}, "ts-new", log)
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/manifest.json")
    written = json.loads(call.kwargs["Body"])
    assert written[0]["id"] == "put-scan-new"
    assert written[1]["id"] == "put-scan-old"


def test_write_manifest_sets_cache_control():
    mock_s3 = _make_s3()
    log = MagicMock()
    _write_manifest_to_s3(mock_s3, "my-bucket", "puts/manifest.json", "put-scan-001", {"tickers_flagged": 1}, "ts", log)
    call = next(c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "puts/manifest.json")
    assert call.kwargs["CacheControl"] == "no-store"


def test_write_report_sets_content_type():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_report_to_s3(signals, [], mock_s3, "bucket", "2026-01-01_09-31", log)

    for c in mock_s3.put_object.call_args_list:
        assert c.kwargs["ContentType"] == "application/json"
