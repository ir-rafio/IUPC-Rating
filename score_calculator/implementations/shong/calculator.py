from score_calculator.model import ScoreCalculator


class ShongScoreCalculator(ScoreCalculator):
    def __init__(self, institution_team_limit: int, rating_degree: float):
        self.institution_team_limit = institution_team_limit
        self.rating_degree = rating_degree

    def calculate(self, performances: list[float]) -> float | None:
        selected = performances[:self.institution_team_limit]
        if not selected:
            return None
        powered_mean = sum(value ** self.rating_degree for value in selected) / len(selected)
        return powered_mean ** (1 / self.rating_degree)
