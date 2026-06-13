from pathlib import Path

from bs4 import BeautifulSoup, Tag


def standings_rows(filepath: Path) -> list[Tag]:
    with filepath.open(encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    table = soup.find("table")
    if table is None:
        raise ValueError(f"No standings table found in {filepath}")
    return table.find_all("tr")[1:]


def warning(filepath: Path, row_number: int, error: Exception) -> str:
    return f"{filepath.name}: row {row_number}: {type(error).__name__}: {error}"


def optional_rank(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None
