import logging
from datetime import datetime
from time import time
from typing import Iterator, Optional

from perp_simulation.constant import (
    BINANCE_FUTURES_BTC_FUNDING_RATE_FREQ,
    Symbol,
    Timeframe,
)
from perp_simulation.entity.account import Account
from perp_simulation.entity.funding_rate import FundingRate
from perp_simulation.entity.ohlcv import OHLCV
from perp_simulation.entity.simulation import Simulation
from perp_simulation.gateway.funding_rate_repository import FundingRateRepository
from perp_simulation.gateway.ohlcv_repository import OHLCVRepository
from perp_simulation.use_case.liquidate_positions import LiquidatePositions
from perp_simulation.use_case.make_account_snapshot import MakeAccountSnapshot
from perp_simulation.use_case.open_cross_margin_position import OpenCrossMarginPosition
from perp_simulation.use_case.settle_funding_rate_costs import SettleFundingRateCosts
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
from perp_simulation.use_case.update_position_unrealized_pnl import (
    UpdatePositionUnrealizedPnl,
)


class RunSimulation:
    """Run a simulation over historical data.

    - Actor: User
    - Scenario:
        1. User provides the start and end time of the simulation and an account.
        2. The system retrieves the data from the repository.
        3. For each bar of data, the system simulates:
            3.1. Updates account info including positions.
            3.2. Settles funding rate fees.
            3.3. Liquidates positions.
            3.4. Opens positions.
            3.5. Takes a snapshot of the account.
        4. Adds the snapshot to the simulation.
        5. The system returns the simulation.
    """

    def __init__(
        self,
        ohlcv_repository: OHLCVRepository,
        funding_rate_repository: FundingRateRepository,
        open_cross_margin_position_use_case: OpenCrossMarginPosition,
        settle_funding_rate_costs_use_case: SettleFundingRateCosts,
        update_position_unrealized_pnl_use_case: UpdatePositionUnrealizedPnl,
        update_position_initial_margin_use_case: UpdatePositionInitialMargin,
        update_position_maintenance_margin_use_case: UpdatePositionMaintenanceMargin,
        update_position_effective_leverage_use_case: UpdatePositionEffectiveLeverage,
        update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice,
        liquidate_position_use_case: LiquidatePositions,
        make_account_snapshot_use_case: MakeAccountSnapshot,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self._ohlcv_repository = ohlcv_repository
        self._funding_rate_repository = funding_rate_repository
        self._open_cross_margin_position_use_case = open_cross_margin_position_use_case
        self._settle_funding_rate_costs_use_case = settle_funding_rate_costs_use_case
        self._update_position_unrealized_pnl_use_case = (
            update_position_unrealized_pnl_use_case
        )
        self._update_position_initial_margin_use_case = (
            update_position_initial_margin_use_case
        )
        self._update_position_maintenance_margin_use_case = (
            update_position_maintenance_margin_use_case
        )
        self._update_position_effective_leverage_use_case = (
            update_position_effective_leverage_use_case
        )
        self._update_position_liquidation_price_use_case = (
            update_position_liquidation_price_use_case
        )
        self._liquidate_position_use_case = liquidate_position_use_case
        self._make_account_snapshot_use_case = make_account_snapshot_use_case

    def run(
        self,
        start_time: datetime,
        end_time: datetime,  # TODO: remove
        timeframe: str,
        symbol: str,
        account: Account,
    ) -> Simulation:
        """Run a simulation over historical data.

        Load historical data from the repository and runs the simulation.
        The simulation itself is done in the simulate method.

        Args:
            start_time (datetime): The start time of the simulation.
            end_time (datetime): The end time of the simulation.
            timeframe (str): The timeframe of the data.
            symbol (str): The symbol of the data.
            account (Account): The account to simulate.
        Returns:
            Simulation: The simulation.
        """
        self.logger.info(
            "Running simulation from %s to %s with timeframe %s and symbol %s and account %s",
            start_time,
            end_time,
            timeframe,
            symbol,
            account,
        )

        self.logger.info("Retrieving historical OHLCV data")
        ohlcv_iterator = self._ohlcv_repository.get_historical_data(
            symbol,
            start_time,
            timeframe,
        )
        self.logger.info("Retrieving historical funding rate data")
        funding_rate_iterator = self._funding_rate_repository.get_historical_data(
            symbol,
            start_time,
            timeframe,
        )

        self.logger.info("Simulating")
        simulation = self.simulate(
            start_time,
            end_time,
            timeframe,
            symbol,
            account,
            ohlcv_iterator,
            funding_rate_iterator,
        )
        self.logger.info("Running simulation completed")
        return simulation

    def simulate(
        self,
        start_time: datetime,
        end_time: datetime,
        timeframe: str,
        symbol: str,
        account: Account,
        ohlcv_iterator: Iterator,
        funding_rate_iterator: Iterator,
    ) -> Simulation:
        """Simulate the account over the historical data.

        Use OHLCV iterator (and it's ts) to iterate over the historical data in
        the main loop and simulate the account.
        The funding rate iterator is handled manually because it's not guaranteed
        to have the same length as the OHLCV iterator.

        The data is assumed to be in the same timeframe and covering the same period.

        Args:
            start_time (datetime): The start time of the simulation.
            end_time (datetime): The end time of the simulation.
            timeframe (str): The timeframe of the data.
            symbol (str): The symbol of the data.
            account (Account): The account to simulate.
            ohlcv_iterator (Iterator): The OHLCV data iterator.
            funding_rate_iterator (Iterator): The funding rate data iterator.
        Returns:
            Simulation: The simulation result.
        """
        run_start_ts = int(time())
        self.logger.debug(
            "Simulation parameters: %s %s %s %s",
            start_time,
            end_time,
            timeframe,
            symbol,
        )

        # Prepare the simulation result
        simulation_name = self._create_simulation_name(
            start_time, end_time, timeframe, symbol
        )
        self.logger.debug("Simulation name: %s", simulation_name)
        simulation_start_ts = start_time.timestamp()
        simulation_end_ts = end_time.timestamp()
        simulation = Simulation(
            name=simulation_name,
            simulation_start_ts=simulation_start_ts,
            simulation_end_ts=simulation_end_ts,
            timeframe=timeframe,
            symbol=symbol,
            run_start_ts=run_start_ts,
        )

        # Simulation
        self.logger.debug("Simulating account %s", account)
        timeframe_seconds = Timeframe.to_seconds(timeframe)
        funding_rate = next(funding_rate_iterator)
        for ohlcv in ohlcv_iterator:
            # TODO: downsample iterator of OHLCV to avoid this.
            #   Simulation should not be aware of matching the datapoints
            # Simulate the step with funding rate if it matches the OHLCV timestamp
            step_funding_rate = None
            if funding_rate.ts == ohlcv.ts:
                step_funding_rate = funding_rate

            # Simulate the step
            updated_account = self.simulate_step(account, ohlcv, step_funding_rate)
            self.logger.debug("Taking account snapshot for account %s", updated_account)

            # The account snapshot is taken after simulating the step, having the
            # data at the end of the step and so the timestamp should be the one
            # at the end of the step, i.e., the next timestamp
            account_snapshot_ts = ohlcv.ts + timeframe_seconds
            account_snapshot = self._make_account_snapshot_use_case.make(
                updated_account, account_snapshot_ts
            )
            simulation.add_account_snapshot(account_snapshot)

            # Get the next funding rate
            try:
                funding_rate = next(funding_rate_iterator)
            except StopIteration:
                self.logger.warning(
                    "No more funding rates, using the last one: %s", funding_rate
                )

        # Log the last datapoints to be able to check divergence in timestamps
        self.logger.debug(
            "Last datapoints: OHLCV=%s, funding rate=%s", ohlcv, funding_rate
        )

        self.logger.debug(
            "Made %s account snapshots", len(simulation.account_snapshots)
        )

        run_end_ts = int(time())
        simulation.run_end_ts = run_end_ts
        self.logger.info(
            "Simulation completed in %s seconds", run_end_ts - run_start_ts
        )
        return simulation

    def simulate_step(
        self,
        account: Account,
        ohlcv: OHLCV,
        funding_rate: Optional[FundingRate],
    ) -> Account:
        """Simulate a step for the account.

        Settle funding rate fees, update the account info, liquidate positions,
        open positions, and take a snapshot of the account.

        Args:
            account (Account): The account to simulate.
            ohlcv (OHLCV): The OHLCV data.
            funding_rate (FundingRate): The funding rate data.
        Returns:
            Account: The updated account.
        """
        self.logger.debug(
            "Simulating step for account %s with OHLCV %s and funding rate %s",
            account,
            ohlcv,
            funding_rate,
        )
        # Funding rate settlement is done at the beginning of the bar in the exchange
        updated_account = account
        if funding_rate is not None and funding_rate.rate is not None:
            self.logger.debug("Settling funding rate fees to account")
            updated_account = self._settle_funding_rate_costs_use_case.settle(
                updated_account, funding_rate.rate
            )
            self.logger.debug(
                "Settled funding rate fees to account %s", updated_account
            )

        account_balance = account.balance
        self.logger.debug("Using account balance %s to simulate step", account_balance)

        market_price = ohlcv.close
        self.logger.debug("Using close price %s to simulate step", market_price)

        self.logger.debug("Updating account info including positions")
        for position in updated_account.positions:
            self.logger.debug("Updating position %s", position)
            updated_position = position

            updated_position = (
                self._update_position_unrealized_pnl_use_case.update_unrealized_pnl(
                    updated_position, market_price
                )
            )
            updated_position = (
                self._update_position_initial_margin_use_case.update_initial_margin(
                    updated_position
                )
            )
            updated_position = self._update_position_maintenance_margin_use_case.update_maintenance_margin(
                updated_position
            )
            updated_position = self._update_position_effective_leverage_use_case.update_effective_leverage(
                updated_position, account_balance
            )
            updated_position = self._update_position_liquidation_price_use_case.update_liquidation_price(
                updated_position, account_balance
            )
            self.logger.debug("Updated position to %s", updated_position)

        self.logger.debug("Liquidating positions")
        updated_account = self._liquidate_position_use_case.liquidate(
            updated_account, market_price
        )
        self.logger.debug("Liquidated positions in account %s", updated_account)

        self.logger.debug("Getting signal")
        signal = self._get_signal()

        if signal != 0:
            self.logger.debug("Opening positions")
            updated_account = self._open_cross_margin_position_use_case.open(
                updated_account, ohlcv
            )

        self.logger.debug("Simulating step completed")
        return updated_account

    def _create_simulation_name(self, start_time, end_time, timeframe, symbol):
        """Create a simulation name based on the simulation parameters."""
        # TODO: add symbol and account name to the simulation name?
        start_time_str = start_time.isoformat().replace(":", "-")
        end_time_str = end_time.isoformat().replace(":", "-")
        normalized_symbol = Symbol.normalize(symbol)
        simulation_name = (
            f"{start_time_str}_{end_time_str}_{timeframe}_{normalized_symbol}"
        )

        return simulation_name

    def _get_signal(self) -> int:
        """Temporary method to get a signal for opening positions. TODO: implement"""
        return 0

    def _get_market_funding_rate_frequency(self) -> str:
        """Get the frequency of the market funding rate.

        This is a temporal implementation. In a real system,
        this should be fetched from a data repository.

        Args:
        Returns:
            The frequency of the market funding rate.
        """
        return BINANCE_FUTURES_BTC_FUNDING_RATE_FREQ
