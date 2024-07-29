"""Define the constant variables used in the project."""

from typing import List


class Symbol:
    """Define the symbols of the data source."""

    BTCUSD = "BTC/USDT:USDT"
    ETHUSD = "ETH/USDT:UDST"

    @staticmethod
    def all() -> List[str]:
        """Return all available symbols."""
        return [Symbol.BTCUSD, Symbol.ETHUSD]
    
    @staticmethod
    def normalize(symbol: str) -> str:
        """Normalize the symbol."""
        return symbol.replace("/", "_").replace(":", "_")


class DataType:
    """Define the data type of the data source."""

    OHLCV = "futures"
    FUNDING_RATE = "funding_rate"
    MARK_PRICE = "mark"

    @staticmethod
    def all() -> List[str]:
        """Return all available data types."""
        return [DataType.OHLCV, DataType.FUNDING_RATE, DataType.MARK_PRICE]


class Timeframe:
    """Define the timeframe of the data source."""

    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    ONE_HOUR = "1h"
    EIGHT_HOUR = "8h"

    @staticmethod
    def to_seconds(t: str) -> int:
        """Convert the timeframe to seconds."""
        timeframe_to_sec = {"1m": 60, "5m": 5 * 60, "1h": 60 * 60, "8h": 60 * 60 * 8}
        return timeframe_to_sec[t]

    @staticmethod
    def to_pd(t: str) -> str:
        """Convert the timeframe to a Pandas-compatible timeframe string."""
        # TODO: warning: T for minute is going to be deprecated
        return t.replace("m", "T").replace("h", "H")

    @staticmethod
    def all() -> List[str]:
        """Return all available timeframes."""
        return [
            Timeframe.ONE_MIN,
            Timeframe.FIVE_MIN,
            Timeframe.ONE_HOUR,
            Timeframe.EIGHT_HOUR,
        ]


BINANCE_FUTURES_TAKER_FEE_PCT = 0.0005
BINANCE_FUTURES_BTC_LEVERAGE = 125
BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE = 0.004
BINANCE_FUTURES_BTC_FUNDING_RATE_FREQ = Timeframe.EIGHT_HOUR
