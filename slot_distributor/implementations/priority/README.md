# PrioritySlotDistributor

Slots are assigned one at a time to the institution with the highest priority:

```text
priority = institution rating / next slot number
```

A never-rated institution (NULL rating, i.e. it has not appeared in any IUPC)
gets top priority for its **first** slot — ahead of even the highest-rated
institution — and zero priority for every slot after that.

When two institutions have equal priority, the one holding fewer slots so far
wins. For example, with ratings 600 and 400, the second slot of the 400 team
(`400 / 2 = 200`) outranks the third slot of the 600 team (`600 / 3 = 200`).

## Allocation

1. The first `min_unique` institutions, ranked by priority, are each guaranteed
   one slot.
2. The remaining slots are then distributed by priority. Institutions that were
   not in the guaranteed group still compete for their first slot
   (`rating / 1`), so a high-rated team may take extra slots before a low-rated
   team receives any.

## Waiting list

The same priority sequence continues to build the waiting list, with one
override: institutions that received **zero** slots are placed first, in
priority order, so everyone reaches their first slot before the list resumes
normal priority ordering. If organizers add `k` slots, the first `k`
waiting-list entries receive them. An institution may appear multiple times.

The `Priority` column shows `MAX` for a never-rated institution still waiting on
its first slot.

## Parameters

- `total_slots`: normal slot count
- `max_slots`: maximum slots per institution, including waiting-list entries
- `waiting_list_size`: maximum number of waiting-list entries
- `min_unique`: minimum number of distinct institutions guaranteed at least one
  slot (capped by `total_slots` and the number of registered institutions)

Select it with `"distributor": "PRIORITY"` in the slot distributor options.
