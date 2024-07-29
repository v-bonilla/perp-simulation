from datetime import datetime
from typing import Iterator

import pandas as pd

from perp_simulation.constant import DataType
from perp_simulation.entity.ohlcv import OHLCV
from perp_simulation.gateway.data_service import DataProcessingService
from perp_simulation.gateway.historical_feather_repository import (
    HistoricalFeatherRepository,
)


class OHLCVRepository(HistoricalFeatherRepository):
    """Repository class for OHLCV data."""

    def __init__(self, data_base_path: str):
        _data_processing_service = DataProcessingService()
        super().__init__(data_base_path, DataType.OHLCV, _data_processing_service)

    def get_historical_dataframe(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> pd.DataFrame:
        """Get historical data from the Feather file."""
        self.logger.info(
            "Getting historical dataframe for %s from %s with timeframe %s",
            symbol,
            start_time,
            timeframe,
        )
        df = self._get_df(timeframe, symbol)
        self.logger.debug("Processing raw data")
        start_time_str = start_time.isoformat()
        df = self._data_processing_service.process_raw_data(
            df, start_time_str, timeframe
        )
        return df

    def get_historical_iterator(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> Iterator[OHLCV]:
        """Get historical data from the Feather file."""
        self.logger.info(
            "Getting historical iterator for %s from %s with timeframe %s",
            symbol,
            start_time,
            timeframe,
        )
        df = self.get_historical_dataframe(symbol, start_time, timeframe)
        # TODO: optimize. in freqtrade it is converted to python native objects to get a faster loop
        for index, values in df.iterrows():
            ohlcv = OHLCV(
                ts=int(index.timestamp()),
                symbol=symbol,
                open=values.open,
                high=values.high,
                low=values.low,
                close=values.close,
                volume=values.volume,
            )
            yield ohlcv
