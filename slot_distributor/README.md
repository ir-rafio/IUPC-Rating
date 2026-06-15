# Slot Distributor Module

## Flow

```text
rating_calculator/output/latest_ratings.csv + input/registered.txt + input/options.json
-> selected SlotDistributor implementation
-> output/slots.xlsx
```

Registered institution names are first checked directly against
`latest_ratings.csv`.
If direct matching fails, the institution finder resolves alternate names.
A name that resolves to a known institution but has no rating yet is kept with
a NULL rating (it never participated in an IUPC). Only names that do not match
any institution in the database produce `output/missing.csv` with fuzzy
suggestions and then stop execution, so they can be triaged as typos or added
to the institution database.

The files under `input/example/` only document the required formats. The
distributor rejects that directory. It requires real `input/registered.txt`
and `input/options.json` files and stops before touching outputs when either
file is missing or the registered-institution list is empty.

## Files

- `model.py`: abstract `SlotDistributor` interface
- `__init__.py`: package exports
- `__main__.py`: enables `python -m slot_distributor`
- `service.py`: registered-name validation, fuzzy report, and workflow
- `exporter.py`: Excel workbook writer
- `cli.py`: command-line entry point
- `implementations/__init__.py`: distributor registry
- `implementations/priority/__init__.py`: priority implementation export
- `implementations/priority/distributor.py`: priority distributor implementation
- `implementations/priority/README.md`: priority distributor documentation
- `input/example/registered.txt`: non-executable registered-list format reference
- `input/example/options.json`: non-executable options format reference
- `input/registered.txt`: registered institutions
- `input/options.json`: distributor and parameters
- `../institution_finder/data/institutions.json`: canonical and alternate names
- `output/slots.xlsx`: slot allocation, waiting list, and ratings workbook
- `output/missing.csv`: missing-name report generated on failure

## Command

```bash
iupc-slot-distributor
iupc-slot-distributor \
  --input path/to/input \
  --ratings path/to/rating-output \
  --output path/to/output
```

The path passed to `--input` must contain actual inputs and cannot be an
`example` directory.
