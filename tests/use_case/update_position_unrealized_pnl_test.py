# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.entity.position import Position
from perp_simulation.use_case.update_position_unrealized_pnl import (
    UpdatePositionUnrealizedPnl,
)


@pytest.fixture
def update_position_unrealized_pnl_use_case():
    return UpdatePositionUnrealizedPnl()


@pytest.mark.parametrize(
    "market_price, expected_unrealized_pnl",
    [
        (50000.0, 0.0),
        (51000.0, 10.0),
        (40000.0, -100.0),
    ],
)
def test_update_position_unrealized_pnl(
    update_position_unrealized_pnl_use_case: UpdatePositionUnrealizedPnl,
    position_long_500usd: Position,
    market_price: float,
    expected_unrealized_pnl: float,
) -> None:
    result_position = update_position_unrealized_pnl_use_case.update_unrealized_pnl(
        position_long_500usd, market_price
    )
    assert result_position.unrealized_pnl == expected_unrealized_pnl
