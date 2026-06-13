import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .records import ParsedContest
from .implementations import get_parser
from .repository import ParsedContestRepository, contest_id


def _hash_files(paths: list[Path]) -> list[str]:
    return [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]


def run(input_directory: Path, output_directory: Path, force: bool = False) -> dict[str, int]:
    with (input_directory / "contests.json").open() as file:
        contests = json.load(file)["contests"]
    with (input_directory / "options.json").open() as file:
        options = json.load(file)
    source_directory = input_directory / "contest_files"
    repository = ParsedContestRepository(output_directory)
    manifest = repository.load_manifest()
    parsed_count = 0
    skipped_count = 0

    for configuration in contests:
        parser = get_parser(configuration["parser"])
        files = [source_directory / name for name in configuration["filenames"]]
        hashes = _hash_files(files)
        key = contest_id(configuration["name"])
        prior = manifest["contests"].get(key)
        current_signature = {
            "source_files": configuration["filenames"],
            "source_hashes": hashes,
            "parser": configuration["parser"].upper(),
            "parser_version": parser.version,
            "date": configuration["date"],
        }
        contest_path = repository.contests_directory / f"{key}.json"
        if not force and prior and all(prior.get(field) == value for field, value in current_signature.items()) and contest_path.exists():
            skipped_count += 1
            continue

        teams, warnings = parser.parse(files)
        if not teams:
            raise ValueError(f"No teams parsed for {configuration['name']}")
        if warnings and options["fail_on_warnings"]:
            raise ValueError(f"Parser warnings for {configuration['name']}: {warnings}")
        repository.save(ParsedContest(
            name=configuration["name"].upper(),
            date=configuration["date"],
            parser=configuration["parser"].upper(),
            teams=teams,
            warnings=warnings,
        ))
        manifest["contests"][key] = {
            **current_signature,
            "parsed_at": datetime.now(timezone.utc).isoformat(),
            "team_count": len(teams),
            "warning_count": len(warnings),
        }
        parsed_count += 1

    repository.save_manifest(manifest)
    return {"parsed": parsed_count, "skipped": skipped_count}
