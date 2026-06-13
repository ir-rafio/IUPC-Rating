from rating_calculator.model import RatingCalculator

from .shong import ShongRatingCalculator


def get_calculator(name: str, parameters: dict) -> RatingCalculator:
    calculators = {"SHONG": ShongRatingCalculator}
    try:
        return calculators[name.upper()](**parameters)
    except KeyError as error:
        raise ValueError(f"Unknown rating calculator: {name}") from error


__all__ = ["RatingCalculator", "get_calculator"]
