import re
from pathlib import Path

from parser.model import Parser
from parser.records import Team
from parser.implementations.common import optional_rank, standings_rows, warning


class BapsParser(Parser):
    version = 2

    def parse_file(self, filepath: Path) -> tuple[list[Team], list[str]]:
        teams: list[Team] = []
        warnings: list[str] = []
        for row_number, row in enumerate(standings_rows(filepath), start=2):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                solved_text = cells[2].get_text(strip=True)
                team = Team(
                    rank=optional_rank(cells[0].get_text(strip=True)),
                    name=cells[1].find("strong").get_text(strip=True),
                    institution=(cells[1].find("div").get_text(strip=True) if cells[1].find("div") else "").upper(),
                    solved=int(re.search(r"(\d+)", solved_text).group(1)),
                    penalty=int(re.search(r"\((\d+)\)", solved_text).group(1)),
                    first_solve_count=sum(
                        1 for cell in cells[3:]
                        if cell.find("div", style=re.compile(r"animation:.*shine.*"))
                    ),
                )
                teams.append(team)
            except Exception as error:
                warnings.append(warning(filepath, row_number, error))
        return teams, warnings
