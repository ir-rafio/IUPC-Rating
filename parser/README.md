# Parser Module

## Flow

```text
input/contest_files + input/contests.json + input/options.json
-> selected Parser implementation
-> output contest database
```

## Files

- `model.py`: abstract `Parser` interface
- `__init__.py`: package exports
- `__main__.py`: enables `python -m parser`
- `records.py`: `Team` and `ParsedContest` records
- `service.py`: hashes sources, selects parsers, and updates changed contests
- `cli.py`: command-line entry point
- `implementations/__init__.py`: parser registry
- `implementations/common.py`: shared HTML row and warning helpers
- `implementations/baps/__init__.py`: BAPS implementation export
- `implementations/baps/parser.py`: BAPS parser implementation
- `implementations/baps/README.md`: BAPS parser documentation
- `implementations/toph/__init__.py`: Toph implementation export
- `implementations/toph/parser.py`: auto-detecting Toph parser implementation
- `implementations/toph/README.md`: Toph parser documentation
- `input/contests.json`: contest name, date, filenames, and parser
- `input/options.json`: `fail_on_warnings` behavior
- `input/contest_files/`: saved standings HTML
- `output/manifest.json`: source hashes, parser versions, and parse statistics
- `output/contests/`: one parsed JSON document per contest

## Parsers

- `BAPS`: parses BAPS standings
- `TOPH`: detects and parses supported older and current Toph layouts

Every parseable row is retained. Unofficial ranks such as `*` are stored as `null`.

## Command

```bash
iupc-parser
iupc-parser --force
iupc-parser --input path/to/input --output path/to/output
```
