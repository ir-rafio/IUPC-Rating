from performance_calculator.model import PerformanceCalculator

from .shong import ShongPerformanceCalculator


def get_calculator(name: str, parameters: dict) -> PerformanceCalculator:
    calculators = {"SHONG": ShongPerformanceCalculator}
    try:
        return calculators[name.upper()](**parameters)
    except KeyError as error:
        raise ValueError(f"Unknown performance calculator: {name}") from error


__all__ = ["PerformanceCalculator", "get_calculator"]
