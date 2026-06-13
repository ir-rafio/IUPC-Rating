# IUPC Rating

The **parser** converts saved contest standings into structured contest data.  
The **performance calculator** assigns a performance to every team in every
parsed contest.  
The **score calculator** combines team performances into an institution score for each contest.  
The **rating calculator** combines contest
scores using contest credits.  
The **slot distributor** allocates slots from the latest institution ratings.

The institution finder resolves institution names for the calculators and slot distributor. Contest metadata is always read from parser outputs.

## Installation

### Python

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[test]
```

### Anaconda

```bash
conda env create -f environment.yml
conda activate iupc-rating
```

`pyproject.toml` defines dependencies, packages, CLI commands, package data,
and test configuration. Editable installation with `-e` makes source changes
available without reinstalling.

## Run

```bash
iupc-parser
iupc-performance-calculator
iupc-score-calculator
iupc-rating-calculator
iupc-slot-distributor
```

Each calculator reads the previous module's output and reads contest metadata from parser outputs.

Before running the slot distributor, create
`slot_distributor/input/registered.txt` and
`slot_distributor/input/options.json`. Use the files under
`slot_distributor/input/example/` only as format references.

## Modules And Files

- `parser/`: HTML contest parsing module; see [parser/README.md](parser/README.md)
- `performance_calculator/`: team performance module; see [performance_calculator/README.md](performance_calculator/README.md)
- `score_calculator/`: institution contest score module; see [score_calculator/README.md](score_calculator/README.md)
- `rating_calculator/`: institution rating module; see [rating_calculator/README.md](rating_calculator/README.md)
- `slot_distributor/`: slot distribution module; see [slot_distributor/README.md](slot_distributor/README.md)
- `institution_finder/`: canonical institution and alternate-name lookup; see [institution_finder/README.md](institution_finder/README.md)
- `utilities/`: maintenance commands; see [utilities/README.md](utilities/README.md)
- `tests/`: automated test suite
- `pyproject.toml`: Python package, dependencies, commands, and test configuration
- `environment.yml`: Anaconda environment definition
- `LICENSE`: project license
- `README.md`: project overview and usage instructions

## Utility Commands

Add a contest:

```bash
iupc-add-contest \
  --html path/to/standings.html \
  --name "Contest 2026" \
  --date 2026-06-01 \
  --parser TOPH \
  --credit 1
```

Add an institution:

```bash
iupc-add-institution --name "Example University"
```

Add an alternate institution name:

```bash
iupc-add-institution-alt-name \
  --institution "Example University" \
  --alt-name "Example University Alias"
```

See [utilities/README.md](utilities/README.md) for validation and file-update details.
