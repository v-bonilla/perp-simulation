import logging
from datetime import datetime

from perp_simulation.constant import BINANCE_FUTURES_TAKER_FEE_PCT, Symbol, Timeframe
from perp_simulation.entity.account import Account
from perp_simulation.entity.position import Position
from perp_simulation.entity.trade import Trade
from perp_simulation.gateway.funding_rate_repository import FundingRateRepository
from perp_simulation.gateway.ohlcv_repository import OHLCVRepository
from perp_simulation.gateway.simulation_serializer import SimulationSerializer
from perp_simulation.use_case.liquidate_positions import LiquidatePositions
from perp_simulation.use_case.make_account_snapshot import MakeAccountSnapshot
from perp_simulation.use_case.open_cross_margin_position import OpenCrossMarginPosition
from perp_simulation.use_case.run_simulation import RunSimulation
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


def setup_run_simulation_use_case(data_base_path: str) -> RunSimulation:
    # Repositories
    ohlcv_repository = OHLCVRepository(data_base_path)
    funding_rate_repository = FundingRateRepository(data_base_path)

    # Use cases
    update_position_initial_margin_use_case = UpdatePositionInitialMargin()
    update_position_maintenance_margin_use_case = UpdatePositionMaintenanceMargin()
    update_position_effective_leverage_use_case = UpdatePositionEffectiveLeverage()
    update_position_liquidation_price_use_case = UpdatePositionLiquidationPrice()
    update_position_unrealized_pnl_use_case = UpdatePositionUnrealizedPnl()
    open_cross_margin_position_use_case = OpenCrossMarginPosition(
        update_position_initial_margin_use_case=update_position_initial_margin_use_case,
        update_position_maintenance_margin_use_case=update_position_maintenance_margin_use_case,
        update_position_effective_leverage_use_case=update_position_effective_leverage_use_case,
        update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
    )
    liquidate_position_use_case = LiquidatePositions(
        update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
        update_position_unrealized_pnl_use_case=update_position_unrealized_pnl_use_case,
    )
    run_simulation_use_case = RunSimulation(
        ohlcv_repository=ohlcv_repository,
        funding_rate_repository=funding_rate_repository,
        open_cross_margin_position_use_case=open_cross_margin_position_use_case,
        settle_funding_rate_costs_use_case=SettleFundingRateCosts(),
        update_position_unrealized_pnl_use_case=UpdatePositionUnrealizedPnl(),
        update_position_initial_margin_use_case=update_position_initial_margin_use_case,
        update_position_maintenance_margin_use_case=update_position_maintenance_margin_use_case,
        update_position_effective_leverage_use_case=update_position_effective_leverage_use_case,
        update_position_liquidation_price_use_case=update_position_liquidation_price_use_case,
        liquidate_position_use_case=liquidate_position_use_case,
        make_account_snapshot_use_case=MakeAccountSnapshot(),
    )
    return run_simulation_use_case


def main(
    data_base_path: str,
    output_path: str,
    start_time: datetime,
    end_time: datetime,
    timeframe: str,
    symbol: str,
    account_balance: float,
    leverage: float,
    trade_price: float,
):
    run_simulation_use_case = setup_run_simulation_use_case(data_base_path)

    trade_ts = start_time.timestamp() - 60
    position_notional = account_balance * leverage
    trade_quantity = position_notional / trade_price
    trade_fee = position_notional * BINANCE_FUTURES_TAKER_FEE_PCT

    account = Account(
        balance=account_balance,
        positions=[
            Position(
                open_ts=trade_ts,
                symbol=Symbol.BTCUSD,
                side=Position.LONG,
                quantity=trade_quantity,
                entry_price=trade_price,
                avg_price=trade_price,
                trade=Trade(
                    ts=trade_ts,
                    symbol=Symbol.BTCUSD,
                    type=Trade.BUY,
                    quantity=trade_quantity,
                    price=trade_price,
                    fee=trade_fee,
                ),
            )
        ],
    )

    simulation_result = run_simulation_use_case.run(
        account=account,
        start_time=start_time,
        end_time=end_time,
        timeframe=timeframe,
        symbol=symbol,
    )

    output_file_path = f"{output_path}/simulation_result.json"
    simulation_json = SimulationSerializer.to_json(simulation_result)
    with open(output_file_path, "w", encoding="UTF-8") as output_file:
        output_file.write(simulation_json)


if __name__ == "__main__":
    # TODO: Add parsing of command line arguments

    # Config
    # TODO: configure log file
    logging.basicConfig(level=logging.DEBUG, filename="./logs/perp_simulation.log", filemode="w")

    # Data parameters
    DATA_BASE_PATH = "./data/binance-futures"
    OUTPUT_PATH = "./output"

    # Simulation parameters
    start_time = datetime.fromisoformat("2024-01-01T00:00:00Z")
    end_time = datetime.fromisoformat("2024-01-01T00:00:00Z")
    timeframe = Timeframe.ONE_MIN
    symbol = Symbol.BTCUSD

    # Account and position parameters
    account_balance = 10000.0
    leverage = 10.0
    trade_price = 42283.0

    main(
        DATA_BASE_PATH,
        OUTPUT_PATH,
        start_time,
        end_time,
        timeframe,
        symbol,
        account_balance,
        leverage,
        trade_price,
    )
