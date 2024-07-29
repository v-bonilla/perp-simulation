import logging

from perp_simulation.constant import BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE, Symbol
from perp_simulation.entity.position import Position


class UpdatePositionMaintenanceMargin:
    """Update the maintenance margin of a position.

    - Actor: User
    - Scenario:
        1. The system retrieves the maintenance margin ratio. For the moment, it's fixed.
        2. The system calculates the maintenance margin of the position.
        3. The system returns the updated position.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def update_maintenance_margin(self, position: Position) -> Position:
        """Get the maintenance margin of a position.

        Args:
            position: The position to get the maintenance margin.
        Returns:
            The updated position with the maintenance margin.
        """
        self.logger.info("Getting maintenance margin for position: %s", position)
        position_notional_value = position.quantity * position.avg_price
        self.logger.debug("Position notional value: %s", position_notional_value)
        maintenance_margin_rate = self._get_market_maintenance_margin_rate(
            position.symbol
        )
        self.logger.debug("Market maintenance margin rate: %s", maintenance_margin_rate)
        maintenance_margin = position_notional_value * maintenance_margin_rate
        self.logger.debug("Maintenance margin: %s", maintenance_margin)
        position.maintenance_margin = maintenance_margin
        self.logger.info("Position updated with maintenance margin: %s", position)
        return position

    def _get_market_maintenance_margin_rate(self, symbol: str) -> float:
        """Get the market maintenance margin rate for a symbol.

        This is a temporal implementation. In a real system,
        this should be fetched from a data repository.

        Args:
            symbol: The symbol to get the maintenance margin rate.
        Returns:
            The maintenance margin rate for the symbol.
        """
        self.logger.debug(
            "Getting market maintenance margin rate for symbol: %s", symbol
        )
        if not symbol == Symbol.BTCUSD:
            raise ValueError(f"Unknown symbol: {symbol}")
        return BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE
