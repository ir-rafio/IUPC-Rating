import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from parser.service import run as parse
from performance_calculator.model import PerformanceCalculator
from performance_calculator.service import run as calculate_performances
from rating_calculator.model import RatingCalculator
from rating_calculator.service import run as calculate_ratings
from score_calculator.model import ScoreCalculator
from score_calculator.service import run as calculate_scores


ROOT = Path(__file__).resolve().parents[1]


def test_calculator_models_are_abstract():
    for model in [PerformanceCalculator, ScoreCalculator, RatingCalculator]:
        with pytest.raises(TypeError):
            model()


def test_calculator_pipeline_generates_declared_outputs():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests"
        performances = root / "performances"
        scores = root / "scores"
        ratings = root / "ratings"
        parse(ROOT / "parser/input", contests)
        calculate_performances(ROOT / "performance_calculator/input", contests, performances)
        calculate_scores(ROOT / "score_calculator/input", performances, contests, scores)
        calculate_ratings(ROOT / "rating_calculator/input", scores, contests, ratings)
        assert sorted(path.name for path in performances.iterdir()) == ["performances.csv"]
        assert sorted(path.name for path in scores.iterdir()) == [
            "score_history.csv",
            "score_rank_history.csv",
        ]
        assert sorted(path.name for path in ratings.iterdir()) == [
            "latest_ratings.csv",
            "rating_rank_history.csv",
            "ratings_history.csv",
        ]
        performance_columns = pd.read_csv(performances / "performances.csv").columns.tolist()
        assert performance_columns == ["Contest", "Team", "Institution", "Performance"]
        parsed_team_count = sum(
            len(json.loads(path.read_text())["teams"])
            for path in (contests / "contests").glob("*.json")
        )
        assert len(pd.read_csv(performances / "performances.csv")) == parsed_team_count
        assert "Rating After NDUB 2026" in pd.read_csv(ratings / "ratings_history.csv")
        assert pd.read_csv(ratings / "latest_ratings.csv").columns.tolist() == [
            "Institution",
            "Rating",
        ]


def test_performance_calculator_uses_canonical_institution_names():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests"
        output = root / "performances"
        parse(ROOT / "parser/input", contests)
        calculate_performances(ROOT / "performance_calculator/input", contests, output)
        institutions = set(pd.read_csv(output / "performances.csv")["Institution"].dropna())
        assert "BANGLADESH UNIVERSITY OF ENGINEERING AND TECHNOLOGY" in institutions
        assert "BANGLADESH UNIVERSITY OF ENGINEERING & TECHNOLOGY" not in institutions


def test_score_calculator_fails_when_parsed_contest_performances_are_missing():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests" / "contests"
        contests.mkdir(parents=True)
        (contests / "missing.json").write_text(json.dumps({
            "name": "MISSING CONTEST",
            "date": "2026-01-01",
        }))
        performances = root / "performances"
        performances.mkdir()
        pd.DataFrame([{
            "Contest": "OTHER CONTEST",
            "Team": "A",
            "Institution": "UNIVERSITY OF DHAKA",
            "Performance": 4000,
        }]).to_csv(performances / "performances.csv", index=False)
        with pytest.raises(ValueError, match="MISSING CONTEST"):
            calculate_scores(
                ROOT / "score_calculator/input",
                performances,
                root / "contests",
                root / "scores",
            )


def test_rating_calculator_fails_when_credited_contest_is_missing():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        scores = root / "scores"
        scores.mkdir()
        pd.DataFrame([{"Institution": "UNIVERSITY OF DHAKA", "Score In OTHER": 4000}]).to_csv(
            scores / "score_history.csv",
            index=False,
        )
        with pytest.raises(ValueError, match="CUET 2024"):
            calculate_ratings(
                ROOT / "rating_calculator/input",
                scores,
                ROOT / "parser/output",
                root / "ratings",
            )
