import json
from datetime import date
from pathlib import Path

import pandas as pd

from institution_finder import InstitutionFinder

from .implementations import get_calculator


def _export(frame: pd.DataFrame, path: Path) -> None:
    exported = frame.reset_index().rename(columns={"index": "Institution"})
    exported.to_csv(path, index=False)


def run(
    input_directory: Path,
    scores_directory: Path,
    contests_directory: Path,
    output_directory: Path,
    institution_database: Path = Path("institution_finder/data/institutions.json"),
) -> None:
    with (input_directory / "credits.json").open() as file:
        credits = {name.upper(): value for name, value in json.load(file).items()}
    with (input_directory / "options.json").open() as file:
        options = json.load(file)
    dates = {}
    for path in (contests_directory / "contests").glob("*.json"):
        with path.open() as file:
            contest = json.load(file)
        dates[contest["name"]] = date.fromisoformat(contest["date"])
    missing_metadata = [name for name in credits if name not in dates]
    if missing_metadata:
        raise ValueError(f"Missing parsed contest metadata: {', '.join(missing_metadata)}")
    contests = sorted(credits, key=dates.get)
    score_history = pd.read_csv(scores_directory / "score_history.csv")
    score_columns = {column.removeprefix("Score In "): column for column in score_history if column != "Institution"}
    missing = [contest for contest in contests if contest not in score_columns]
    if missing:
        raise ValueError(f"Missing contest scores: {', '.join(missing)}")
    finder = InstitutionFinder(institution_database)
    score_history["Institution"] = score_history["Institution"].map(finder.resolve)
    score_history.dropna(subset=["Institution"], inplace=True)
    score_history.set_index("Institution", inplace=True)
    calculator = get_calculator(options["calculator"], options["parameters"])
    ratings = pd.DataFrame(
        index=finder.canonical_names(),
        columns=[f"Rating After {contest}" for contest in reversed(contests)],
    )
    processed = []
    for latest_contest in contests:
        processed.append(latest_contest)
        for institution in ratings.index:
            institution_scores = {
                contest: score_history.at[institution, score_columns[contest]]
                for contest in processed
                if institution in score_history.index
                and pd.notna(score_history.at[institution, score_columns[contest]])
            }
            ratings.at[institution, f"Rating After {latest_contest}"] = calculator.calculate(
                institution_scores,
                credits,
                dates,
                latest_contest,
            )
    ratings = ratings.infer_objects()
    ratings.sort_values(ratings.columns[0], ascending=False, na_position="last", inplace=True)
    ranks = ratings.rank(axis=0, ascending=False, method="min").astype("Int64")
    ranks.columns = [column.replace("Rating After ", "Rating Rank After ") for column in ranks.columns]
    ratings = ratings.round(0).astype("Int64")
    output_directory.mkdir(parents=True, exist_ok=True)
    _export(ratings, output_directory / "ratings_history.csv")
    _export(ranks, output_directory / "rating_rank_history.csv")
    latest_ratings = ratings[[ratings.columns[0]]].rename(columns={ratings.columns[0]: "Rating"})
    _export(latest_ratings, output_directory / "latest_ratings.csv")
