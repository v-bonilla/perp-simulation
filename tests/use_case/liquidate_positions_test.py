# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.entity.account import Account
from perp_simulation.use_case.liquidate_positions import LiquidatePositions
from perp_simulation.use_case.update_position_liquidation_price import (
    UpdatePositionLiquidationPrice,
)
from perp_simulation.use_case.update_position_unrealized_pnl import (
    UpdatePositionUnrealizedPnl,
)


@pytest.fixture
def liquidate_positions_use_case() -> LiquidatePositions:
    update_position_liquidation_price_use_case = UpdatePositionLiquidationPrice()
    update_position_unrealized_pnl_use_case = UpdatePositionUnrealizedPnl()
    return LiquidatePositions(
        update_position_liquidation_price_use_case,
        update_position_unrealized_pnl_use_case,
    )


def test_liquidate_positions_no_positions(
    liquidate_positions_use_case: LiquidatePositions, account_100_no_positions: Account
) -> None:
    result_account = liquidate_positions_use_case.liquidate(
        account_100_no_positions, 50000.0
    )
    assert result_account == account_100_no_positions


def test_liquidate_positions_long_position_not_to_liquidate(
    liquidate_positions_use_case: LiquidatePositions, account_100_long_500usd: Account
) -> None:
    result_account = liquidate_positions_use_case.liquidate(
        account_100_long_500usd, 100000.0
    )
    assert result_account == account_100_long_500usd


def test_liquidate_positions_long_position_to_liquidate(
    liquidate_positions_use_case: LiquidatePositions, account_100_long_500usd: Account
) -> None:
    position_maintenance_margin = account_100_long_500usd.positions[
        0
    ].maintenance_margin
    # Liquidation price for this position is 40200.0
    result_account = liquidate_positions_use_case.liquidate(
        account_100_long_500usd, 40200.0
    )
    assert result_account.balance == position_maintenance_margin
    assert len(result_account.positions) == 0
