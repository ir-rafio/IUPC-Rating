# Institution Finder Module

The institution finder owns the canonical institution database and resolves canonical names and alternate names.

## Files

- `__init__.py`: exports `InstitutionFinder`
- `finder.py`: `InstitutionFinder` resolution and fuzzy matching
- `data/institutions.json`: canonical institution names and alternate names
- `README.md`: module documentation

## Usage

```python
from pathlib import Path
from institution_finder import InstitutionFinder

finder = InstitutionFinder(Path("institution_finder/data/institutions.json"))
canonical = finder.resolve("University Alias")
suggestion, probability = finder.best_match("Misspelled University")
```
