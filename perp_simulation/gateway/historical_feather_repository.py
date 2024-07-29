import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pandas as pd

from perp_simulation.constant import DataType, Symbol, Timeframe
from perp_simulation.gateway.data_service import DataProcessingService


class HistoricalFeatherRepository:
    # TODO review docstring
    # TODO: think on use cases depending on timeframe and data type, and refactor
    def __init__(
        self,
        data_base_path: str,
        data_type: str,
        data_processing_service: DataProcessingService,
    ):
        # TODO from config
        self._data_base_path = Path(data_base_path)
        self._data_type = data_type
        self._data_processing_service = data_processing_service
        self.logger = logging.getLogger(__name__)

    def _get_data_path(self, timeframe: str, symbol: str) -> Path:
        """Gets the path to the feather file for the given symbol_market, timeframe and data type.

        - Normalize symbol with underscores. Example: BTC-USDT:USDT -> BTC_USDT_USDT
        - Available data types are: "futures", "funding_rate", "mark".
        - Available timeframes are: "1m", "5m", "8h".
        """
        # Checks if the data type is valid
        if self._data_type not in DataType.all():
            raise ValueError(f"Invalid data type: {self._data_type}")

        # Checks if the timeframe is valid
        if timeframe not in Timeframe.all():
            raise ValueError(f"Invalid timeframe: {timeframe}")

        self.logger.debug(
            "Building file path for %s %s %s %s",
            self._data_base_path,
            self._data_type,
            timeframe,
            symbol,
        )
        # Normalize symbol_market
        symbol = Symbol.normalize(symbol)

        file_name = f"{symbol}-{timeframe}-{self._data_type}.feather"
        feather_path = self._data_base_path / file_name

        self.logger.debug("Returning path: %s", feather_path)

        return feather_path

    def _load_data(self, path: Path) -> pd.DataFrame:
        """Load data from the Feather file."""
        self.logger.debug("Loading data from %s", path)
        _df = pd.read_feather(path)
        self.logger.debug("Data loaded successfully")
        return _df

    def _get_df(self, timeframe: str, symbol: str) -> pd.DataFrame:
        """Get the DataFrame from the Feather file."""
        self.logger.debug("Getting DataFrame for %s %s", timeframe, symbol)
        path = self._get_data_path(timeframe, symbol)
        self.logger.debug("Got path %s", path)
        _df = self._load_data(path)
        self.logger.debug("Loaded DataFrame with shape %s", _df.shape)
        return _df

    def get_historical_dataframe(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> pd.DataFrame:
        """Get historical data from the Feather file."""
        raise NotImplementedError

    def get_historical_data(
        self, symbol: str, start_time: datetime, timeframe: str
    ) -> Iterator:
        """Get historical data from the Feather file."""
        raise NotImplementedError
