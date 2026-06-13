from abc import ABC, abstractmethod
from pathlib import Path

from .records import Team


class Parser(ABC):
    version = 1

    def parse(self, filepaths: list[Path]) -> tuple[list[Team], list[str]]:
        teams: list[Team] = []
        warnings: list[str] = []
        for filepath in filepaths:
            parsed, file_warnings = self.parse_file(filepath)
            teams.extend(parsed)
            warnings.extend(file_warnings)
        return teams, warnings

    @abstractmethod
    def parse_file(self, filepath: Path) -> tuple[list[Team], list[str]]:
        raise NotImplementedError
