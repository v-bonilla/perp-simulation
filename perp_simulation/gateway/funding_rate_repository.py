import math
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pandas as pd

from perp_simulation.constant import DataType, Timeframe
from perp_simulation.entity.funding_rate import FundingRate
from perp_simulation.gateway.data_service import FundingRateDataProcessingService
from perp_simulation.gateway.historical_feather_repository import (
    HistoricalFeatherRepository,
)


class FundingRateRepository(HistoricalFeatherRepository):
    """Repository class for funding rate data."""

    def __init__(self, data_base_path: str):
        _data_processing_service = FundingRateDataProcessingService()
        super().__init__(
            data_base_path, DataType.FUNDING_RATE, _data_processing_service
        )

    def _get_data_path(self, timeframe: str, symbol: str) -> Path:
        # TODO: review this architecture
        return super()._get_data_path(Timeframe.EIGHT_HOUR, symbol)

    def get_historical_dataframe(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> pd.DataFrame:
        """Get historical data from the Feather file."""
        # TODO: implement
        pass

    def get_historical_data(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> Iterator[FundingRate]:
        """Get historical data from the Feather file."""
        self.logger.info(
            "Getting historical data for %s from %s with timeframe %s",
            symbol,
            start_time,
            timeframe,
        )
        df = self._get_df(timeframe, symbol)
        self.logger.debug("Processing raw data")
        start_time_str = start_time.isoformat()
        ser = self._data_processing_service.process_raw_data(
            df, start_time_str, timeframe
        )
        # TODO: optimize. in freqtrade it is converted to python native objects to get a faster loop
        for index, value in ser.items():
            funding_rate = FundingRate(
                ts=int(index.timestamp()),
                symbol=symbol,
                rate=value if not math.isnan(value) else None,
            )
            yield funding_rate
