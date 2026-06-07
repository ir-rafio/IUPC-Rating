import argparse
from pathlib import Path

from .service import run


def main() -> None:
    command = argparse.ArgumentParser(prog="iupc-parser")
    command.add_argument("--input", type=Path, default=Path("parser/input"))
    command.add_argument("--output", type=Path, default=Path("parser/output"))
    command.add_argument("--force", action="store_true")
    arguments = command.parse_args()
    result = run(arguments.input, arguments.output, arguments.force)
    print(f"Parsed {result['parsed']} contest(s); skipped {result['skipped']}.")


if __name__ == "__main__":
    main()
