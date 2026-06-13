from abc import ABC, abstractmethod
from datetime import date


class RatingCalculator(ABC):
    @abstractmethod
    def calculate(
        self,
        scores: dict[str, float],
        credits: dict[str, float],
        dates: dict[str, date],
        latest_contest: str,
    ) -> float | None:
        raise NotImplementedError
