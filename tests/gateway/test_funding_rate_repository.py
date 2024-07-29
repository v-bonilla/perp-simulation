# pylint: disable=redefined-outer-name
from datetime import datetime, timezone

import pytest

from perp_simulation.constant import Symbol, Timeframe
from perp_simulation.gateway.funding_rate_repository import FundingRateRepository
from tests.gateway.util import create_test_feather_files

TEST_DATA_BASE_PATH = "./tests/data"


@pytest.mark.skip("Use to create test files")
def test_create_ohlcv_test_data():
    date_column = "date"
    from_ts = "2024-01-22 00:00:00"
    to_ts = "2024-01-23 00:00:00"
    from_ts_file_name_str = from_ts.replace(" ", "T").replace(":", "").replace("-", "")
    to_ts_file_name_str = to_ts.replace(" ", "T").replace(":", "").replace("-", "")
    original_file_path = "./data/binance-futures/BTC_USDT_USDT-1m-futures.feather"
    new_file_name = f"BTC_USDT_USDT-1m-futures_{from_ts_file_name_str}_{to_ts_file_name_str}.feather"
    new_file_path = f"{TEST_DATA_BASE_PATH}/binance-futures/{new_file_name}"
    create_test_feather_files(
        original_file_path=original_file_path,
        new_file_path=new_file_path,
        date_column=date_column,
        from_ts=from_ts,
        to_ts=to_ts,
    )


@pytest.mark.skip("Use to create test files")
def test_create_funding_rate_test_data():
    date_column = "date"
    from_ts = "2024-01-22 00:00:00"
    to_ts = "2024-01-23 00:00:00"
    from_ts_file_name_str = from_ts.replace(" ", "T").replace(":", "").replace("-", "")
    to_ts_file_name_str = to_ts.replace(" ", "T").replace(":", "").replace("-", "")
    original_file_path = "./data/binance-futures/BTC_USDT_USDT-8h-funding_rate.feather"
    new_file_name = f"BTC_USDT_USDT-8h-funding_rate_{from_ts_file_name_str}_{to_ts_file_name_str}.feather"
    new_file_path = f"{TEST_DATA_BASE_PATH}/binance-futures/{new_file_name}"
    create_test_feather_files(
        original_file_path=original_file_path,
        new_file_path=new_file_path,
        date_column=date_column,
        from_ts=from_ts,
        to_ts=to_ts,
    )


@pytest.fixture
def funding_rate_historical_feather_repository() -> FundingRateRepository:
    repository = FundingRateRepository(
        data_base_path=f"{TEST_DATA_BASE_PATH}/binance-futures",
    )
    return repository


def test_get_historical_data_funding_rate_8h_five_bars(
    funding_rate_historical_feather_repository: FundingRateRepository,
):
    """Get historical funding rate, 8h, five bars of data.

    Test data is closed left and open right (last datapoint is 2024-01-22 16:00:00).
    """
    symbol = Symbol.BTCUSD
    timeframe = Timeframe.EIGHT_HOUR
    start_date = datetime(2024, 1, 22, 8, tzinfo=timezone.utc)
    iterator = funding_rate_historical_feather_repository.get_historical_data(
        symbol=symbol, start_time=start_date, timeframe=timeframe
    )
    data = list(iterator)
    assert len(data) == 2
    assert data[0].ts == start_date.timestamp()
