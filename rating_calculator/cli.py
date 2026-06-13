import argparse
from pathlib import Path

from .service import run


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-rating-calculator")
    command.add_argument("--input", type=Path, default=Path("rating_calculator/input"))
    command.add_argument("--scores", type=Path, default=Path("score_calculator/output"))
    command.add_argument("--contests", type=Path, default=Path("parser/output"))
    command.add_argument("--output", type=Path, default=Path("rating_calculator/output"))
    command.add_argument(
        "--institutions",
        type=Path,
        default=Path("institution_finder/data/institutions.json"),
    )
    arguments = command.parse_args()
    run(
        arguments.input,
        arguments.scores,
        arguments.contests,
        arguments.output,
        arguments.institutions,
    )
    print(f"Generated ratings in {arguments.output}.")


if __name__ == "__main__":
    main()
