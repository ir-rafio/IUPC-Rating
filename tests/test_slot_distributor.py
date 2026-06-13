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
            assert "Waiting List" in workbook_xml
            assert "Ratings" in workbook_xml


def test_waiting_list_continues_priority_sequence_and_allows_repeats():
    ratings = pd.DataFrame({
        "Institution": ["A", "B"],
        "Rating": [4000, 1000],
    })
    distributor = PrioritySlotDistributor(total_slots=2, max_slots=5, waiting_list_size=4)
    slots, waiting = distributor.distribute(ratings)
    assert dict(zip(slots["Institution"], slots["Slots"])) == {"A": 1, "B": 1}
    assert waiting["Institution"].tolist().count("A") > 1
    assert waiting["Position"].tolist() == [1, 2, 3, 4]


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
