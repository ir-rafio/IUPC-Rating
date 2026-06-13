import argparse
import shutil
from datetime import date
from pathlib import Path

from parser.implementations import get_parser

from .common import load_json, save_json


def add_contest(
    html_path: Path,
    name: str,
    contest_date: str,
    parser: str,
    credit: float,
    parser_input: Path,
    credits_path: Path,
) -> None:
    contest_name = name.upper()
    date.fromisoformat(contest_date)
    get_parser(parser)
    if credit <= 0:
        raise ValueError("Credit must be greater than zero.")
    if not html_path.is_file():
        raise FileNotFoundError(f"Contest HTML not found: {html_path}")
    contests_path = parser_input / "contests.json"
    contests_data = load_json(contests_path)
    credits = load_json(credits_path)
    if any(contest["name"].upper() == contest_name for contest in contests_data["contests"]):
        raise ValueError(f"Contest already exists: {contest_name}")
    if contest_name in {key.upper() for key in credits}:
        raise ValueError(f"Contest credit already exists: {contest_name}")
    destination = parser_input / "contest_files" / html_path.name
    if destination.exists():
        raise FileExistsError(f"Contest HTML already exists: {destination}")
    contests_data["contests"].append({
        "name": contest_name,
        "filenames": [html_path.name],
        "parser": parser.upper(),
        "date": contest_date,
    })
    credits[contest_name] = credit
    shutil.copy2(html_path, destination)
    save_json(contests_path, contests_data)
    save_json(credits_path, credits)


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-add-contest")
    command.add_argument("--html", required=True, type=Path)
    command.add_argument("--name", required=True)
    command.add_argument("--date", required=True)
    command.add_argument("--parser", required=True, choices=["BAPS", "TOPH"])
    command.add_argument("--credit", type=float, default=1)
    command.add_argument("--parser-input", type=Path, default=Path("parser/input"))
    command.add_argument(
        "--credits",
        type=Path,
        default=Path("rating_calculator/input/credits.json"),
    )
    arguments = command.parse_args()
    add_contest(
        arguments.html,
        arguments.name,
        arguments.date,
        arguments.parser,
        arguments.credit,
        arguments.parser_input,
        arguments.credits,
    )
    print(f"Added contest {arguments.name.upper()}.")


if __name__ == "__main__":
    main()
