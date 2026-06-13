# Score Calculator Module

## Flow

```text
performance_calculator/output/performances.csv
+ parser/output/contests + input/options.json + institution_finder
-> selected ScoreCalculator
-> output/score_history.csv + output/score_rank_history.csv
```

This module calculates score as a function of an institution and contest.
It reads the contest list and dates from parser outputs. Missing contest
performances cause an error. Team performance rows retain contest ranking
order, allowing calculators to select the top teams.

## Files

- `model.py`: abstract `ScoreCalculator` interface
- `service.py`: performance loading, canonical-name resolution, and workflow
- `cli.py`: command-line entry point
- `implementations/`: score calculator implementations
- `input/options.json`: selected calculator and parameters
- `output/score_history.csv`: institution scores in selected contests
- `output/score_rank_history.csv`: institution score ranks in selected contests

## Command

```bash
iupc-score-calculator
```
