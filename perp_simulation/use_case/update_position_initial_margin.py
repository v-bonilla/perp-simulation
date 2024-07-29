import logging

from perp_simulation.constant import BINANCE_FUTURES_BTC_LEVERAGE, Symbol
from perp_simulation.entity.position import Position


class UpdatePositionInitialMargin:
    """Update the initial margin of a position.

    - Actor: User
    - Scenario:
        1. The system retrieves the market leverage. For the moment, it's fixed.
        2. The system calculates the initial margin of the position.
        3. The system returns the updated position.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def update_initial_margin(self, position: Position) -> Position:
        """Get the initial margin of a position.

        Args:
            position: The position to get the initial margin.
        Returns:
            The updated position with the initial margin.
        """
        self.logger.info("Getting initial margin for position: %s", position)
        notional_value = position.quantity * position.avg_price
        self.logger.debug("Position notional value: %s", notional_value)
        leverage = self._get_market_leverage(position.symbol)
        self.logger.debug("Market leverage: %s", leverage)
        initial_margin = notional_value / leverage
        self.logger.debug("Initial margin: %s", initial_margin)
        position.initial_margin = initial_margin
        self.logger.info("Position updated with initial margin: %s", position)
        return position

    def _get_market_leverage(self, symbol: str) -> float:
        """Get the market leverage for a symbol.

        This is a temporal implementation. In a real system,
        this should be fetched from a data repository.

        Args:
            symbol: The symbol to get the leverage.
        Returns:
            The leverage for the symbol.
        """
        self.logger.debug("Getting market leverage for symbol: %s", symbol)
        if not symbol == Symbol.BTCUSD:
            raise ValueError(f"Unknown symbol: {symbol}")
        return BINANCE_FUTURES_BTC_LEVERAGE
