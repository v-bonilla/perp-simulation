import logging

from perp_simulation.constant import (
    BINANCE_FUTURES_BTC_LEVERAGE,
    BINANCE_FUTURES_BTC_MAINTENANCE_MARGIN_RATE,
    Symbol,
)
from perp_simulation.entity.account import Account
from perp_simulation.entity.position import Position
from perp_simulation.entity.trade import Trade
from perp_simulation.error import InsufficientBalanceError
from perp_simulation.use_case.update_position_effective_leverage import (
    UpdatePositionEffectiveLeverage,
)
from perp_simulation.use_case.update_position_initial_margin import (
    UpdatePositionInitialMargin,
)
from perp_simulation.use_case.update_position_liquidation_price import (
    UpdatePositionLiquidationPrice,
)
from perp_simulation.use_case.update_position_maintenance_margin import (
    UpdatePositionMaintenanceMargin,
)


class OpenCrossMarginPosition:
    """Open a cross margin position in the market.

    - Actor: User
    - Scenario:
        1. User provides the account and a trade.
        2. Checks that margin requirements are met.
        3. The system creates a position from the trade.
        4. The system adds the position to the account.
        5. The trade fees are deducted from the account balance.
        6. The system returns the updated account.
    - Preconditions:
        - The account has enough balance to cover the trade value and fees.
    """

    def __init__(
        self,
        update_position_initial_margin_use_case: UpdatePositionInitialMargin,
        update_position_maintenance_margin_use_case: UpdatePositionMaintenanceMargin,
        update_position_effective_leverage_use_case: UpdatePositionEffectiveLeverage,
        update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self._update_position_initial_margin = update_position_initial_margin_use_case
        self._update_position_maintenance_margin = (
            update_position_maintenance_margin_use_case
        )
        self._update_position_effective_leverage = (
            update_position_effective_leverage_use_case
        )
        self._update_position_liquidation_price = (
            update_position_liquidation_price_use_case
        )

    def open(self, account: Account, trade: Trade) -> Account:
        """Open a cross margin position.

        Currently, only long positions are supported.

        Args:
            account: The account to open the position.
            trade: The trade to open the position.
        Returns:
            The opened position.
        """
        if trade.type != Trade.BUY:
            raise NotImplementedError("Only long positions are supported.")

        position = Position.from_trade(trade)
        updated_position = self._update_position_initial_margin.update_initial_margin(
            position
        )

        # Create position first to be efficient when calculating initial margin
        # If Position were a persisted model (like with sqlalchemy)
        # this should not be done in this order!
        if not self._are_margin_requirements_and_costs_met(
            account.balance, trade.fee, updated_position.initial_margin
        ):
            raise InsufficientBalanceError()

        self.logger.info("Opening position with trade: %s; account: %s", trade, account)

        # Deduct trade fees from account balance
        account.update_balance(-trade.fee)
        self.logger.info("Account balance updated to %s", account.balance)

        # Update position account and market dependent metrics
        updated_position.unrealized_pnl = 0.0
        updated_position = (
            self._update_position_maintenance_margin.update_maintenance_margin(
                updated_position
            )
        )
        updated_position = (
            self._update_position_effective_leverage.update_effective_leverage(
                updated_position, account.balance
            )
        )
        updated_position = (
            self._update_position_liquidation_price.update_liquidation_price(
                updated_position, account.balance
            )
        )
        account.add_position(position)
        self.logger.info("Position opened: %s", position)

        return account

    def _are_margin_requirements_and_costs_met(
        self, account_balance: float, trade_cost: float, initial_margin_required: float
    ) -> bool:
        """Check if the initial margin requirements are met.

        For a long position, the balance of the account must be greater
        than the initial margin required.

        Args:
            account_balance: The account balance.
            trade: The trade to open the position.
        Returns:
            True if the balance is greater or equals than the margin requirements.
        """
        self.logger.debug(
            "Checking margin requirements for account balance: %s; trade cost: %s",
            account_balance,
            trade_cost,
        )
        self.logger.debug("Initial margin required: %s", initial_margin_required)
        costs = trade_cost
        self.logger.debug("Costs: %s", costs)

        total_requirements = initial_margin_required + costs
        self.logger.debug("Total requirements to open position: %s", total_requirements)
        return account_balance >= total_requirements
