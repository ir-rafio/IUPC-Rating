import json
from pathlib import Path

from .records import ParsedContest


def contest_id(name: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in name).strip("-")


class ParsedContestRepository:
    def __init__(self, directory: Path):
        self.directory = directory
        self.contests_directory = directory / "contests"
        self.manifest_path = directory / "manifest.json"

    def load_manifest(self) -> dict:
        if not self.manifest_path.exists():
            return {"contests": {}}
        with self.manifest_path.open() as file:
            return json.load(file)

    def save_manifest(self, manifest: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        with self.manifest_path.open("w") as file:
            json.dump(manifest, file, indent=4)

    def save(self, contest: ParsedContest) -> None:
        self.contests_directory.mkdir(parents=True, exist_ok=True)
        with (self.contests_directory / f"{contest_id(contest.name)}.json").open("w") as file:
            json.dump(contest.to_dict(), file, indent=4)
