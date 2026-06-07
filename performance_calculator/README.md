# Performance Calculator Module

## Flow

```text
parser/output/contests + input/options.json + institution_finder
-> selected PerformanceCalculator
-> output/performances.csv
```

This module calculates performance as a function of a team and contest. It loads every parsed contest and resolves each raw institution name through the institution finder. Every team is exported; teams without a numeric rank have an empty performance.

## Files

- `model.py`: abstract `PerformanceCalculator` interface
- `service.py`: contest loading, canonical-name resolution, and workflow
- `cli.py`: command-line entry point
- `implementations/`: performance calculator implementations
- `input/options.json`: selected calculator and parameters
- `output/performances.csv`: contest, team, canonical institution, and performance

## Command

```bash
iupc-performance-calculator
```
