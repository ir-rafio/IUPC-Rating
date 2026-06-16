import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from parser.service import run as parse
from performance_calculator.service import run as calculate_performances
from rating_calculator.service import run as calculate_ratings
from score_calculator.service import run as calculate_scores
from slot_distributor.exporter import _build_slot_sheet
from slot_distributor.implementations.priority import PrioritySlotDistributor
from slot_distributor.model import SlotDistributor
from slot_distributor.service import run


ROOT = Path(__file__).resolve().parents[1]


def calculate(root: Path, contests: Path, ratings: Path) -> None:
    performances = root / "performances"
    scores = root / "scores"
    calculate_performances(ROOT / "performance_calculator/input", contests, performances)
    calculate_scores(ROOT / "score_calculator/input", performances, contests, scores)
    calculate_ratings(ROOT / "rating_calculator/input", scores, contests, ratings)


def create_real_inputs(inputs: Path) -> None:
    examples = ROOT / "slot_distributor/input/example"
    inputs.mkdir()
    shutil.copy2(examples / "registered.txt", inputs / "registered.txt")
    shutil.copy2(examples / "options.json", inputs / "options.json")


def test_slot_distributor_model_is_abstract():
    with pytest.raises(TypeError):
        SlotDistributor()


def test_slot_distributor_generates_workbook():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests"
        ratings = root / "ratings"
        inputs = root / "distribution-input"
        output = root / "distribution-output"
        parse(ROOT / "parser/input", contests)
        calculate(root, contests, ratings)
        create_real_inputs(inputs)
        workbook = run(inputs, ratings, output)
        with zipfile.ZipFile(workbook) as archive:
            assert "xl/workbook.xml" in archive.namelist()
            workbook_xml = archive.read("xl/workbook.xml").decode()
            assert "Read Me" in workbook_xml
            assert "Waiting List" in workbook_xml
            assert "Ratings" in workbook_xml
            assert any(
                b"therealbcs.com/slots" in archive.read(name)
                for name in archive.namelist()
            )


def test_waiting_list_continues_priority_sequence_and_allows_repeats():
    ratings = pd.DataFrame({
        "Institution": ["A", "B"],
        "Rating": [4000, 1000],
    })
    distributor = PrioritySlotDistributor(total_slots=2, max_slots=5, waiting_list_size=4, min_unique=2)
    slots, waiting = distributor.distribute(ratings)
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"A": 1, "B": 1}
    assert waiting["Institution"].tolist().count("A") > 1
    assert waiting["Position"].tolist() == [1, 2, 3, 4]


def test_min_unique_caps_guaranteed_first_slots():
    ratings = pd.DataFrame({
        "Institution": ["A", "B", "C"],
        "Rating": [600, 400, 100],
    })
    distributor = PrioritySlotDistributor(total_slots=4, max_slots=5, waiting_list_size=5, min_unique=2)
    slots, waiting = distributor.distribute(ratings)
    # Only the top two institutions are guaranteed a slot; the remaining two
    # slots follow priority, so B's later slots outrank C's first slot.
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"A": 2, "B": 2, "C": 0}
    # The slotless institution waits for its first slot ahead of everyone else.
    assert waiting.iloc[0]["Institution"] == "C"
    assert waiting.iloc[0]["Potential Slot Number"] == 1


def test_equal_priority_breaks_ties_toward_fewer_slots():
    ratings = pd.DataFrame({
        "Institution": ["A", "B"],
        "Rating": [600, 400],
    })
    distributor = PrioritySlotDistributor(total_slots=4, max_slots=5, waiting_list_size=0, min_unique=2)
    slots, _ = distributor.distribute(ratings)
    # 2nd slot of B (400/2 == 200) ties 3rd slot of A (600/3 == 200); B wins
    # because it holds fewer slots, so the fourth slot goes to B not A.
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"A": 2, "B": 2}


def test_null_rating_takes_top_priority_for_first_slot_only():
    ratings = pd.DataFrame({
        "Institution": ["A", "N", "B"],
        "Rating": [2000, pd.NA, 1000],
    })
    distributor = PrioritySlotDistributor(total_slots=2, max_slots=5, waiting_list_size=3, min_unique=1)
    slots, _ = distributor.distribute(ratings)
    # The single guaranteed slot goes to the never-rated institution, ahead of
    # the top-rated one. The remaining slot then follows normal priority.
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"N": 1, "A": 1, "B": 0}


def test_slot_sheet_reserves_first_timer_slots_and_sorts_by_total():
    slots = pd.DataFrame({
        "Institution": ["LOW", "HIGH", "NEW"],
        "Rating": [1000.0, 3000.0, float("nan")],
        "Slots": [1, 3, 1],
    })
    sheet = _build_slot_sheet(slots)
    # Highest total first; rated 1-slot team outranks the unrated 1-slot team.
    assert sheet["Institution"].tolist() == ["HIGH", "LOW", "NEW"]
    assert sheet["Total Slots"].tolist() == [3, 1, 1]
    new = sheet.set_index("Institution").loc["NEW"]
    assert new["General Slots"] == 0
    assert new["Reserved Slots"] == 1
    assert new["Explanation for Reserved Slots"] == "First-time participation"
    high = sheet.set_index("Institution").loc["HIGH"]
    assert high["General Slots"] == 3
    assert high["Reserved Slots"] == 0
    assert high["Explanation for Reserved Slots"] == ""


def test_null_rating_has_no_priority_after_first_slot():
    ratings = pd.DataFrame({
        "Institution": ["N", "A"],
        "Rating": [pd.NA, 10],
    })
    distributor = PrioritySlotDistributor(total_slots=3, max_slots=5, waiting_list_size=0, min_unique=2)
    slots, _ = distributor.distribute(ratings)
    # Both get their guaranteed first slot; the extra slot goes to A because a
    # null institution carries zero priority from its second slot onward.
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"N": 1, "A": 2}


def test_missing_institutions_generate_report_then_crash():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests"
        ratings = root / "ratings"
        inputs = root / "distribution-input"
        output = root / "distribution-output"
        parse(ROOT / "parser/input", contests)
        calculate(root, contests, ratings)
        create_real_inputs(inputs)
        with (inputs / "registered.txt").open("a") as file:
            file.write("\nUNIVERSITY OF DHAKAA\nMISSING UNIVERSITY\n")
        with pytest.raises(ValueError, match="missing.csv"):
            run(inputs, ratings, output)
        assert not (output / "slots.xlsx").exists()
        report = pd.read_csv(output / "missing.csv")
        assert report.columns.tolist() == [
            "Missing Institution",
            "Best Possible Match",
            "Probability",
        ]
        assert report["Missing Institution"].tolist() == [
            "MISSING UNIVERSITY",
            "UNIVERSITY OF DHAKAA",
        ]
        assert report.loc[1, "Best Possible Match"] == "UNIVERSITY OF DHAKA"
        assert report["Probability"].between(0, 100).all()


def test_institution_alias_resolves_before_missing_report():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contests = root / "contests"
        ratings = root / "ratings"
        inputs = root / "distribution-input"
        output = root / "distribution-output"
        parse(ROOT / "parser/input", contests)
        calculate(root, contests, ratings)
        create_real_inputs(inputs)
        (inputs / "registered.txt").write_text("BANGLADESH UNIVERSITY OF ENGINEERING & TECHNOLOGY\n")
        workbook = run(inputs, ratings, output)
        assert workbook.exists()


def test_example_input_directory_is_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        with pytest.raises(ValueError, match="Example inputs cannot be used"):
            run(
                ROOT / "slot_distributor/input/example",
                root / "ratings",
                root / "output",
            )
        assert not (root / "output").exists()


def test_missing_real_inputs_are_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        inputs = root / "distribution-input"
        inputs.mkdir()
        with pytest.raises(FileNotFoundError, match="registered.txt, options.json"):
            run(inputs, root / "ratings", root / "output")
        assert not (root / "output").exists()


def test_empty_registered_list_is_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        inputs = root / "distribution-input"
        create_real_inputs(inputs)
        (inputs / "registered.txt").write_text("")
        with pytest.raises(ValueError, match="does not contain any institutions"):
            run(inputs, root / "ratings", root / "output")
        assert not (root / "output").exists()
