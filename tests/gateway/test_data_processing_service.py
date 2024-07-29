"""Tests for the data service module.

"""

import numpy as np
import pandas as pd
import pytest

from perp_simulation.constant import Timeframe
from perp_simulation.gateway.data_service import DataProcessingService


@pytest.fixture
def raw_ohlcv_df():
    """Create a sample OHLCV DataFrame for testing"""
    tf = Timeframe.to_pd(Timeframe.ONE_MIN)
    df = pd.DataFrame(
        {
            "date": pd.date_range(start="2022-01-01 00:00:00", periods=10, freq=tf),
            "open": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            "high": [150, 250, 350, 450, 550, 650, 750, 850, 950, 1050],
            "low": [50, 150, 250, 350, 450, 550, 650, 750, 850, 950],
            "close": [120, 220, 320, 420, 520, 620, 720, 820, 920, 1020],
            "volume": [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
        }
    )
    return df


def test_index_raw_df_with_valid_df(raw_ohlcv_df):
    """Test indexing a valid raw OHLCV DataFrame."""
    # Arrange
    data_service = DataProcessingService()

    # Act
    indexed_df = data_service.index_raw_df(raw_ohlcv_df)

    # Assert
    assert indexed_df.index.name == "date"
    assert indexed_df.index.dtype == "datetime64[ns]"
    assert indexed_df.columns.tolist() == ["open", "high", "low", "close", "volume"]


def test_index_raw_df_with_missing_date_column():
    """Test indexing a raw DataFrame with missing date column."""
    # Arrange
    data_service = DataProcessingService()
    df = pd.DataFrame({"value": [1, 2, 3]})

    # Act & Assert
    with pytest.raises(ValueError, match="The date column is missing in the raw data."):
        data_service.index_raw_df(df)


def test_index_raw_df_with_already_indexed_df(raw_ohlcv_df):
    """Test indexing a raw DataFrame that is already indexed by date."""
    # Arrange
    data_service = DataProcessingService()
    bad_df = raw_ohlcv_df.set_index("date")

    # Act & Assert
    with pytest.raises(ValueError, match="The raw data is already indexed by date."):
        data_service.index_raw_df(bad_df)


@pytest.fixture
def indexed_ohlcv_df(raw_ohlcv_df):
    """Create a sample indexed OHLCV DataFrame for testing"""
    df = raw_ohlcv_df.set_index("date", drop=True)
    return df


def test_since_with_valid_df(indexed_ohlcv_df):
    """Test filtering the raw data since a given date with a valid DataFrame."""
    # Arrange
    data_service = DataProcessingService()
    date = "2022-01-01 00:01:00"

    # Act
    filtered_df = data_service.since(indexed_ohlcv_df, date)

    # Assert
    assert filtered_df.index.name == "date"
    assert filtered_df.index.dtype == "datetime64[ns]"
    assert filtered_df.columns.tolist() == ["open", "high", "low", "close", "volume"]
    assert (filtered_df.index >= pd.to_datetime(date)).all()


def test_since_with_invalid_index_type(indexed_ohlcv_df):
    """Test filtering the raw data since a given date with a DataFrame that has an invalid index type."""
    # Arrange
    data_service = DataProcessingService()
    date = "2022-01-02"
    bad_df = indexed_ohlcv_df.reset_index()

    # Act & Assert
    with pytest.raises(ValueError, match="The index of _df is not of type datetime."):
        data_service.since(bad_df, date)


def test_since_with_missing_date(indexed_ohlcv_df):
    """Test filtering the raw data since a missing date."""
    # Arrange
    data_service = DataProcessingService()
    date = "2022-01-04"

    # Act & Assert
    with pytest.raises(ValueError, match="The date 2022-01-04 is not in _df."):
        data_service.since(indexed_ohlcv_df, date)


def test_resample_to_with_valid_df(indexed_ohlcv_df):
    """Test resampling the raw data to a given timeframe with a valid DataFrame."""
    # Arrange
    data_service = DataProcessingService()
    tf = Timeframe.FIVE_MIN

    # Act
    resampled_df = data_service.resample_to(indexed_ohlcv_df, tf)

    expected_index = pd.date_range(
        start="2022-01-01", periods=2, freq=Timeframe.to_pd(tf), name="date"
    )
    expected_df = pd.DataFrame(
        {
            "open": [100, 600],
            "high": [550, 1050],
            "low": [50, 550],
            "close": [520, 1020],
            "volume": [15000, 40000],
        },
        index=expected_index,
    )
    # Assert
    pd.testing.assert_frame_equal(resampled_df, expected_df)


def test_resample_to_with_invalid_index_type(indexed_ohlcv_df):
    """Test resampling the raw data to a given timeframe with a DataFrame that has an invalid index type."""
    # Arrange
    data_service = DataProcessingService()
    timeframe = Timeframe.ONE_HOUR
    bad_df = indexed_ohlcv_df.reset_index()

    # Act & Assert
    with pytest.raises(ValueError, match="The index of _df is not of type datetime."):
        data_service.resample_to(bad_df, timeframe)


def test_resample_to_with_invalid_timeframe(indexed_ohlcv_df):
    """Test resampling the raw data to an invalid timeframe."""
    # Arrange
    data_service = DataProcessingService()
    timeframe = "1M"

    # Act & Assert
    with pytest.raises(ValueError, match=f"Invalid timeframe: {timeframe}"):
        data_service.resample_to(indexed_ohlcv_df, timeframe)


def test_pct_change_with_valid_df(indexed_ohlcv_df):
    """Test calculating percentage change of OHLCV data with a valid DataFrame."""
    # Arrange
    data_service = DataProcessingService()

    # Act
    change_df = data_service.pct_change(indexed_ohlcv_df)

    # Assert
    expected_df = indexed_ohlcv_df / indexed_ohlcv_df.shift(1) - 1
    pd.testing.assert_frame_equal(change_df, expected_df)
