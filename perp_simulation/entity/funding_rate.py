from dataclasses import dataclass


@dataclass
class FundingRate:
    """
    Represents a funding rate in the trading system.
    """

    ts: int
    symbol: str
    rate: float
