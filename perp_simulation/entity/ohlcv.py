from dataclasses import dataclass


@dataclass
class OHLCV:
    """
    Represents an OHLCV (Open, High, Low, Close, Volume) data point.
    """

    ts: int
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
