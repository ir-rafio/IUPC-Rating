import re
from pathlib import Path

from parser.implementations.common import optional_rank, standings_rows, warning
from parser.model import Parser
from parser.records import Team


class TophParser(Parser):
    version = 1

    def parse_file(self, filepath: Path) -> tuple[list[Team], list[str]]:
        teams: list[Team] = []
        warnings: list[str] = []
        for row_number, row in enumerate(standings_rows(filepath), start=2):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                teams.append(self._parse_row(cells))
            except Exception as error:
                warnings.append(warning(filepath, row_number, error))
        return teams, warnings

    def _parse_row(self, cells) -> Team:
        team_cell = cells[1]
        result_cell = cells[2]
        institution_element = team_cell.find("div", class_="adjunct")
        penalty_element = result_cell.find("div", class_="adjunct")
        penalty_text = penalty_element.get("data-tippy-content", "") if penalty_element else ""
        penalty_match = re.search(r"Penalty:\s*(\d+)", penalty_text)
        current_layout = team_cell.find("div", class_="d-flex") is not None
        return Team(
            rank=optional_rank(cells[0].get_text(strip=True)),
            name=self._team_name(team_cell, current_layout),
            institution=(institution_element.get_text(strip=True) if institution_element else "").upper(),
            solved=int(result_cell.find("strong").get_text(strip=True)),
            penalty=int(penalty_match.group(1)) if penalty_match else 0,
            first_solve_count=self._first_solve_count(cells[3:], current_layout),
        )

    def _team_name(self, team_cell, current_layout: bool) -> str:
        if not current_layout:
            return team_cell.contents[0].strip()
        container = team_cell.find("div", class_="d-flex")
        name_element = container.find("div") if container else None
        return name_element.contents[0].strip() if name_element else ""

    def _first_solve_count(self, cells, current_layout: bool) -> int:
        if current_layout:
            return sum(
                1 for cell in cells
                if cell.find("use") and "#star" in (
                    cell.find("use").get("href") or cell.find("use").get("xlink:href") or ""
                )
            )
        return sum(
            1 for cell in cells
            if cell.find("img", class_="icon green")
            and cell.find("img", class_="icon green").get("data-tippy-content") == "First to Solve"
        )
