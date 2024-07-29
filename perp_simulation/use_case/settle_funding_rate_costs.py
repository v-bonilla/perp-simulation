import logging

from perp_simulation.entity.account import Account
from perp_simulation.entity.position import Position


class SettleFundingRateCosts:
    """Settle the funding rate costs to the account balance.

    - Actor: Market.
    - Scenario:
        1. The system retrieves the funding rate from the market. For the moment, it is an argument.
        2. For each position, the system calculates the funding rate fee.
        3. The system deducts the funding rate fees from the account balance.
    - Preconditions:
        - The account has open positions.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def settle(self, account: Account, funding_rate: float) -> Account:
        """Settle the funding rate costs for each position in the account and
        updates position and account respective data.

        Args:
            account: The account to settle the funding rate costs.
            funding_rate: The funding rate to settle.
        Returns:
            The updated account.
        """
        if account.positions is None:
            self.logger.info("No positions to settle funding rate costs")
            return account

        self.logger.info(
            "Settling funding rate %s for account: %s", funding_rate, account
        )
        for position in account.positions:
            funding_rate_cost = self._calculate_funding_rate_cost(
                position, funding_rate
            )
            self.logger.info(
                "Adding funding rate cost %s to position %s",
                funding_rate_cost,
                position,
            )
            position.add_funding_rate_cost(funding_rate_cost)
            self.logger.info(
                "Updating account balance with funding rate cost %s", funding_rate_cost
            )
            account.update_balance(-funding_rate_cost)
        self.logger.info("Account and positions updated with funding rate costs")
        return account

    def _calculate_funding_rate_cost(
        self, position: Position, funding_rate: float
    ) -> float:
        """Calculate the funding rate cost for a position.

        If the funding rate is positive, the long positions pay the short positions.
        If the funding rate is negative, the short positions pay the long positions.

        Args:
            position: The position to calculate the funding rate cost.
            funding_rate: The funding rate to settle.
        Returns:
            The funding rate cost.
        """
        self.logger.debug(
            "Calculating funding rate cost for funding rate: %s; position: %s",
            funding_rate,
            position,
        )
        position_notional_value = position.quantity * position.avg_price
        self.logger.debug("Position notional value: %s", position_notional_value)
        funding_rate_cost = 0.0
        if position.side == Position.LONG:
            funding_rate_cost = funding_rate * position_notional_value
        elif position.side == Position.SHORT:
            funding_rate_cost = -funding_rate * position_notional_value
        else:
            raise ValueError("Invalid position side")
        self.logger.debug("Funding rate cost: %s", funding_rate_cost)
        return funding_rate_cost
