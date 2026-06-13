import json
from pathlib import Path

import pandas as pd

from institution_finder import InstitutionFinder

from .implementations import get_calculator


def run(
    input_directory: Path,
    contests_directory: Path,
    output_directory: Path,
    institution_database: Path = Path("institution_finder/data/institutions.json"),
) -> Path:
    with (input_directory / "options.json").open() as file:
        options = json.load(file)
    calculator = get_calculator(options["calculator"], options["parameters"])
    finder = InstitutionFinder(institution_database)
    rows = []
    for path in sorted((contests_directory / "contests").glob("*.json")):
        with path.open() as file:
            contest = json.load(file)
        ranked_teams = [team for team in contest["teams"] if team["rank"] is not None]
        maximum_solved = max((team["solved"] for team in ranked_teams), default=0)
        for team in contest["teams"]:
            institution = finder.resolve(team["institution"])
            rows.append({
                "Contest": contest["name"],
                "Team": team["name"],
                "Institution": institution,
                "Performance": (
                    calculator.calculate(team["rank"], team["solved"], maximum_solved)
                    if team["rank"] is not None
                    else None
                ),
            })
    performances = pd.DataFrame(
        rows,
        columns=["Contest", "Team", "Institution", "Performance"],
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "performances.csv"
    performances.to_csv(output_path, index=False)
    return output_path
