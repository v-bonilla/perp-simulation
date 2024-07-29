import logging

from perp_simulation.entity.position import Position


class UpdatePositionEffectiveLeverage:
    """Update the effective leverage of a position.

    - Actor: User
    - Scenario:
        1. The system retrieves the account balance. For the moment, it's an argument.
        2. The system calculates the effective leverage of the position.
        3. The system returns the updated position.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def update_effective_leverage(
        self, position: Position, account_balance: float
    ) -> Position:
        """Get the effective leverage of a position.

        Args:
            position: The position to get the effective leverage.
            account_balance: The account balance.
        Returns:
            The updated position with the effective leverage.
        """
        self.logger.info("Getting effective leverage of position: %s", position)
        position_notional_value = position.quantity * position.avg_price
        self.logger.debug("Position notional value: %s", position_notional_value)
        effective_leverage = position_notional_value / account_balance
        self.logger.debug("Effective leverage: %s", effective_leverage)
        position.effective_leverage = effective_leverage
        self.logger.info("Position updated with effective leverage: %s", position)
        return position
