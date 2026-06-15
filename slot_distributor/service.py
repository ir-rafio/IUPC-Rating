import json
from pathlib import Path

import pandas as pd

from institution_finder import InstitutionFinder

from .exporter import generate_excel
from .implementations import get_distributor


def _validate_input_directory(input_directory: Path) -> tuple[Path, Path]:
    if input_directory.name.lower() == "example":
        raise ValueError("Example inputs cannot be used for slot distribution.")
    registered_path = input_directory / "registered.txt"
    options_path = input_directory / "options.json"
    missing = [path.name for path in (registered_path, options_path) if not path.is_file()]
    if missing:
        names = ", ".join(missing)
        raise FileNotFoundError(f"Missing slot distributor input files: {names}.")
    if not registered_path.read_text().strip():
        raise ValueError("registered.txt does not contain any institutions.")
    return registered_path, options_path


def _resolve_registered(
    ratings: pd.DataFrame,
    registered_path: Path,
    output_directory: Path,
    finder: InstitutionFinder,
) -> tuple[set[str], set[str]]:
    targets = {line.strip().upper() for line in registered_path.read_text().splitlines() if line.strip()}
    available = {name.upper(): name for name in ratings["Institution"]}
    rated = set()
    unrated = set()
    missing_targets = set()
    for target in targets:
        if target in available:
            rated.add(available[target])
            continue
        canonical = finder.resolve(target)
        if canonical is None:
            missing_targets.add(target)
        elif canonical in available:
            rated.add(available[canonical])
        else:
            # Recognized in the institution database but never rated -> NULL rating.
            unrated.add(canonical)
    if missing_targets:
        missing = []
        for target in sorted(missing_targets):
            best_match, probability = finder.best_match(target, set(available))
            missing.append({
                "Missing Institution": target,
                "Best Possible Match": best_match,
                "Probability": probability,
            })
        output_directory.mkdir(parents=True, exist_ok=True)
        report = output_directory / "missing.csv"
        pd.DataFrame(missing).to_csv(report, index=False)
        raise ValueError(f"Registered institutions were not found. See {report}.")
    return rated, unrated


def run(
    input_directory: Path,
    ratings_directory: Path,
    output_directory: Path,
    institution_database: Path = Path("institution_finder/data/institutions.json"),
) -> Path:
    registered_path, options_path = _validate_input_directory(input_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "slots.xlsx"
    missing_path = output_directory / "missing.csv"
    output_path.unlink(missing_ok=True)
    missing_path.unlink(missing_ok=True)
    with options_path.open() as file:
        options = json.load(file)
    ratings = pd.read_csv(ratings_directory / "latest_ratings.csv")
    finder = InstitutionFinder(institution_database)
    rated, unrated = _resolve_registered(
        ratings,
        registered_path,
        output_directory,
        finder,
    )
    considered = ratings[ratings["Institution"].isin(rated)].copy()
    if unrated:
        null_ratings = pd.DataFrame({"Institution": sorted(unrated), "Rating": [float("nan")] * len(unrated)})
        considered = pd.concat([considered, null_ratings], ignore_index=True)
    distributor = get_distributor(options["distributor"], options["parameters"])
    slots, waiting_list = distributor.distribute(considered)
    generate_excel(considered, slots, waiting_list, output_path)
    return output_path
