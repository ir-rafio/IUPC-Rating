import json
from pathlib import Path

import pandas as pd

from institution_finder import InstitutionFinder

from .implementations import get_calculator


def _export(frame: pd.DataFrame, path: Path) -> None:
    exported = frame.reset_index().rename(columns={"index": "Institution"})
    exported.to_csv(path, index=False)


def run(
    input_directory: Path,
    performances_directory: Path,
    contests_directory: Path,
    output_directory: Path,
    institution_database: Path = Path("institution_finder/data/institutions.json"),
) -> None:
    with (input_directory / "options.json").open() as file:
        options = json.load(file)
    contest_metadata = []
    for path in (contests_directory / "contests").glob("*.json"):
        with path.open() as file:
            contest = json.load(file)
        contest_metadata.append((contest["date"], contest["name"]))
    contests = [name for _, name in sorted(contest_metadata)]
    performances = pd.read_csv(performances_directory / "performances.csv")
    available = set(performances["Contest"])
    missing = [contest for contest in contests if contest not in available]
    if missing:
        raise ValueError(f"Missing contest performances: {', '.join(missing)}")
    finder = InstitutionFinder(institution_database)
    performances["Institution"] = performances["Institution"].map(
        lambda name: finder.resolve(name) if isinstance(name, str) else None
    )
    calculator = get_calculator(options["calculator"], options["parameters"])
    institution_names = finder.canonical_names()
    scores = pd.DataFrame(
        index=institution_names,
        columns=[f"Score In {contest}" for contest in reversed(contests)],
    )
    for contest in contests:
        contest_rows = performances[
            (performances["Contest"] == contest) & performances["Performance"].notna()
        ]
        for institution, rows in contest_rows.dropna(subset=["Institution"]).groupby("Institution"):
            values = rows["Performance"].tolist()
            scores.at[institution, f"Score In {contest}"] = calculator.calculate(values)
    scores = scores.infer_objects()
    newest_column = scores.columns[0]
    scores.sort_values(newest_column, ascending=False, na_position="last", inplace=True)
    ranks = scores.rank(axis=0, ascending=False, method="min").astype("Int64")
    ranks.columns = [column.replace("Score In ", "Score Rank In ") for column in ranks.columns]
    output_directory.mkdir(parents=True, exist_ok=True)
    _export(scores, output_directory / "score_history.csv")
    _export(ranks, output_directory / "score_rank_history.csv")
