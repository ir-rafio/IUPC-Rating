import json
import tempfile
from pathlib import Path

from utilities.add_contest import add_contest
from utilities.add_institution import add_institution
from utilities.add_institution_alt_name import add_institution_alt_name


def test_add_contest_updates_parser_and_rating_inputs():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parser_input = root / "parser"
        parser_input.mkdir()
        (parser_input / "contest_files").mkdir()
        (parser_input / "contests.json").write_text('{"contests": []}')
        credits = root / "credits.json"
        credits.write_text("{}")
        html = root / "contest.html"
        html.write_text("<table></table>")
        add_contest(
            html,
            "Test Contest",
            "2026-06-01",
            "TOPH",
            1.5,
            parser_input,
            credits,
        )
        contest = json.loads((parser_input / "contests.json").read_text())["contests"][0]
        assert contest["name"] == "TEST CONTEST"
        assert json.loads(credits.read_text())["TEST CONTEST"] == 1.5
        assert (parser_input / "contest_files" / "contest.html").exists()


def test_add_institution_and_alt_name():
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "institutions.json"
        database.write_text('{"institutions": []}')
        add_institution("Test University", database)
        add_institution_alt_name("Test University", "Test U", database)
        institution = json.loads(database.read_text())["institutions"][0]
        assert institution == {
            "name": "TEST UNIVERSITY",
            "alt_names": ["TEST U"],
        }
