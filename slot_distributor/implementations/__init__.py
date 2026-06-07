from .priority import PrioritySlotDistributor
from slot_distributor.model import SlotDistributor


def get_distributor(name: str, parameters: dict) -> SlotDistributor:
    distributors = {
        "PRIORITY": PrioritySlotDistributor,
    }
    try:
        return distributors[name.upper()](**parameters)
    except KeyError as error:
        raise ValueError(f"Unknown slot distributor: {name}") from error


__all__ = ["SlotDistributor", "get_distributor"]
