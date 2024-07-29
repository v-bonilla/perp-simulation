import logging

from perp_simulation.entity.account import Account
from perp_simulation.use_case.update_position_liquidation_price import (
    UpdatePositionLiquidationPrice,
)
from perp_simulation.use_case.update_position_unrealized_pnl import (
    UpdatePositionUnrealizedPnl,
)


class LiquidatePositions:
    """Liquidate positions in the account.

    For now, the liquidation doesn't take into account liquidation fees.

    - Actor: Market.
    - Scenario:
        1. The system retrieves the market price. For the moment, it is an argument.
        2. For each position, the system calculates the liquidation price.
        3. If the market price reaches the liquidation price, the system liquidates the position.
        4. Updates the account including balance and positions.
        5. The system returns the account.
    """

    def __init__(
        self,
        update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice,
        update_position_unrealized_pnl_use_case: UpdatePositionUnrealizedPnl,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self._update_position_liquidation_price_use_case = (
            update_position_liquidation_price_use_case
        )
        self._update_position_unrealized_pnl_use_case = (
            update_position_unrealized_pnl_use_case
        )

    def liquidate(self, account: Account, market_price: float) -> Account:
        """Liquidate positions in the account.

        Args:
            account: The account to liquidate positions.
            market_price: The market price to liquidate positions.
        Returns:
            The updated account.
        """
        if account.positions is None:
            self.logger.info("No positions to liquidate")
            return account

        self.logger.info(
            "Liquidating positions with market price %s for account: %s",
            market_price,
            account,
        )
        for position in account.positions:
            # TODO get from position info
            updated_position = (
                self._update_position_liquidation_price_use_case.update_liquidation_price(
                    position, account.balance
                )
            )
            # TODO: set logging level to debug
            self.logger.info(
                "Liquidation price for position is %s",
                updated_position.liquidation_price,
            )
            if market_price <= updated_position.liquidation_price:
                self.logger.info(
                    "Liquidating position %s with market price %s",
                    position,
                    market_price,
                )
                # TODO create a trade and create a use case to close the position
                updated_position = (
                    self._update_position_unrealized_pnl_use_case.update_unrealized_pnl(
                        updated_position, market_price
                    )
                )
                account.update_balance(updated_position.unrealized_pnl)
                account.remove_position(position)
                self.logger.info(
                    "Position liquidated. Account balance updated to %s",
                    account.balance,
                )
        self.logger.info("Account and positions updated with liquidation")
        return account
