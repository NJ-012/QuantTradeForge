"""Common strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from quanttradeforge.data.models import Bar
from quanttradeforge.strategies.models import Signal


class Strategy(ABC):
    """Strategy contract independent of brokers and order management."""

    strategy_id: str
    version: str

    @abstractmethod
    def evaluate(self, bars: Sequence[Bar]) -> Signal:
        """Evaluate completed bars only and return one standardized signal."""
        raise NotImplementedError
