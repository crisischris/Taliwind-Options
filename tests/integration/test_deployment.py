"""
Integration tests for a deployed stage.

Invoke with INTEG_STAGE=<stage> set, e.g.:
    INTEG_STAGE=beta pytest tests/integration/ -v --override-ini="addopts="
"""
from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from tests.integration.conftest import REGION


@pytest.mark.integration
def test_lambda_invokes_successfully(invocation_result: dict[str, Any]) -> None:
    """Lambda completes without error (signals found or no signals — both return 200)."""
    assert invocation_result["statusCode"] == 200


@pytest.mark.integration
def test_manifest_exists_and_is_valid(
    s3_client: Any, config: Any, invocation_result: dict[str, Any]
) -> None:
    """manifest.json is present, parseable, and each entry has the required fields."""
    obj = s3_client.get_object(Bucket=config.bucket_name, Key="manifest.json")
    manifest = json.loads(obj["Body"].read())
    assert isinstance(manifest, list)
    for entry in manifest:
        assert "id" in entry
        assert "generated_at" in entry
        assert "tickers_flagged" in entry


@pytest.mark.integration
def test_latest_report_is_well_formed(
    s3_client: Any, config: Any, invocation_result: dict[str, Any]
) -> None:
    """The most recent report JSON has the required top-level structure."""
    obj = s3_client.get_object(Bucket=config.bucket_name, Key="manifest.json")
    manifest = json.loads(obj["Body"].read())
    if not manifest:
        pytest.skip("Scanner found no signals today — no report to validate")

    latest_id = manifest[0]["id"]
    report_obj = s3_client.get_object(Bucket=config.bucket_name, Key=f"{latest_id}.json")
    report = json.loads(report_obj["Body"].read())

    assert report.get("id") == latest_id
    assert "generated_at" in report
    assert "summary" in report
    assert isinstance(report.get("tickers"), list)
    assert all(k in report.get("heroes", {}) for k in ("short", "long", "moonshot"))


@pytest.mark.integration
def test_static_site_responds(config: Any) -> None:
    """The S3 static website returns 200 and serves the React app."""
    url = f"http://{config.bucket_name}.s3-website-{REGION}.amazonaws.com"
    resp = httpx.get(url, timeout=15)
    assert resp.status_code == 200
    assert '<div id="root">' in resp.text


@pytest.mark.integration
def test_manifest_s3_consistency(
    s3_client: Any, config: Any, invocation_result: dict[str, Any]
) -> None:
    """Every report ID listed in manifest.json has a corresponding object in S3."""
    obj = s3_client.get_object(Bucket=config.bucket_name, Key="manifest.json")
    manifest = json.loads(obj["Body"].read())
    if not manifest:
        pytest.skip("No reports in manifest")

    for entry in manifest:
        s3_client.head_object(Bucket=config.bucket_name, Key=f"{entry['id']}.json")
