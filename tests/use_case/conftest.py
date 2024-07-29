# pylint: disable=redefined-outer-name, missing-module-docstring, missing-function-docstring
from datetime import datetime

import pytest

from perp_simulation.constant import BINANCE_FUTURES_BTC_LEVERAGE, BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE, BINANCE_FUTURES_TAKER_FEE_PCT, Symbol
from perp_simulation.entity.account import Account
from perp_simulation.entity.position import Position
from perp_simulation.entity.trade import Trade

# TODO: Change to UTC
BOY_2024_TS = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp()


def _create_2024_btc_buy_trade(quantity: float, price: float) -> Trade:
    fee = quantity * price * BINANCE_FUTURES_TAKER_FEE_PCT
    return Trade(
        ts=BOY_2024_TS,
        symbol=Symbol.BTCUSD,
        type=Trade.BUY,
        quantity=quantity,
        price=price,
        fee=fee,
    )


@pytest.fixture
def trade_buy_500usd() -> Trade:
    quantity = 0.01  # small quantity
    price = 50000.0
    trade = _create_2024_btc_buy_trade(quantity, price)
    return trade


@pytest.fixture
def trade_buy_50kusd() -> Trade:
    quantity = 1.0  # large quantity
    price = 50000.0
    trade = _create_2024_btc_buy_trade(quantity, price)
    return trade


@pytest.fixture
def position_long_500usd(trade_buy_500usd: Trade) -> Position:
    return Position(
        open_ts=trade_buy_500usd.ts,
        symbol=Symbol.BTCUSD,
        side=Position.LONG,
        quantity=trade_buy_500usd.quantity,
        entry_price=trade_buy_500usd.price,
        avg_price=trade_buy_500usd.price,
        trade=trade_buy_500usd,
    )


@pytest.fixture
def position_long_50kusd(trade_buy_50kusd: Trade) -> Position:
    return Position(
        open_ts=trade_buy_500usd.ts,
        symbol=Symbol.BTCUSD,
        side=Position.LONG,
        quantity=trade_buy_50kusd.quantity,
        entry_price=trade_buy_50kusd.price,
        avg_price=trade_buy_50kusd.price,
        trade=trade_buy_50kusd,
    )


@pytest.fixture
def account_100_no_positions() -> Account:
    return Account(
        balance=100.0,
    )


@pytest.fixture
def account_10k_no_positions() -> Account:
    return Account(
        balance=10000.0,
    )


@pytest.fixture
def account_100_long_500usd(
    account_100_no_positions: Account, position_long_500usd: Position
) -> Account:
    position_notional_value = position_long_500usd.quantity * position_long_500usd.avg_price
    position_initial_margin = position_notional_value / BINANCE_FUTURES_BTC_LEVERAGE
    position_maintenance_margin = position_notional_value * BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE
    position_effective_leverage = position_notional_value / account_100_no_positions.balance
    position_liquidation_price = 40200.0
    # Update position
    position_long_500usd.initial_margin = position_initial_margin
    position_long_500usd.maintenance_margin = position_maintenance_margin
    position_long_500usd.effective_leverage = position_effective_leverage
    position_long_500usd.liquidation_price = position_liquidation_price
    # Add position to account
    account_100_no_positions.add_position(position_long_500usd)
    return account_100_no_positions
