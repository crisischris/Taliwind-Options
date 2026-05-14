from dataclasses import dataclass

VALID_STAGES = {"beta", "prod"}


@dataclass(frozen=True)
class StageConfig:
    stage: str

    def __post_init__(self):
        if self.stage not in VALID_STAGES:
            raise ValueError(f"stage must be one of {VALID_STAGES}, got '{self.stage}'")

    @property
    def stack_name(self) -> str:
        return f"OptionsHunterStack-{self.stage.capitalize()}"

    @property
    def bucket_name(self) -> str:
        return f"options-hunter-reports-{self.stage}"

    @property
    def function_name(self) -> str:
        return f"options-hunter-scanner-{self.stage}"

    @property
    def enable_scheduler(self) -> bool:
        """Daily cron runs in prod only; beta is invoked directly by CI integration tests."""
        return self.stage == "prod"
