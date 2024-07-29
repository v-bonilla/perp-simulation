from dataclasses import dataclass
from typing import Literal


@dataclass
class Trade:
    """
    Represents a trade in the trading system.
    """

    BUY = 1
    SELL = -1

    ts: int
    symbol: str
    type: Literal[
        1, -1
    ]  # BUY or SELL. TODO: make enum so it's accepted in the Literal exp
    quantity: float
    price: float
    fee: float

    @classmethod
    def from_dict(cls, data: dict) -> "Trade":
        """
        Creates a new trade from a dictionary.
        """
        return cls(**data)
