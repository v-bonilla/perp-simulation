# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.constant import BINANCE_FUTURES_BTC_LEVERAGE
from perp_simulation.entity.position import Position
from perp_simulation.use_case.update_position_initial_margin import (
    UpdatePositionInitialMargin,
)


@pytest.fixture
def update_position_initial_margin_use_case() -> UpdatePositionInitialMargin:
    return UpdatePositionInitialMargin()


def test_update_position_initial_margin_long_position(
    update_position_initial_margin_use_case: UpdatePositionInitialMargin,
    position_long_500usd: Position,
) -> None:
    result_position = update_position_initial_margin_use_case.update_initial_margin(
        position_long_500usd
    )
    expected_initial_margin = (
        position_long_500usd.quantity
        * position_long_500usd.avg_price
        / BINANCE_FUTURES_BTC_LEVERAGE
    )
    assert result_position.initial_margin == expected_initial_margin
