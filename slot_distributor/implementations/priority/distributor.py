import heapq

import pandas as pd

from slot_distributor.model import SlotDistributor


class PrioritySlotDistributor(SlotDistributor):
    def __init__(self, total_slots: int, max_slots: int, waiting_list_size: int):
        self.total_slots = total_slots
        self.max_slots = max_slots
        self.waiting_list_size = waiting_list_size

    def distribute(self, ratings: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        values = dict(zip(ratings["Institution"], ratings["Rating"].fillna(0).astype(int)))
        allocated = {institution: 1 for institution in values}
        heap = [(-rating / 2, institution) for institution, rating in values.items()]
        heapq.heapify(heap)
        total_allocated = len(allocated)

        while total_allocated < self.total_slots and heap:
            _, institution = heapq.heappop(heap)
            if allocated[institution] >= self.max_slots:
                continue
            allocated[institution] += 1
            total_allocated += 1
            heapq.heappush(heap, (-values[institution] / (allocated[institution] + 1), institution))

        slots = pd.DataFrame({
            "Institution": allocated.keys(),
            "Rating": values.values(),
            "Slots": allocated.values(),
        })
        waiting = []
        while len(waiting) < self.waiting_list_size and heap:
            negative_priority, institution = heapq.heappop(heap)
            if allocated[institution] >= self.max_slots:
                continue
            allocated[institution] += 1
            waiting.append({
                "Position": len(waiting) + 1,
                "Institution": institution,
                "Rating": values[institution],
                "Potential Slot Number": allocated[institution],
                "Priority": -negative_priority,
            })
            heapq.heappush(heap, (-values[institution] / (allocated[institution] + 1), institution))
        return slots, pd.DataFrame(waiting, columns=[
            "Position",
            "Institution",
            "Rating",
            "Potential Slot Number",
            "Priority",
        ])
