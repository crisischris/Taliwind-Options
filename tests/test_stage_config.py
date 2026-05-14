import pytest
from infra.stage_config import StageConfig


def test_beta_stack_name():
    assert StageConfig("beta").stack_name == "OptionsHunterStack-Beta"


def test_prod_stack_name():
    assert StageConfig("prod").stack_name == "OptionsHunterStack-Prod"


def test_beta_bucket_name():
    assert StageConfig("beta").bucket_name == "options-hunter-reports-beta"


def test_prod_bucket_name():
    assert StageConfig("prod").bucket_name == "options-hunter-reports-prod"


def test_beta_function_name():
    assert StageConfig("beta").function_name == "options-hunter-scanner-beta"


def test_prod_function_name():
    assert StageConfig("prod").function_name == "options-hunter-scanner-prod"


def test_prod_enables_scheduler():
    assert StageConfig("prod").enable_scheduler is True


def test_beta_disables_scheduler():
    assert StageConfig("beta").enable_scheduler is False


def test_invalid_stage_raises():
    with pytest.raises(ValueError, match="must be one of"):
        StageConfig("staging")


def test_invalid_stage_empty_string():
    with pytest.raises(ValueError):
        StageConfig("")


def test_frozen_dataclass():
    cfg = StageConfig("beta")
    with pytest.raises((AttributeError, TypeError)):
        cfg.stage = "prod"  # type: ignore[misc]
