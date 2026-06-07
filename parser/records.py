from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Team:
    rank: int | None
    name: str
    institution: str
    solved: int
    penalty: int
    first_solve_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Team":
        return cls(**value)


@dataclass
class ParsedContest:
    name: str
    date: str
    parser: str
    teams: list[Team]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date": self.date,
            "parser": self.parser,
            "teams": [team.to_dict() for team in self.teams],
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ParsedContest":
        return cls(
            name=value["name"],
            date=value["date"],
            parser=value["parser"],
            teams=[Team.from_dict(team) for team in value["teams"]],
            warnings=value.get("warnings", []),
        )
