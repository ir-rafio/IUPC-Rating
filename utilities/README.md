# Utility Scripts

The utility commands update project inputs while validating duplicate names
and files.

## Files

- `__init__.py`: utility package definition
- `common.py`: JSON loading and atomic JSON writing
- `add_contest.py`: contest HTML, metadata, and credit maintenance
- `add_institution.py`: canonical institution maintenance
- `add_institution_alt_name.py`: alternate institution-name maintenance
- `README.md`: utility command documentation

## Add Contest

```bash
iupc-add-contest \
  --html path/to/standings.html \
  --name "Contest 2026" \
  --date 2026-06-01 \
  --parser TOPH \
  --credit 1
```

This copies the HTML file into `parser/input/contest_files/`, appends contest
metadata to `parser/input/contests.json`, and adds its credit to
`rating_calculator/input/credits.json`.

## Add Institution

```bash
iupc-add-institution --name "Example University"
```

This adds a canonical institution to
`institution_finder/data/institutions.json`.

## Add Institution Alternate Name

```bash
iupc-add-institution-alt-name \
  --institution "Example University" \
  --alt-name "Example University Alias"
```

The canonical institution must already exist. Alternate names must be unique
across the full database.
