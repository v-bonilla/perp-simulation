from pathlib import Path

import pandas as pd
import pytest

from perp_simulation.constant import DataType, Timeframe
from perp_simulation.gateway.data_service import FeatherRepository


@pytest.fixture
def feather_repository(tmp_path):
    """Create a FeatherRepository instance for testing"""
    return FeatherRepository(tmp_path)


def test_get_feather_path(feather_repository):
    """Test getting the path to the feather file"""
    # Arrange
    data_type = DataType.OHLCV
    timeframe = Timeframe.ONE_MIN
    symbol_market = "BTC-USDT:USDT"
    expected_path = feather_repository._data_path / "BTC_USDT_USDT-1m-futures.feather"

    # Act
    feather_path = feather_repository._get_feather_path(
        data_type, timeframe, symbol_market
    )

    # Assert
    assert feather_path == expected_path


def test_get_feather_path_with_invalid_data_type(feather_repository):
    """Test getting the path to the feather file with an invalid data type"""
    # Arrange
    data_type = "invalid"
    timeframe = Timeframe.ONE_MIN
    symbol_market = "BTC-USDT:USDT"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid data type: invalid"):
        feather_repository._get_feather_path(data_type, timeframe, symbol_market)


def test_get_feather_path_with_invalid_timeframe(feather_repository):
    """Test getting the path to the feather file with an invalid timeframe"""
    # Arrange
    data_type = DataType.OHLCV
    timeframe = "invalid"
    symbol_market = "BTC-USDT:USDT"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid timeframe: invalid"):
        feather_repository._get_feather_path(data_type, timeframe, symbol_market)


def test_load(feather_repository, mocker):
    """Test loading data from a Feather file"""
    # Arrange
    data_type = DataType.OHLCV
    timeframe = Timeframe.ONE_MIN
    symbol_market = "BTC-USDT:USDT"
    file_path = Path("/path/to/data/BTC_USDT_USDT-1m-futures.feather")
    expected_df = pd.DataFrame({"value": [1, 2, 3]})

    mocker.patch("pandas.read_feather", return_value=expected_df)

    # Act
    df = feather_repository.load(data_type, timeframe, symbol_market)

    # Assert
    assert df.equals(expected_df)


def test_store(feather_repository, mocker):
    """Test storing data to a Feather file"""
    # Arrange
    data_type = DataType.OHLCV
    timeframe = Timeframe.ONE_MIN
    symbol_market = "BTC-USDT:USDT"
    file_path = feather_repository._data_path / "BTC_USDT_USDT-1m-futures.feather"
    df = pd.DataFrame({"value": [1, 2, 3]})

    mocker.patch("pandas.DataFrame.to_feather")

    # Act
    feather_repository.store(data_type, timeframe, symbol_market, df)

    # Assert
    pd.DataFrame.to_feather.assert_called_once_with(file_path)
