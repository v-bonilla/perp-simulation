"""Data service module for data ingestion and processing."""

import logging
from pathlib import Path

import pandas as pd

from perp_simulation.constant import DataType, Timeframe


class FeatherRepository:
    """Service class to load raw data from a Feather file."""

    def __init__(self, data_path):
        self.logger = logging.getLogger(__name__)
        self._data_path = data_path

    def _get_feather_path(
        self, _data_type: str, _timeframe: str, _symbol_market: str
    ) -> Path:
        """Gets the path to the feather file for the given symbol_market, timeframe and data type.

        - Normalize symbol with underscores. Example: BTC-USDT:USDT -> BTC_USDT_USDT
        - Available data types are: "futures", "funding_rate", "mark".
        - Available timeframes are: "1m", "5m", "8h".
        """
        # Checks if the data type is valid
        if _data_type not in DataType.all():
            raise ValueError(f"Invalid data type: {_data_type}")

        # Checks if the timeframe is valid
        if _timeframe not in Timeframe.all():
            raise ValueError(f"Invalid timeframe: {_timeframe}")

        self.logger.debug(
            "Building file path for %s %s %s %s",
            self._data_path,
            _data_type,
            _timeframe,
            _symbol_market,
        )
        # Normalize symbol_market
        _symbol_market = _symbol_market.replace("-", "_")
        _symbol_market = _symbol_market.replace(":", "_")

        file_name = f"{_symbol_market}-{_timeframe}-{_data_type}.feather"
        feather_path = self._data_path / file_name

        self.logger.debug("Returning feather path: %s", feather_path)

        return feather_path

    def load(
        self, _data_type: str, _timeframe: str, _symbol_market: str
    ) -> pd.DataFrame:
        """Loads the raw data from a Feather file for the given symbol_market,
        timeframe and data type.
        """
        file_path = self._get_feather_path(_data_type, _timeframe, _symbol_market)
        self.logger.debug("Loading data from %s", file_path)
        df = pd.read_feather(file_path)
        self.logger.debug("Data loaded successfully")
        return df

    def store(
        self, _data_type: str, _timeframe: str, _symbol_market: str, _df: pd.DataFrame
    ):
        """Stores the data to a Feather file for the given symbol_market,
        timeframe and data type.
        """
        file_path = self._get_feather_path(_data_type, _timeframe, _symbol_market)
        self.logger.debug("Storing data to %s", file_path)
        _df.to_feather(file_path)
        self.logger.debug("Data stored successfully")


# TODO: think on use cases depending on timeframe and data type, and refactor
class DataProcessingService:
    """Service class to process raw data."""

    @staticmethod
    def index_raw_df(_df: pd.DataFrame) -> pd.DataFrame:
        """Indexes the raw data by date."""
        # Check that the index is not already the date
        if _df.index.name == "date":
            raise ValueError("The raw data is already indexed by date.")

        # Check that the date column is present
        if "date" not in _df.columns:
            raise ValueError("The date column is missing in the raw data.")

        if "datetime64" not in str(_df["date"].dtype):
            _df["date"] = pd.to_datetime(_df["date"])
        
        _df.set_index("date", inplace=True)
        return _df

    @staticmethod
    def since(_df: pd.DataFrame, _date: str) -> pd.DataFrame:
        """Filters the raw data since a given date."""
        # TODO: check that _date is a valid format
        # Check that index is of type datetime
        if "datetime64" not in str(_df.index.dtype):
            raise ValueError("The index of _df is not of type datetime.")

        # Check that _date is in the index
        if _date not in _df.index:
            raise ValueError(
                f"The date {_date} is not in _df. "
                "min date: {_df.index.min()}, max date: {_df.index.max()}"
            )

        _df = _df[_df.index >= _date]
        return _df

    @staticmethod
    def pct_change(_df: pd.DataFrame) -> pd.DataFrame:
        """Gets percentage change of data."""
        change_df = _df.pct_change()
        return change_df

    @staticmethod
    def validate_resample_to_args(_df: pd.DataFrame, _timeframe: str) -> pd.DataFrame:
        """Validates the arguments for resampling the data."""
        # Check that the index is of type datetime
        if "datetime64" not in str(_df.index.dtype):
            raise ValueError("The index of _df is not of type datetime.")

        # Check that the timeframe is valid
        if _timeframe not in Timeframe.all():
            raise ValueError(f"Invalid timeframe: {_timeframe}")

    @staticmethod
    def resample_to(_df: pd.DataFrame, _timeframe: str) -> pd.DataFrame:
        """Resamples the OHLCV data to a given timeframe."""
        DataProcessingService.validate_resample_to_args(_df, _timeframe)
        pd_tf = Timeframe.to_pd(_timeframe)
        # TODO: Get frequency from the index and skip resample if it's the same
        _df = _df.resample(pd_tf).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        return _df

    @staticmethod
    def process_raw_data(
        _df: pd.DataFrame, _since_date: str, _timeframe: str
    ) -> pd.DataFrame:
        """Processes the raw data."""
        _df = DataProcessingService.index_raw_df(_df)
        _df = DataProcessingService.since(_df, _since_date)
        _df = DataProcessingService.resample_to(_df, _timeframe)
        return _df


class FundingRateDataProcessingService(DataProcessingService):
    """Service class to process funding rate data."""

    @staticmethod
    def to_series(_df: pd.DataFrame) -> pd.Series:
        """Converts the OHLCV DataFrame to a Series.

        The funding rate timeseries is at the "open" column. The rest is zero.
        """
        if "open" not in _df.columns:
            raise ValueError("The 'open' column is missing in the raw data.")

        ser = _df["open"]
        ser = ser.rename("funding_rate")
        return ser

    @staticmethod
    def process_raw_data(
        _df: pd.DataFrame, _since_date: str, _timeframe: str
    ) -> pd.Series:
        """Processes the raw data."""
        _df = DataProcessingService.process_raw_data(_df, _since_date, _timeframe)
        _df = FundingRateDataProcessingService.to_series(_df)
        return _df
