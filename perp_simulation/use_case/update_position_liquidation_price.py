import logging

from perp_simulation.entity.position import Position


class UpdatePositionLiquidationPrice:
    """Update the liquidation price of a position.

    - Actor: User
    - Scenario:
        1. The system retrieves the account balance. For the moment, it's an argument.
        2. The system calculates the liquidation price of the position.
        3. The system returns the updated position.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def update_liquidation_price(
        self, position: Position, account_balance: float
    ) -> Position:
        """Get the liquidation price of a position.

        Args:
            position: The position to get the liquidation price.
            account_balance: The account balance.
        Returns:
            The updated position with the liquidation price.
        """
        self.logger.info("Getting liquidation price of position: %s", position)
        liquidation_price = self._calculate_liquidation_price(position, account_balance)
        self.logger.debug("Liquidation price %s", liquidation_price)
        position.liquidation_price = liquidation_price
        self.logger.info("Position updated with liquidation price: %s", position)
        return position

    def _calculate_liquidation_price(
        self, position: Position, account_balance: float
    ) -> float:
        """Calculate the liquidation price for a position.

        The liquidation price is the price where the unrealized pnl of the position is
        inverse to the available balance (meaning that when realized that pnl, the balance is 0).
        The available balance in a cross margin account needs to
        take into account the maintenance margin.

        The formula to calculate the liquidation price is as follows:

        1. Let available_balance = account_balance - position.maintenance_margin
        2. available_balance + (liquidation_price - position.avg_price) * position.quantity = 0
        3. available_balance = - (liquidation_price - position.avg_price) * position.quantity
        4. available_balance / position.quantity = - (liquidation_price - position.avg_price)
        5. - (available_balance / position.quantity) = liquidation_price - position.avg_price
        6. - (available_balance / position.quantity) + position.avg_price = liquidation_price
        """
        if position.maintenance_margin is None:
            raise ValueError(
                "Maintenance margin is None and it's needed to calculate the liquidation price"
            )
        self.logger.debug(
            "Calculating liquidation price for position %s with account balance %s",
            position,
            account_balance,
        )
        available_balance = account_balance - position.maintenance_margin
        self.logger.debug("Available balance: %s", available_balance)
        liquidation_price = (
            -(available_balance / position.quantity) + position.avg_price
        )
        self.logger.debug("Liquidation price: %s", liquidation_price)
        return liquidation_price
