from score_calculator.model import ScoreCalculator

from .shong import ShongScoreCalculator


def get_calculator(name: str, parameters: dict) -> ScoreCalculator:
    calculators = {"SHONG": ShongScoreCalculator}
    try:
        return calculators[name.upper()](**parameters)
    except KeyError as error:
        raise ValueError(f"Unknown score calculator: {name}") from error


__all__ = ["ScoreCalculator", "get_calculator"]
