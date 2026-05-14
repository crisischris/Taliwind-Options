from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from lambda_handler import _InvocationLogger, handler, _write_report_to_s3
from tests.conftest import make_signal


class _NoSuchKey(Exception):
    pass


def _make_s3(manifest_exists: bool = False, existing_manifest: list | None = None):
    """Build a mock S3 client with correct exception behavior."""
    mock_s3 = MagicMock()
    mock_s3.exceptions.NoSuchKey = _NoSuchKey

    if manifest_exists and existing_manifest is not None:
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: json.dumps(existing_manifest).encode())
        }
    else:
        mock_s3.get_object.side_effect = _NoSuchKey("no such key")

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
            with patch("indicators.sources.gainer_puts.GainerPutScanner") as MockScanner:
                MockScanner.return_value.check.return_value = []
                result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert result["body"] == "no signals"


def test_handler_with_signals():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()

    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client", return_value=mock_s3):
            with patch("indicators.sources.gainer_puts.GainerPutScanner") as MockScanner:
                MockScanner.return_value.check.return_value = signals
                result = handler({}, _make_context())

    assert result["statusCode"] == 200
    assert "1 signals" in result["body"]


def test_handler_returns_500_on_exception():
    with patch.dict("os.environ", {"REPORTS_BUCKET": "test-bucket"}):
        with patch("lambda_handler.boto3.client"):
            with patch("indicators.sources.gainer_puts.GainerPutScanner", side_effect=RuntimeError("boom")):
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
            with patch("indicators.sources.gainer_puts.GainerPutScanner") as MockScanner:
                MockScanner.return_value.check.return_value = [triggered, untriggered]
                result = handler({}, _make_context())

    assert "1 signals" in result["body"]


def test_handler_uses_request_id_in_log(caplog):
    with caplog.at_level(logging.INFO):
        with patch.dict("os.environ", {"REPORTS_BUCKET": "bucket"}):
            with patch("lambda_handler.boto3.client"):
                with patch("indicators.sources.gainer_puts.GainerPutScanner") as MockScanner:
                    MockScanner.return_value.check.return_value = []
                    handler({}, _make_context("my-unique-id"))

    assert any("my-unique-id" in r.message for r in caplog.records)


# ── _write_report_to_s3 ───────────────────────────────────────────────────────

def test_write_report_puts_report_object():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", log)

    put_calls = mock_s3.put_object.call_args_list
    keys = [c.kwargs["Key"] for c in put_calls]
    assert any("put-scan-" in k and ".json" in k for k in keys)
    assert any(k == "manifest.json" for k in keys)


def test_write_report_updates_existing_manifest():
    signals = [make_signal("AAPL", term="short")]
    existing = [{"id": "put-scan-old", "generated_at": "2025-12-31_09-31"}]
    mock_s3 = _make_s3(manifest_exists=True, existing_manifest=existing)
    log = MagicMock()

    _write_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", log)

    manifest_call = next(
        c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "manifest.json"
    )
    written = json.loads(manifest_call.kwargs["Body"])
    assert len(written) == 2
    assert written[0]["id"] == "put-scan-2026-01-01_09-31"
    assert written[1]["id"] == "put-scan-old"


def test_write_report_deduplicates_manifest():
    signals = [make_signal("AAPL", term="short")]
    existing = [{"id": "put-scan-2026-01-01_09-31", "generated_at": "2026-01-01_09-31"}]
    mock_s3 = _make_s3(manifest_exists=True, existing_manifest=existing)
    log = MagicMock()

    _write_report_to_s3(signals, mock_s3, "my-bucket", "2026-01-01_09-31", log)

    manifest_call = next(
        c for c in mock_s3.put_object.call_args_list if c.kwargs["Key"] == "manifest.json"
    )
    written = json.loads(manifest_call.kwargs["Body"])
    assert len(written) == 1


def test_write_report_sets_content_type():
    signals = [make_signal("AAPL", term="short")]
    mock_s3 = _make_s3()
    log = MagicMock()

    _write_report_to_s3(signals, mock_s3, "bucket", "2026-01-01_09-31", log)

    for c in mock_s3.put_object.call_args_list:
        assert c.kwargs["ContentType"] == "application/json"
