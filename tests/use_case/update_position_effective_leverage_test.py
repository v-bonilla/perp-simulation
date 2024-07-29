# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.entity.account import Account
from perp_simulation.use_case.update_position_effective_leverage import (
    UpdatePositionEffectiveLeverage,
)


@pytest.fixture
def update_position_effective_leverage_use_case() -> UpdatePositionEffectiveLeverage:
    return UpdatePositionEffectiveLeverage()


def test_update_position_effective_leverage_long_position(
    update_position_effective_leverage_use_case: UpdatePositionEffectiveLeverage,
    account_100_long_500usd: Account,
) -> None:
    position = account_100_long_500usd.positions[0]
    result_position = (
        update_position_effective_leverage_use_case.update_effective_leverage(
            position, account_100_long_500usd.balance
        )
    )
    expected_effective_leverage = (
        position.quantity * position.avg_price / account_100_long_500usd.balance
    )
    assert result_position.effective_leverage == expected_effective_leverage
