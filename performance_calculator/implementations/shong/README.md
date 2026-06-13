# ShongPerformanceCalculator

For rank `r`, solved count `s`, and the contest maximum solved count `m`:

```text
maximum_team_rating
* (1 - rank_decay_rate)^(r - 1)
* (s / m)^solved_ratio_exponent
```

The default maximum is `4000`. Teams without a numeric rank are excluded.
