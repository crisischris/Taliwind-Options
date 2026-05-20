from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Signal:
    triggered: bool
    title: str
    message: str
    subtitle: str = ""
    data: dict[str, Any] = field(default_factory=dict)


class Indicator(ABC):
    """Base class for all indicator checks."""

    @abstractmethod
    def check(self) -> list[Signal]:
        """Run the indicator logic and return any triggered signals."""
        ...
