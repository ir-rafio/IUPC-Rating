import argparse
from pathlib import Path

from .common import load_json, save_json


def add_institution(name: str, database_path: Path) -> None:
    institution_name = name.upper()
    data = load_json(database_path)
    known_names = {
        candidate.upper()
        for institution in data["institutions"]
        for candidate in [institution["name"], *institution.get("alt_names", [])]
    }
    if institution_name in known_names:
        raise ValueError(f"Institution name already exists: {institution_name}")
    data["institutions"].append({"name": institution_name, "alt_names": []})
    data["institutions"].sort(key=lambda institution: institution["name"])
    save_json(database_path, data)


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-add-institution")
    command.add_argument("--name", required=True)
    command.add_argument(
        "--database",
        type=Path,
        default=Path("institution_finder/data/institutions.json"),
    )
    arguments = command.parse_args()
    add_institution(arguments.name, arguments.database)
    print(f"Added institution {arguments.name.upper()}.")


if __name__ == "__main__":
    main()
