# PrioritySlotDistributor

Every registered institution receives one slot. Remaining slots are assigned
one at a time to the institution with the highest priority:

```text
priority = institution rating / next slot number
```

After normal allocation, the same priority sequence continues to create a
waiting list. If organizers add `k` slots, the first `k` waiting-list entries
receive them. An institution may appear multiple times.

Parameters:

- `total_slots`: normal slot count
- `max_slots`: maximum slots per institution, including waiting-list entries
- `waiting_list_size`: maximum number of waiting-list entries

Select it with `"distributor": "PRIORITY"` in the slot distributor options.
