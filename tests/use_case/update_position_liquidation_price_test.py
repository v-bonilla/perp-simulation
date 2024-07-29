# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.entity.account import Account
from perp_simulation.use_case.update_position_liquidation_price import (
    UpdatePositionLiquidationPrice,
)


@pytest.fixture
def update_position_liquidation_price_use_case() -> UpdatePositionLiquidationPrice:
    return UpdatePositionLiquidationPrice()


def test_update_position_liquidation_price_long_position(
    update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice,
    account_100_long_500usd: Account,
) -> None:
    position = account_100_long_500usd.positions[0]
    result_position = (
        update_position_liquidation_price_use_case.update_liquidation_price(
            position, account_100_long_500usd.balance
        )
    )
    assert result_position.liquidation_price == 40200.0
