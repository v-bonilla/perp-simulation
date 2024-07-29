# pylint: disable=redefined-outer-name
from datetime import datetime

import pytest

from perp_simulation.constant import Symbol, Timeframe
from perp_simulation.entity.account import Account
from perp_simulation.entity.account_snapshot import AccountSnapshot
from perp_simulation.entity.position import Position
from perp_simulation.entity.simulation import Simulation
from perp_simulation.entity.trade import Trade
from perp_simulation.gateway.simulation_serializer import SimulationSerializer


@pytest.fixture
def simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd():
    trade_ts = datetime.fromisoformat("2024-01-22T07:57:00Z").timestamp()

    account_snapshots = [
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T07:59:00Z").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=trade_ts,
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=trade_ts,
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
            ts=datetime.fromisoformat("2024-01-22T08:00:00Z").timestamp(),
            account=Account(
                balance=4.0,
                positions=[
                    Position(
                        open_ts=trade_ts,
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=trade_ts,
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
            ts=datetime.fromisoformat("2024-01-22T08:01:00Z").timestamp(),
            account=Account(
                balance=3.95,
                positions=[
                    Position(
                        open_ts=trade_ts,
                        symbol=Symbol.BTCUSD,
                        side=Position.LONG,
                        quantity=0.01,
                        entry_price=50000.0,
                        avg_price=50000.0,
                        trade=Trade(
                            ts=trade_ts,
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
            ts=datetime.fromisoformat("2024-01-22T08:02:00Z").timestamp(),
            account=Account(
                balance=1.9529980005000835,
                positions=[],
            ),
        ),
        AccountSnapshot(
            ts=datetime.fromisoformat("2024-01-22T08:03:00Z").timestamp(),
            account=Account(
                balance=1.9529980005000835,
                positions=[],
            ),
        ),
    ]
    simulation = Simulation(
        name="2024-01-22T07-58-00_2024-01-22T08-02-00_1m_BTC_USDT_USDT",
        simulation_start_ts=datetime.fromisoformat("2024-01-22T07:58:00Z").timestamp(),
        simulation_end_ts=datetime.fromisoformat("2024-01-22T08:02:00Z").timestamp(),
        timeframe=Timeframe.ONE_MIN,
        symbol=Symbol.BTCUSD,
        account_snapshots=account_snapshots,
    )
    return simulation


def test_serialize_simulation_to_json(
    simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd: Simulation,
):
    json = SimulationSerializer.to_json(
        simulation_20240122T075800_20240122T080200_1min_account_4_long_500usd
    )
    # TODO: Add assertions
    assert True
