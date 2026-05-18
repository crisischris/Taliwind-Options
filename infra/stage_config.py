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
        return f"TailwindOptionsStack-{self.stage.capitalize()}"

    @property
    def bucket_name(self) -> str:
        return f"tailwind-options-reports-{self.stage}"

    @property
    def function_name(self) -> str:
        return f"tailwind-options-scanner-{self.stage}"

    @property
    def enable_scheduler(self) -> bool:
        """Daily cron runs in prod only; beta is invoked directly by CI integration tests."""
        return self.stage == "prod"

    @property
    def domain_name(self) -> str | None:
        """Custom domain for prod only. Beta uses the S3 website URL."""
        return "tailwindoptions.com" if self.stage == "prod" else None

    @property
    def enable_monitoring(self) -> bool:
        """CloudWatch alarms + SNS alerts in prod only."""
        return self.stage == "prod"

    @property
    def alert_email(self) -> str:
        return "chrnelsn.general@gmail.com"

    @property
    def alert_phone(self) -> str:
        return "+19522972768"
