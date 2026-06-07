import argparse
from pathlib import Path

from .service import run


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-slot-distributor")
    command.add_argument("--input", type=Path, default=Path("slot_distributor/input"))
    command.add_argument("--ratings", type=Path, default=Path("rating_calculator/output"))
    command.add_argument("--output", type=Path, default=Path("slot_distributor/output"))
    command.add_argument(
        "--institutions",
        type=Path,
        default=Path("institution_finder/data/institutions.json"),
    )
    arguments = command.parse_args()
    output = run(arguments.input, arguments.ratings, arguments.output, arguments.institutions)
    print(f"Generated slot distribution sheet at {output}.")


if __name__ == "__main__":
    main()
