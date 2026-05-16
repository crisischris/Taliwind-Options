from __future__ import annotations

import json
import os
import sys

import pytest

boto3 = pytest.importorskip("boto3")  # auto-skips all integration tests if boto3 missing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../infra"))
from stage_config import StageConfig  # noqa: E402

REGION = "us-east-1"
_stage = os.environ.get("INTEG_STAGE", "beta")
_config = StageConfig(_stage)


@pytest.fixture(scope="session")
def config() -> StageConfig:
    return _config


@pytest.fixture(scope="session")
def s3_client():
    return boto3.client("s3", region_name=REGION)


@pytest.fixture(scope="session")
def lambda_client():
    return boto3.client("lambda", region_name=REGION)


@pytest.fixture(scope="session")
def invocation_result(lambda_client, config):
    """Invoke the scanner once per CI run; all S3 tests share this result."""
    resp = lambda_client.invoke(
        FunctionName=config.function_name,
        InvocationType="RequestResponse",
    )
    return json.loads(resp["Payload"].read())


@pytest.fixture(scope="session", autouse=True)
def _cleanup_artifacts(s3_client, config):
    """Delete any S3 reports written during this test run."""
    def _read_manifest(prefix: str) -> set[str]:
        try:
            obj = s3_client.get_object(Bucket=config.bucket_name, Key=f"{prefix}/manifest.json")
            return {e["id"] for e in json.loads(obj["Body"].read())}
        except Exception:
            return set()

    before_puts = _read_manifest("puts")
    before_calls = _read_manifest("calls")

    yield

    for prefix, before_ids in (("puts", before_puts), ("calls", before_calls)):
        try:
            obj = s3_client.get_object(Bucket=config.bucket_name, Key=f"{prefix}/manifest.json")
            after_manifest = json.loads(obj["Body"].read())
        except Exception:
            continue

        new_ids = {e["id"] for e in after_manifest} - before_ids
        if not new_ids:
            continue

        for report_id in new_ids:
            s3_client.delete_object(Bucket=config.bucket_name, Key=f"{prefix}/{report_id}.json")

        surviving = [e for e in after_manifest if e["id"] not in new_ids]
        s3_client.put_object(
            Bucket=config.bucket_name,
            Key=f"{prefix}/manifest.json",
            Body=json.dumps(surviving, indent=2),
            ContentType="application/json",
        )
