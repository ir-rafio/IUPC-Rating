from abc import ABC, abstractmethod


class ScoreCalculator(ABC):
    @abstractmethod
    def calculate(self, performances: list[float]) -> float | None:
        raise NotImplementedError
