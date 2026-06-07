from abc import ABC, abstractmethod

import pandas as pd


class SlotDistributor(ABC):
    @abstractmethod
    def distribute(self, ratings: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        raise NotImplementedError
