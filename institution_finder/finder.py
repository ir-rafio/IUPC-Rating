import json
from difflib import SequenceMatcher
from pathlib import Path


class InstitutionFinder:
    def __init__(self, database_path: Path):
        with database_path.open() as file:
            self.institutions = json.load(file)["institutions"]
        self.names = {
            candidate.upper(): institution["name"].upper()
            for institution in self.institutions
            for candidate in [institution["name"], *institution.get("alt_names", [])]
        }

    def resolve(self, name: str) -> str | None:
        return self.names.get(name.upper())

    def canonical_names(self) -> list[str]:
        return [institution["name"].upper() for institution in self.institutions]

    def best_match(self, name: str, allowed_names: set[str] | None = None) -> tuple[str, float]:
        candidates = [
            (candidate, canonical)
            for candidate, canonical in self.names.items()
            if allowed_names is None or canonical in allowed_names
        ]
        probability, canonical = max(
            (
                (SequenceMatcher(None, name.upper(), candidate).ratio(), canonical)
                for candidate, canonical in candidates
            ),
            default=(0, ""),
        )
        return canonical, round(probability * 100, 2)
