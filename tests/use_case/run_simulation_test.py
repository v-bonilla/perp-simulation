# pylint: disable=redefined-outer-name,invalid-name
from datetime import datetime
from typing import Callable, Iterator

import pytest

from perp_simulation.constant import Symbol, Timeframe
from perp_simulation.entity.account import Account
from perp_simulation.entity.account_snapshot import AccountSnapshot
from perp_simulation.entity.funding_rate import FundingRate
from perp_simulation.entity.ohlcv import OHLCV
from perp_simulation.entity.position import Position
from perp_simulation.entity.simulation import Simulation
from perp_simulation.entity.trade import Trade
from perp_simulation.use_case.liquidate_positions import LiquidatePositions
from perp_simulation.use_case.make_account_snapshot import MakeAccountSnapshot
from perp_simulation.use_case.open_cross_margin_position import OpenCrossMarginPosition
from perp_simulation.use_case.run_simulation import RunSimulation
from perp_simulation.use_case.settle_funding_rate_costs import SettleFundingRateCosts
from perp_simulation.use_case.update_position_effective_leverage import (
    UpdatePositionEffectiveLeverage,
)
from perp_simulation.use_case.update_position_initial_margin import (
    UpdatePositionInitialMargin,
)
from perp_simulation.use_case.update_position_liquidation_price import (
    UpdatePositionLiquidationPrice,
)
from perp_simulation.use_case.update_position_maintenance_margin import (
    UpdatePositionMaintenanceMargin,
)
from perp_simulation.use_case.update_position_unrealized_pnl import (
    UpdatePositionUnrealizedPnl,
)


def create_ohlcv_iterator(
    start_ts: int,
    end_ts: int,
    timeframe: str,
    price_start: float,
    price_pct_change: float,
    price_pct_variance: float,
) -> Iterator[OHLCV]:
    # Adding first bar
    ohlcv_data = [
        OHLCV(
            ts=start_ts,
            symbol=Symbol.BTCUSD,
            open=price_start,
            high=price_start + price_pct_variance * price_start,
            low=price_start - price_pct_variance * price_start,
            close=price_start + price_pct_change * price_start,
            volume=10.0,
        )
    ]
    # Looping from second bar
    period_seconds = Timeframe.to_seconds(timeframe)
    second_bar_ts = int(start_ts + period_seconds)
    last_bar_ts = int(end_ts)
    for ts in range(second_bar_ts, last_bar_ts, period_seconds):
        prev_ohlcv = ohlcv_data[-1]
        ohlcv = OHLCV(
            ts=ts,
            symbol=Symbol.BTCUSD,
            open=prev_ohlcv.close,
            high=prev_ohlcv.close + price_pct_variance * prev_ohlcv.close,
            low=prev_ohlcv.close - price_pct_variance * prev_ohlcv.close,
            close=prev_ohlcv.close + price_pct_change * prev_ohlcv.close,
            volume=10.0,
        )
        ohlcv_data.append(ohlcv)
    return iter(ohlcv_data)


@pytest.fixture
def create_mocked_run_simulation_use_case(
    mocker,
) -> Callable[[Iterator[OHLCV], Iterator[FundingRate]], RunSimulation]:
    def _factory(ohlcv_iterator, funding_rate_iterator):
        # Mocks. To add the returning value in the test.
        ohlcv_repository = mocker.Mock()
        ohlcv_repository.get_historical_data.return_value = ohlcv_iterator
        funding_rate_repository = mocker.Mock()
        funding_rate_repository.get_historical_data.return_value = funding_rate_iterator

        update_position_initial_margin_use_case = UpdatePositionInitialMargin()
        update_position_maintenance_margin_use_case = UpdatePositionMaintenanceMargin()
        update_position_effective_leverage_use_case = UpdatePositionEffectiveLeverage()
        update_position_liquidation_price_use_case = UpdatePositionLiquidationPrice()
        update_position_unrealized_pnl_use_case = UpdatePositionUnrealizedPnl()
        open_cross_margin_position_use_case = OpenCrossMarginPosition(
            update_position_initial_margin_use_case=update_position_initial_margin_use_case,
            update_position_maintenance_margin_use_case=update_position_maintenance_margin_use_case,
            update_position_effective_leverage_use_case=update_position_effective_leverage_use_case,
            update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
        )
        liquidate_position_use_case = LiquidatePositions(
            update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
            update_position_unrealized_pnl_use_case=update_position_unrealized_pnl_use_case,
        )
        run_simulation_use_case = RunSimulation(
            ohlcv_repository=ohlcv_repository,
            funding_rate_repository=funding_rate_repository,
            open_cross_margin_position_use_case=open_cross_margin_position_use_case,
            settle_funding_rate_costs_use_case=SettleFundingRateCosts(),
            update_position_unrealized_pnl_use_case=UpdatePositionUnrealizedPnl(),
            update_position_initial_margin_use_case=update_position_initial_margin_use_case,
            update_position_maintenance_margin_use_case=update_position_maintenance_margin_use_case,
            update_position_effective_leverage_use_case=update_position_effective_leverage_use_case,
            update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
            liquidate_position_use_case=liquidate_position_use_case,
            make_account_snapshot_use_case=MakeAccountSnapshot(),
        )
        return run_simulation_use_case

    return _factory


@pytest.fixture
def ohlcv_btc_20240122T075000_20240122T075500_1min_price_decrease_iterator():
    # TODO: Change to UTC
    start_ts = datetime.fromisoformat("2024-01-22T07:50:00").timestamp()
    end_ts = datetime.fromisoformat("2024-01-22T07:55:00").timestamp()
    timeframe = Timeframe.ONE_MIN
    price_start = 50000.0
    price_pct_change = -0.001
    price_pct_variance = 0.0005
    ohlcv_data = create_ohlcv_iterator(
        start_ts, end_ts, timeframe, price_start, price_pct_change, price_pct_variance
    )
    return ohlcv_data


@pytest.fixture
def ohlcv_btc_20240122T075800_20240122T080200_1min_price_decrease_iterator():
    # TODO: Change to UTC
    start_ts = datetime.fromisoformat("2024-01-22T07:58:00").timestamp()
    end_ts = datetime.fromisoformat("2024-01-22T08:03:00").timestamp()
    timeframe = Timeframe.ONE_MIN
    price_start = 50000.0
    price_pct_change = -0.001
    price_pct_variance = 0.0005
    ohlcv_data = create_ohlcv_iterator(
        start_ts, end_ts, timeframe, price_start, price_pct_change, price_pct_variance
    )
    return ohlcv_data


@pytest.fixture
def funding_rate_btc_20240122T075000_20240122T081000_1min_iterator():
    funding_rate_data = [
        FundingRate(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T08:00:00").timestamp(),
            symbol=Symbol.BTCUSD,
            rate=0.0001,
        )
    ]
    return iter(funding_rate_data)


@pytest.fixture
def expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd():
    account_snapshots = [
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:51:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            # TODO: Change to UTC
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.5,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:52:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            # TODO: Change to UTC
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.999499999999971,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:53:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            # TODO: Change to UTC
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.4985004999999365,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:54:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            # TODO: Change to UTC
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.9970019994999166,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:55:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            # TODO: Change to UTC
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-2.4950049975004367,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
    ]
    simulation = Simulation(
        name="2024-01-22T07-50-00_2024-01-22T07-55-00_1m_BTC_USDT_USDT",
        # TODO: Change to UTC
        simulation_start_ts=datetime.fromisoformat("2024-01-22T07:50:00").timestamp(),
        simulation_end_ts=datetime.fromisoformat("2024-01-22T07:55:00").timestamp(),
        timeframe=Timeframe.ONE_MIN,
        symbol=Symbol.BTCUSD,
        account_snapshots=account_snapshots,
    )
    return simulation


def test_run_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd(
    ohlcv_btc_20240122T075000_20240122T075500_1min_price_decrease_iterator: Iterator[
        OHLCV
    ],
    funding_rate_btc_20240122T075000_20240122T081000_1min_iterator: Iterator[
        FundingRate
    ],
    create_mocked_run_simulation_use_case: Callable[
        [Iterator[OHLCV], Iterator[FundingRate]], RunSimulation
    ],
    account_100_long_500usd: Account,
    expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd: Simulation,
):
    """Run a simulation with five bars of data, open position."""
    # Test
    run_simulation_use_case = create_mocked_run_simulation_use_case(
        ohlcv_btc_20240122T075000_20240122T075500_1min_price_decrease_iterator,
        funding_rate_btc_20240122T075000_20240122T081000_1min_iterator,
    )
    # TODO: Change to UTC
    start_time = datetime.fromisoformat("2024-01-22T07:50:00")
    end_time = datetime.fromisoformat("2024-01-22T07:55:00")
    timeframe = Timeframe.ONE_MIN
    symbol = Symbol.BTCUSD
    result_simulation = run_simulation_use_case.run(
        start_time, end_time, timeframe, symbol, account_100_long_500usd
    )

    # Assert
    assert (
        result_simulation.name
        == expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.name
    )
    assert (
        result_simulation.simulation_start_ts
        == expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.simulation_start_ts
    )
    assert (
        result_simulation.simulation_end_ts
        == expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.simulation_end_ts
    )
    assert (
        result_simulation.timeframe
        == expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.timeframe
    )
    assert (
        result_simulation.symbol
        == expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.symbol
    )
    assert len(result_simulation.account_snapshots) == len(
        expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.account_snapshots
    )
    for i, snapshot in enumerate(result_simulation.account_snapshots):
        expected_snapshot = expected_simulation_20240122T075000_20240122T075500_1min_account_100_long_500usd.account_snapshots[
            i
        ]
        assert snapshot.ts == expected_snapshot.ts
        assert snapshot.account.balance == expected_snapshot.account.balance
        assert len(snapshot.account.positions) == len(
            expected_snapshot.account.positions
        )
        for j, position in enumerate(snapshot.account.positions):
            expected_position = expected_snapshot.account.positions[j]
            # assert position.open_ts == expected_position.open_ts  # This is a detail for now
            assert position.symbol == expected_position.symbol
            assert position.side == expected_position.side
            assert position.quantity == expected_position.quantity
            assert position.entry_price == expected_position.entry_price
            assert position.avg_price == expected_position.avg_price
            # assert position.trade.ts == expected_position.trade.ts  # This is a detail for now
            assert position.trade.symbol == expected_position.trade.symbol
            assert position.trade.type == expected_position.trade.type
            assert position.trade.quantity == expected_position.trade.quantity
            assert position.trade.price == expected_position.trade.price
            assert position.trade.fee == expected_position.trade.fee
            assert position.unrealized_pnl == expected_position.unrealized_pnl
            assert position.funding_rate_costs == expected_position.funding_rate_costs
            assert position.initial_margin == expected_position.initial_margin
            assert position.maintenance_margin == expected_position.maintenance_margin
            assert position.effective_leverage == expected_position.effective_leverage
            assert position.liquidation_price == expected_position.liquidation_price


@pytest.fixture
def expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd():
    account_snapshots = [
        AccountSnapshot(
            # TODO: Change to UTC
            ts=datetime.fromisoformat("2024-01-22T07:51:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        # TODO: Change to UTC
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.5,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:52:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.999499999999971,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:53:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.4985004999999365,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:54:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:49:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:49:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.9970019994999166,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:55:00").timestamp(),
            account=Account(
                balance=1.5049950024995633,
                positions=[],
            ),
        ),
    ]
    simulation = Simulation(
        name="2024-01-22T07-50-00_2024-01-22T07-55-00_1m_BTC_USDT_USDT",
        simulation_start_ts=datetime.fromisoformat("2024-01-22T07:50:00").timestamp(),
        simulation_end_ts=datetime.fromisoformat("2024-01-22T07:55:00").timestamp(),
        timeframe=Timeframe.ONE_MIN,
        symbol=Symbol.BTCUSD,
        account_snapshots=account_snapshots,
    )
    return simulation


def test_run_simulation_20240122T075000_20240122T075500_1min_account_3_long_500usd(
    ohlcv_btc_20240122T075000_20240122T075500_1min_price_decrease_iterator: Iterator[
        OHLCV
    ],
    funding_rate_btc_20240122T075000_20240122T081000_1min_iterator: Iterator[
        FundingRate
    ],
    create_mocked_run_simulation_use_case: Callable[
        [Iterator[OHLCV], Iterator[FundingRate]], RunSimulation
    ],
    account_100_long_500usd: Account,
    expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd: Simulation,
):
    """Run a simulation with five bars of data, open position, liquidate position."""
    # Test
    run_simulation_use_case = create_mocked_run_simulation_use_case(
        ohlcv_btc_20240122T075000_20240122T075500_1min_price_decrease_iterator,
        funding_rate_btc_20240122T075000_20240122T081000_1min_iterator,
    )
    start_time = datetime.fromisoformat("2024-01-22T07:50:00")
    end_time = datetime.fromisoformat("2024-01-22T07:55:00")
    timeframe = Timeframe.ONE_MIN
    symbol = Symbol.BTCUSD
    account_100_long_500usd.balance = 4.0
    result_simulation = run_simulation_use_case.run(
        start_time, end_time, timeframe, symbol, account_100_long_500usd
    )

    # Assert
    assert (
        result_simulation.name
        == expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.name
    )
    assert (
        result_simulation.simulation_start_ts
        == expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.simulation_start_ts
    )
    assert (
        result_simulation.simulation_end_ts
        == expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.simulation_end_ts
    )
    assert (
        result_simulation.timeframe
        == expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.timeframe
    )
    assert (
        result_simulation.symbol
        == expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.symbol
    )
    assert len(result_simulation.account_snapshots) == len(
        expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.account_snapshots
    )
    for i, snapshot in enumerate(result_simulation.account_snapshots):
        expected_snapshot = expected_simulation_20240122T075000_20240122T075500_1min_account_4_long_500usd.account_snapshots[
            i
        ]
        assert snapshot.ts == expected_snapshot.ts
        assert snapshot.account.balance == expected_snapshot.account.balance
        assert len(snapshot.account.positions) == len(
            expected_snapshot.account.positions
        )
        for j, position in enumerate(snapshot.account.positions):
            expected_position = expected_snapshot.account.positions[j]
            # assert position.open_ts == expected_position.open_ts  # This is a detail for now
            assert position.symbol == expected_position.symbol
            assert position.side == expected_position.side
            assert position.quantity == expected_position.quantity
            assert position.entry_price == expected_position.entry_price
            assert position.avg_price == expected_position.avg_price
            # assert position.trade.ts == expected_position.trade.ts  # This is a detail for now
            assert position.trade.symbol == expected_position.trade.symbol
            assert position.trade.type == expected_position.trade.type
            assert position.trade.quantity == expected_position.trade.quantity
            assert position.trade.price == expected_position.trade.price
            assert position.trade.fee == expected_position.trade.fee
            assert position.unrealized_pnl == expected_position.unrealized_pnl
            assert position.funding_rate_costs == expected_position.funding_rate_costs
            assert position.initial_margin == expected_position.initial_margin
            assert position.maintenance_margin == expected_position.maintenance_margin
            assert position.effective_leverage == expected_position.effective_leverage
            assert position.liquidation_price == expected_position.liquidation_price


@pytest.fixture
def expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd():
    account_snapshots = [
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:59:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.5,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:00:00").timestamp(),
            account=Account(
                balance=100.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.999499999999971,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.0,
                        liquidation_price=40200.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:01:00").timestamp(),
            account=Account(
                balance=99.95,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.4985004999999365,
                        funding_rate_costs=[0.05],
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.002501250625312,
                        liquidation_price=40205.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:02:00").timestamp(),
            account=Account(
                balance=99.95,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.9970019994999166,
                        funding_rate_costs=[0.05],
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.002501250625312,
                        liquidation_price=40205.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:03:00").timestamp(),
            account=Account(
                balance=99.95,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-2.4950049975004367,
                        funding_rate_costs=[0.05],
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=5.002501250625312,
                        liquidation_price=40205.0,
                    )
                ],
            ),
        ),
    ]
    simulation = Simulation(
        name="2024-01-22T07-58-00_2024-01-22T08-02-00_1m_BTC_USDT_USDT",
        simulation_start_ts=datetime.fromisoformat("2024-01-22T07:58:00").timestamp(),
        simulation_end_ts=datetime.fromisoformat("2024-01-22T08:02:00").timestamp(),
        timeframe=Timeframe.ONE_MIN,
        symbol=Symbol.BTCUSD,
        account_snapshots=account_snapshots,
    )
    return simulation


def test_run_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd(
    ohlcv_btc_20240122T075800_20240122T080200_1min_price_decrease_iterator: Iterator[
        OHLCV
    ],
    funding_rate_btc_20240122T075000_20240122T081000_1min_iterator: Iterator[
        FundingRate
    ],
    create_mocked_run_simulation_use_case: Callable[
        [Iterator[OHLCV], Iterator[FundingRate]], RunSimulation
    ],
    account_100_long_500usd: Account,
    expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd: Simulation,
):
    """Run a simulation with five bars of data, open position, settle funding rate costs."""
    # Test
    run_simulation_use_case = create_mocked_run_simulation_use_case(
        ohlcv_btc_20240122T075800_20240122T080200_1min_price_decrease_iterator,
        funding_rate_btc_20240122T075000_20240122T081000_1min_iterator,
    )
    start_time = datetime.fromisoformat("2024-01-22T07:58:00")
    end_time = datetime.fromisoformat("2024-01-22T08:02:00")
    timeframe = Timeframe.ONE_MIN
    symbol = Symbol.BTCUSD
    result_simulation = run_simulation_use_case.run(
        start_time, end_time, timeframe, symbol, account_100_long_500usd
    )

    # Assert
    assert (
        result_simulation.name
        == expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.name
    )
    assert (
        result_simulation.simulation_start_ts
        == expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.simulation_start_ts
    )
    assert (
        result_simulation.simulation_end_ts
        == expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.simulation_end_ts
    )
    assert (
        result_simulation.timeframe
        == expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.timeframe
    )
    assert (
        result_simulation.symbol
        == expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.symbol
    )
    assert len(result_simulation.account_snapshots) == len(
        expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.account_snapshots
    )
    for i, snapshot in enumerate(result_simulation.account_snapshots):
        expected_snapshot = expected_simulation_20240122T075800_20240122T080200_1min_account_100_long_500usd.account_snapshots[
            i
        ]
        assert snapshot.ts == expected_snapshot.ts
        assert snapshot.account.balance == expected_snapshot.account.balance
        assert len(snapshot.account.positions) == len(
            expected_snapshot.account.positions
        )
        for j, position in enumerate(snapshot.account.positions):
            expected_position = expected_snapshot.account.positions[j]
            # assert position.open_ts == expected_position.open_ts  # This is a detail for now
            assert position.symbol == expected_position.symbol
            assert position.side == expected_position.side
            assert position.quantity == expected_position.quantity
            assert position.entry_price == expected_position.entry_price
            assert position.avg_price == expected_position.avg_price
            # assert position.trade.ts == expected_position.trade.ts  # This is a detail for now
            assert position.trade.symbol == expected_position.trade.symbol
            assert position.trade.type == expected_position.trade.type
            assert position.trade.quantity == expected_position.trade.quantity
            assert position.trade.price == expected_position.trade.price
            assert position.trade.fee == expected_position.trade.fee
            assert position.unrealized_pnl == expected_position.unrealized_pnl
            assert position.funding_rate_costs == expected_position.funding_rate_costs
            assert position.initial_margin == expected_position.initial_margin
            assert position.maintenance_margin == expected_position.maintenance_margin
            assert position.effective_leverage == expected_position.effective_leverage
            assert position.liquidation_price == expected_position.liquidation_price


@pytest.fixture
def expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd():
    account_snapshots = [
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:59:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.5,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:00:00").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-0.999499999999971,
                        funding_rate_costs=None,
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=125.0,
                        liquidation_price=49800.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:01:00").timestamp(),
            account=Account(
                balance=3.95,
                positions=[
                    Position(
                        open_ts=datetime.fromisoformat(
                            "2024-01-22T07:57:00"
                        ).timestamp(),
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=datetime.fromisoformat(
                                "2024-01-22T07:57:00"
                            ).timestamp(),
                            symbol=Symbol.BTCUSD,
                            type=Trade.BUY,
                            quantity=0.01,
                            price=50000.0,
                            fee=0.25,
                        ),
                        unrealized_pnl=-1.4985004999999365,
                        funding_rate_costs=[0.05],
                        initial_margin=4.0,
                        maintenance_margin=2.0,
                        effective_leverage=126.58227848101265,
                        liquidation_price=49805.0,
                    )
                ],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:02:00").timestamp(),
            account=Account(
                balance=1.9529980005000835,
                positions=[],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:03:00").timestamp(),
            account=Account(
                balance=1.9529980005000835,
                positions=[],
            ),
        ),
    ]
    simulation = Simulation(
        name="2024-01-22T07-58-00_2024-01-22T08-02-00_1m_BTC_USDT_USDT",
        simulation_start_ts=datetime.fromisoformat("2024-01-22T07:58:00").timestamp(),
        simulation_end_ts=datetime.fromisoformat("2024-01-22T08:02:00").timestamp(),
        timeframe=Timeframe.ONE_MIN,
        symbol=Symbol.BTCUSD,
        account_snapshots=account_snapshots,
    )
    return simulation


def test_run_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd(
    ohlcv_btc_20240122T075800_20240122T080200_1min_price_decrease_iterator: Iterator[
        OHLCV
    ],
    funding_rate_btc_20240122T075000_20240122T081000_1min_iterator: Iterator[
        FundingRate
    ],
    create_mocked_run_simulation_use_case: Callable[
        [Iterator[OHLCV], Iterator[FundingRate]], RunSimulation
    ],
    account_100_long_500usd: Account,
    expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd: Simulation,
):
    """Run a simulation with five bars of data, open position, 
    settle funding rate costs, liquidate position."""
    # Test
    run_simulation_use_case = create_mocked_run_simulation_use_case(
        ohlcv_btc_20240122T075800_20240122T080200_1min_price_decrease_iterator,
        funding_rate_btc_20240122T075000_20240122T081000_1min_iterator,
    )
    start_time = datetime.fromisoformat("2024-01-22T07:58:00")
    end_time = datetime.fromisoformat("2024-01-22T08:02:00")
    timeframe = Timeframe.ONE_MIN
    symbol = Symbol.BTCUSD
    account_100_long_500usd.balance = 4.0
    result_simulation = run_simulation_use_case.run(
        start_time, end_time, timeframe, symbol, account_100_long_500usd
    )

    # Assert
    assert (
        result_simulation.name
        == expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.name
    )
    assert (
        result_simulation.simulation_start_ts
        == expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.simulation_start_ts
    )
    assert (
        result_simulation.simulation_end_ts
        == expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.simulation_end_ts
    )
    assert (
        result_simulation.timeframe
        == expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.timeframe
    )
    assert (
        result_simulation.symbol
        == expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.symbol
    )
    assert len(result_simulation.account_snapshots) == len(
        expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.account_snapshots
    )
    for i, snapshot in enumerate(result_simulation.account_snapshots):
        expected_snapshot = expected_simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd.account_snapshots[
            i
        ]
        assert snapshot.ts == expected_snapshot.ts
        assert snapshot.account.balance == expected_snapshot.account.balance
        assert len(snapshot.account.positions) == len(
            expected_snapshot.account.positions
        )
        for j, position in enumerate(snapshot.account.positions):
            expected_position = expected_snapshot.account.positions[j]
            # assert position.open_ts == expected_position.open_ts  # This is a detail for now
            assert position.symbol == expected_position.symbol
            assert position.side == expected_position.side
            assert position.quantity == expected_position.quantity
            assert position.entry_price == expected_position.entry_price
            assert position.avg_price == expected_position.avg_price
            # assert position.trade.ts == expected_position.trade.ts  # This is a detail for now
            assert position.trade.symbol == expected_position.trade.symbol
            assert position.trade.type == expected_position.trade.type
            assert position.trade.quantity == expected_position.trade.quantity
            assert position.trade.price == expected_position.trade.price
            assert position.trade.fee == expected_position.trade.fee
            assert position.unrealized_pnl == expected_position.unrealized_pnl
            assert position.funding_rate_costs == expected_position.funding_rate_costs
            assert position.initial_margin == expected_position.initial_margin
            assert position.maintenance_margin == expected_position.maintenance_margin
            assert position.effective_leverage == expected_position.effective_leverage
            assert position.liquidation_price == expected_position.liquidation_price

# TODO: do integration test without mocking data or objects
