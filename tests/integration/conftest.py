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
