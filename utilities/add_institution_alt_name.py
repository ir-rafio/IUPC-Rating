import argparse
from pathlib import Path

from .common import load_json, save_json


def add_institution_alt_name(institution_name: str, alt_name: str, database_path: Path) -> None:
    canonical = institution_name.upper()
    alternate = alt_name.upper()
    data = load_json(database_path)
    known_names = {
        candidate.upper()
        for institution in data["institutions"]
        for candidate in [institution["name"], *institution.get("alt_names", [])]
    }
    if alternate in known_names:
        raise ValueError(f"Institution name already exists: {alternate}")
    institution = next(
        (value for value in data["institutions"] if value["name"].upper() == canonical),
        None,
    )
    if institution is None:
        raise ValueError(f"Canonical institution not found: {canonical}")
    institution.setdefault("alt_names", []).append(alternate)
    institution["alt_names"].sort()
    save_json(database_path, data)


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-add-institution-alt-name")
    command.add_argument("--institution", required=True)
    command.add_argument("--alt-name", required=True)
    command.add_argument(
        "--database",
        type=Path,
        default=Path("institution_finder/data/institutions.json"),
    )
    arguments = command.parse_args()
    add_institution_alt_name(arguments.institution, arguments.alt_name, arguments.database)
    print(f"Added alternate name {arguments.alt_name.upper()}.")


if __name__ == "__main__":
    main()
