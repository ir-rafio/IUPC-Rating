# ShongScoreCalculator

The calculator selects an institution's first `institution_team_limit` teams
in contest ranking order and combines their performances using a power mean:

```text
(mean(performance^rating_degree))^(1 / rating_degree)
```

The defaults select four teams and use a degree of `3.14159`.
