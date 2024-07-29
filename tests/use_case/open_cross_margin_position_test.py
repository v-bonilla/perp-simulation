# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.entity.account import Account
from perp_simulation.entity.trade import Trade
from perp_simulation.error import InsufficientBalanceError
from perp_simulation.use_case.open_cross_margin_position import OpenCrossMarginPosition
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


@pytest.fixture
def open_cross_margin_position_use_case() -> OpenCrossMarginPosition:
    update_position_initial_margin_use_case = UpdatePositionInitialMargin()
    update_position_maintenance_margin_use_case = UpdatePositionMaintenanceMargin()
    update_position_effective_leverage_use_case = UpdatePositionEffectiveLeverage()
    update_position_liquidation_price_use_case = UpdatePositionLiquidationPrice()
    op = OpenCrossMarginPosition(
        update_position_initial_margin_use_case,
        update_position_maintenance_margin_use_case,
        update_position_effective_leverage_use_case,
        update_position_liquidation_price_use_case,
    )
    return op


def test_open_cross_margin_position(
    open_cross_margin_position_use_case: OpenCrossMarginPosition,
    account_10k_no_positions: Account,
    trade_buy_500usd: Trade,
) -> None:
    updated_account = open_cross_margin_position_use_case.open(
        account_10k_no_positions, trade_buy_500usd
    )
    assert updated_account.balance == 9999.75  # initial balance - trade fees
    assert len(updated_account.positions) == 1

    position = updated_account.positions[0]
    assert position.open_ts == trade_buy_500usd.ts
    assert position.symbol == trade_buy_500usd.symbol
    assert position.side == position.LONG
    assert position.quantity == trade_buy_500usd.quantity
    assert position.entry_price == trade_buy_500usd.price
    assert position.avg_price == trade_buy_500usd.price
    assert position.trade == trade_buy_500usd
    assert position.unrealized_pnl == 0.0
    assert position.funding_rate_costs is None
    assert position.initial_margin == 4.0
    assert position.maintenance_margin == 2.0
    assert position.effective_leverage == 0.050001250031250784
    assert position.liquidation_price == -949775.0


def test_open_cross_margin_position_insufficient_balance(
    open_cross_margin_position_use_case: OpenCrossMarginPosition,
    account_100_no_positions: Account,
    trade_buy_50kusd: Trade,
) -> None:
    with pytest.raises(InsufficientBalanceError):
        open_cross_margin_position_use_case.open(
            account_100_no_positions, trade_buy_50kusd
        )
