# ShongRatingCalculator

At every rating-history point, older contest credits are reduced:

```text
effective_credit
= contest_credit
* (1 - time_decay_rate)^elapsed_periods
```

Institution contest scores are combined using a credit-weighted root mean
square:

```text
sqrt(sum((score * effective_credit)^2) / sum(effective_credit^2))
```

Contests without a score for the institution are excluded.
