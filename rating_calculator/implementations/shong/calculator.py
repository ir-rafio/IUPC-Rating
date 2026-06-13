import math
from datetime import date

from rating_calculator.model import RatingCalculator


class ShongRatingCalculator(RatingCalculator):
    def __init__(self, time_decay_rate: float, time_decay_pulse_days: float):
        self.time_decay_rate = time_decay_rate
        self.time_decay_pulse_days = time_decay_pulse_days

    def calculate(
        self,
        scores: dict[str, float],
        credits: dict[str, float],
        dates: dict[str, date],
        latest_contest: str,
    ) -> float | None:
        rating_squares = 0.0
        weight_squares = 0.0
        for contest, score in scores.items():
            periods = (dates[latest_contest] - dates[contest]).days // self.time_decay_pulse_days
            weight = credits[contest] * ((1 - self.time_decay_rate) ** periods)
            rating_squares += (score * weight) ** 2
            weight_squares += weight ** 2
        return math.sqrt(rating_squares / weight_squares) if weight_squares else None
