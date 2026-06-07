from pathlib import Path

from institution_finder import InstitutionFinder


ROOT = Path(__file__).resolve().parents[1]


def test_resolves_canonical_and_alternate_names():
    finder = InstitutionFinder(ROOT / "institution_finder/data/institutions.json")
    canonical = "BANGLADESH UNIVERSITY OF ENGINEERING AND TECHNOLOGY"
    assert finder.resolve(canonical) == canonical
    assert finder.resolve("BANGLADESH UNIVERSITY OF ENGINEERING & TECHNOLOGY") == canonical
