# Rating Calculator Module

## Flow

```text
score_calculator/output/score_history.csv
+ parser/output/contests + input/credits.json + input/options.json + institution_finder
-> selected RatingCalculator
-> output/latest_ratings.csv + output/ratings_history.csv + output/rating_rank_history.csv
```

This module calculates rating as a function of an institution. Credits in
`input/credits.json` select contests and control their influence. Contest
dates are read from parser outputs. Missing selected contest metadata or
scores cause an error.

## Files

- `model.py`: abstract `RatingCalculator` interface
- `service.py`: score loading, canonical-name resolution, and workflow
- `cli.py`: command-line entry point
- `implementations/`: rating calculator implementations
- `input/credits.json`: selected contests and credits
- `input/options.json`: selected calculator and parameters
- `output/latest_ratings.csv`: latest institution ratings
- `output/ratings_history.csv`: institution rating after each contest
- `output/rating_rank_history.csv`: institution rating rank after each contest

## Command

```bash
iupc-rating-calculator
```
