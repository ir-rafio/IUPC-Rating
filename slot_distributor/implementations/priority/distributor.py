import heapq
import math

import pandas as pd

from slot_distributor.model import SlotDistributor


class PrioritySlotDistributor(SlotDistributor):
    def __init__(self, total_slots: int, max_slots: int, waiting_list_size: int, min_unique: int):
        self.total_slots = total_slots
        self.max_slots = max_slots
        self.waiting_list_size = waiting_list_size
        self.min_unique = min_unique

    def distribute(self, ratings: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        institutions = list(ratings["Institution"])
        original = dict(zip(ratings["Institution"], ratings["Rating"]))
        is_null = {institution: pd.isna(rating) for institution, rating in original.items()}
        values = {institution: 0 if pd.isna(rating) else int(rating) for institution, rating in original.items()}
        allocated = {institution: 0 for institution in institutions}

        def priority(institution: str) -> float:
            # Priority of granting the next slot, given how many are already held.
            next_slot = allocated[institution] + 1
            if is_null[institution]:
                # Never participated: top priority for the very first slot, none after.
                return math.inf if next_slot == 1 else 0.0
            return values[institution] / next_slot

        def entry(institution: str) -> tuple[float, int, str]:
            # Min-heap ordering: highest priority first, then fewest slots held, then name.
            return (-priority(institution), allocated[institution], institution)

        # Guarantee a first slot to the top `min_unique` institutions by priority.
        guarantee = min(self.min_unique, self.total_slots, len(institutions))
        first_choice = [(-priority(institution), institution) for institution in institutions]
        heapq.heapify(first_choice)
        for _ in range(guarantee):
            _, institution = heapq.heappop(first_choice)
            allocated[institution] = 1
        total_allocated = guarantee

        # Distribute the remaining slots by priority; institutions without a slot
        # still compete for their first one.
        heap = [entry(institution) for institution in institutions if allocated[institution] < self.max_slots]
        heapq.heapify(heap)
        while total_allocated < self.total_slots and heap:
            _, _, institution = heapq.heappop(heap)
            allocated[institution] += 1
            total_allocated += 1
            if allocated[institution] < self.max_slots:
                heapq.heappush(heap, entry(institution))

        slots = pd.DataFrame({
            "Institution": institutions,
            "Rating": [original[institution] for institution in institutions],
            "Slots": [allocated[institution] for institution in institutions],
        })

        waiting = []

        def record(institution: str, value: float) -> None:
            waiting.append({
                "Position": len(waiting) + 1,
                "Institution": institution,
                "Rating": original[institution],
                "Potential Slot Number": allocated[institution],
                "Priority": "MAX" if math.isinf(value) else value,
            })

        # Waiting list first serves institutions still without any slot.
        first_slot = [(-priority(institution), institution) for institution in institutions if allocated[institution] == 0]
        heapq.heapify(first_slot)
        while len(waiting) < self.waiting_list_size and first_slot:
            negative_priority, institution = heapq.heappop(first_slot)
            if allocated[institution] >= self.max_slots:
                continue
            allocated[institution] += 1
            record(institution, -negative_priority)

        # Once everyone has a (potential) first slot, continue by normal priority.
        heap = [entry(institution) for institution in institutions if allocated[institution] < self.max_slots]
        heapq.heapify(heap)
        while len(waiting) < self.waiting_list_size and heap:
            negative_priority, _, institution = heapq.heappop(heap)
            allocated[institution] += 1
            record(institution, -negative_priority)
            if allocated[institution] < self.max_slots:
                heapq.heappush(heap, entry(institution))

        return slots, pd.DataFrame(waiting, columns=[
            "Position",
            "Institution",
            "Rating",
            "Potential Slot Number",
            "Priority",
        ])
