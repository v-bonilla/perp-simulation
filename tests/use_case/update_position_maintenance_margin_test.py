# pylint: disable=redefined-outer-name
import pytest

from perp_simulation.constant import BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE
from perp_simulation.entity.position import Position
from perp_simulation.use_case.update_position_maintenance_margin import (
    UpdatePositionMaintenanceMargin,
)


@pytest.fixture
def update_position_maintenance_margin_use_case() -> UpdatePositionMaintenanceMargin:
    return UpdatePositionMaintenanceMargin()


def test_update_position_maintenance_margin_long_position(
    update_position_maintenance_margin_use_case: UpdatePositionMaintenanceMargin,
    position_long_500usd: Position,
) -> None:
    result_position = (
        update_position_maintenance_margin_use_case.update_maintenance_margin(
            position_long_500usd
        )
    )
    expected_maintenance_margin = (
        position_long_500usd.quantity
        * position_long_500usd.avg_price
        * BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE
    )
    assert result_position.maintenance_margin == expected_maintenance_margin
