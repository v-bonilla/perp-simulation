import logging

from perp_simulation.entity.position import Position


class UpdatePositionUnrealizedPnl:
    """Update the unrealized PnL of a position.

    - Actor: User
    - Scenario:
        1. The system retrieves the market price. For the moment, it is an argument.
        2. The system calculates the unrealized PnL of the position.
        3. The system returns the updated position.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def update_unrealized_pnl(self, position: Position, market_price: float) -> Position:
        """Get the unrealized PnL of a position.

        Args:
            position: The position to calculate the unrealized PnL.
            market_price: The market price to calculate the unrealized PnL.
        Returns:
            The updated position with the unrealized PnL.
        """
        self.logger.info(
            "Calculating unrealized PnL for position %s with market price %s",
            position,
            market_price,
        )
        price_diff = market_price - position.entry_price
        self.logger.info("Price diff: %s", price_diff)
        unrealized_pnl = price_diff * position.quantity
        self.logger.debug("Unrealized PnL: %s", unrealized_pnl)
        position.unrealized_pnl = unrealized_pnl
        self.logger.info("Position updated with unrealized PnL: %s", position)
        return position
