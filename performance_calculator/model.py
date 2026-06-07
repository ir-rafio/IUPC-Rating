from abc import ABC, abstractmethod


class PerformanceCalculator(ABC):
    @abstractmethod
    def calculate(self, rank: int, solved: int, maximum_solved: int) -> float:
        raise NotImplementedError
