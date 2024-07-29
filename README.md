# perp-simulation

![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.2.1-blue)
![Plotly](https://img.shields.io/badge/Plotly-5.20.0-blue)
![Poetry](https://img.shields.io/badge/Poetry-1.7.0-blue)

## Table of Contents

- [Description](#description)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Run the Application](#run-the-application)
- [Roadmap](#roadmap)
- [Resources](#resources)
- [Software architecture](#software-architecture)
- [Objects](#objects)
- [Testing](#testing)

## Description

This projects aims to provide the tools to simulate the performance and risks of a strategy buying and selling perpetual futures to invest into the cryptocurrency markets.

Perpetual futures are derivative products introducing the concept of funding rate, which is the cost applied periodically to open positions so that the price of the product doesn't diverge from the underlying.

Funding rates along with the use of leverage make the strategies risk sensitive, and so the goal of this project is to shed some light on these questions.

This project is built following the [Clean Architecture](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) principles and applying Test-Driven-Development.

## Dependencies

- Python 3.12
- Pandas 2.2.1
- Plotly 5.20.0
- Poetry 1.7.0

## Installation

To set up `perp-simulation` on your local machine, follow these steps:

1. **Clone the repository**
    ```sh
    git clone https://github.com/v-bonilla/perp-simulation.git
    cd perp-simulation
    ```

2. **Set up the Python environment using Poetry**
    ```sh
    poetry install
    ```

## Run the Application

1. **Configure the values under the main block in `main.py`**

2. **Run:**

    ```sh
    poetry run python perp-simulation/main.py
    ```

## Roadmap

- Implement an integration test withouth mocking
- Review architecture of repositories in terms of resampling data and loading the file with the timeframe in the name. Think on use cases!
- Given that the data time is UTC, change datetime to UTC in tests and review its usage in the code.


## Resources

- https://click.palletsprojects.com/en/8.1.x/
- https://www.thedigitalcatbooks.com/pycabook-chapter-05/
- https://thedigitalcatonline.com/blog/2020/09/11/tdd-in-python-with-pytest-part-2/
- https://youtube.com/watch?v=C7MRkqP5NRI

## Software architecture

This project is built following the [Clean Architecture](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) principles and applying Test-Driven-Development.

### Use cases

- Open a cross margin position in the market.
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
- Settle the funding rate costs to the account balance.
    - Actor: Market.
    - Scenario:
        1. The system retrieves the funding rate from the market.
        2. For each position, the system calculates the funding rate fee.
        3. The system deducts the funding rate fees from the account balance.
    - Preconditions:
        - The account has open positions.
- Update the unrealized PnL of a position.
    - Actor: User
    - Scenario:
        1. The system retrieves the market price. For the moment, it's an argument.
        2. The system calculates the unrealized PnL of the position.
        3. The system returns the updated position.
- Update the initial margin of a position.
    - Actor: User
    - Scenario:
        1. The system retrieves the market leverage. For the moment, it's fixed.
        2. The system calculates the initial margin of the position.
        3. The system returns the updated position.
- Update the maintenance margin of a position.
    - Actor: User
    - Scenario:
        1. The system retrieves the maintenance margin ratio. For the moment, it's fixed.
        2. The system calculates the maintenance margin of the position.
        3. The system returns the updated position.
- Update the effective leverage of a position.
    - Actor: User
    - Scenario:
        1. The system retrieves the account balance. For the moment, it's an argument.
        2. The system calculates the effective leverage of the position.
        3. The system returns the updated position.
- Update the liquidation price of a position.
    - Actor: User
    - Scenario:
        1. The system retrieves the account balance. For the moment, it's an argument.
        2. The system calculates the liquidation price of the position.
        3. The system returns the updated position.
- Liquidate positions in the account.
    - Actor: Market.
    - Scenario:
        1. The system retrieves the market price.
        2. For each position, the system calculates the liquidation price.
        3. If the market price reaches the liquidation price, the system liquidates the position.
        4. Updates the account including balance and positions.
        5. The system returns the account.
- Make a snapshot of the account.
    - Actor: User
    - Scenario:
        1. The system retrieves the current ts. For the moment, it's an argument.
        2. Make a recursive copy of the account.
        3. The system returns the snapshot.
- Run a simulation over historical data.
    - Actor: User
    - Scenario:
        1. User provides the start and end time of the simulation, timeframe, symbol and an account.
        2. The system retrieves the data from the repository.
        3. For each bar of data, the system simulates:
            3.1. Updates account info including positions.
            3.2. Settles funding rate fees.
            3.3. Liquidates positions.
            3.4. Opens positions.
            3.5. Takes a snapshot of the account.
        4. Adds the snapshot to the simulation.
        5. The system returns the simulation.

## Objects

All timestamps (ts) are POSIX timestamps (integer number of seconds since 1970-01-01 00:00:00 UTC).

### Entities

```
- Trade # dataclass
    - Attributes:
        + ts: int
        + symbol: str
        + type: Literal[1, -1]  # buy or sell
        + quantity: float
        + price: float
        + fee: float
- Position # dataclass
    - Attributes:
        + open_ts: int
        + symbol: str
        + side: Literal[1, -1]  # long or short
        + quantity: float
        + entry_price: float
        + avg_price: float
        + trade: Trade
        <!-- Performance measures -->
        + unrealized_pnl: Optional[float]
        <!-- Cost measures -->
        + funding_rate_costs: Optional[List[float]]
        <!-- Risk measures -->
        + initial_margin: Optional[float]
        + maintenance_margin: Optional[float]
        + effective_leverage: Optional[float]
        + liquidation_price: Optional[float]
    - Methods:
        + from_trade(trade: Trade) -> None
        + add_funding_rate_cost(funding_rate_cost: float) -> None
- Account # dataclass
    - Attributes:
        + balance: float
        + positions: Optional[List[Position]]
    - Methods:
        + update_balance(amount: float) -> None
        + add_position(position: Position) -> None
        + remove_position(position: Position) -> None
- AccountSnapshot # dataclass
    - Attributes:
        + ts: int
        + account: Account
- Simulation # dataclass
    - Attributes:
        + name: str
        + simulation_start_ts: int
        + simulation_end_ts: int
        + timeframe: str
        + symbol: str
        <!-- + strategy -->
        + run_start_ts: Optional[int]
        + run_end_ts: Optional[int]
        + account_snapshots: Optional[List[Account]]
    - Methods:
        + add_account_snapshot(account_snapshot: AccountSnapshot) -> None
- OHLCV # dataclass
    - Attributes:
        + ts: int
        + symbol: str
        + open: float
        + high: float
        + low: float
        + close: float
        + volume: float
- FundingRate # dataclass
    - Attributes:
        + ts: int
        + symbol: str
        + rate: float
```

### Use cases

```
- OpenCrossMarginPosition
    - Attributes:
        - update_position_initial_margin_use_case: UpdatePositionInitialMargin
        - update_position_maintenance_margin_use_case: UpdatePositionMaintenanceMargin
        - update_position_effective_leverage_use_case: UpdatePositionEffectiveLeverage
        - update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice
    - Methods:
        + open(
            account: Account,
            trade: Trade,
        ) -> Account
        - _are_margin_requirements_and_costs_met(
            account: Account,
            trade: Trade,
        ) -> bool
- SettleFundingRateCosts
    - Attributes:
    - Methods:
        + settle(
            account: Account,
            funding_rate: float,
        ) -> Account
- UpdatePositionUnrealizedPnl
    - Attributes:
    - Methods:
        + get_unrealized_pnl(
            position: Position,
            market_price: float,
        ) -> float
- UpdatePositionInitialMargin
    - Attributes:
    - Methods:
        + get_initial_margin(
            position: Position,
        ) -> float
        - _get_market_leverage(
            symbol: str,
        ) -> float
- UpdatePositionMaintenanceMargin
    - Attributes:
    - Methods:
        + get_maintenance_margin(
            position: Position,
        ) -> float
        - _get_maintenance_margin_ratio(
            symbol: str,
        ) -> float
- UpdatePositionEffectiveLeverage
    - Attributes:
    - Methods:
        + get_effective_leverage(
            position: Position,
            account_balance: float,
        ) -> float
- UpdatePositionLiquidationPrice
    - Attributes:
    - Methods:
        + get_liquidation_price(
            position: Position,
            account_balance: float,
        ) -> float
- LiquidatePositions
    - Attributes:
        - update_position_liquidation_price_use_case: UpdatePositionLiquidationPrice
        - update_position_unrealized_pnl_use_case: UpdatePositionUnrealizedPnl
    - Methods:
        + liquidate(
            account: Account,
            market_price: float,
        ) -> Account
- MakeAccountSnapshot
    - Attributes:
    - Methods:
        + make(
            account: Account,
            ts: int,
        ) -> AccountSnapshot
- RunSimulation
    - Attributes:
        - _ohlcv_repository: OHLCVRepository
        - _funding_rate_repository: FundingRateRepository
    - Methods:
        + run(
            start_time: datetime,
            end_time: datetime,
            timeframe: str,
            symbol: str,
            account: Account,
        ) -> Simulation
        + simulate(
            start_time: datetime,
            end_time: datetime,
            timeframe: str,
            symbol: str,
            account: Account,
            ohlcv_data: Iterator[OHLCV],
            funding_rate_data: Iterator[FundingRate],
        ) -> Simulation
        + simulate_step(
            account: Account,
            ohlcv: OHLCV,
            funding_rate: FundingRate,
        ) -> Account
```

### Gateways

```
- HistoricalFeatherRepository
    - Attributes:
        - _data_base_path: Path
        - _data_type: str
        - _data_processing_service: DataProcessingService
    - Methods:
        - get_data_path(
            data_type: str,
            timeframe: str,
            symbol: str,
        ) -> Path
        - load_data(
            data_path: Path,
        ) -> pd.DataFrame
        - get_df(
            timeframe: str,
            symbol: str,
        ) -> pd.DataFrame
        + get_historical_dataframe(  # To implement in subclasses
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> pd.DataFrame
        + get_historical_iterator(  # To implement in subclasses
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> Iterator
- OHLCVRepository(HistoricalFeatherRepository)
    - Attributes:
    - Methods:
        + get_historical_dataframe(
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> pd.DataFrame
        + get_historical_data(
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> Iterator
- FundingRateRepository(HistoricalFeatherRepository)
    - Attributes:
    - Methods:
        + get_historical_dataframe(
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> pd.DataFrame
        + get_historical_data(
            symbol: str,
            start_time: datetime,
            timeframe: str,
        ) -> Iterator
- SimulationSerializer
    - Attributes:
    - Methods:
        + to_json(simulation: Simulation) -> str  # staticmethod
```

## Testing

This projects uses `pytest` for testing. The strategy is aimed to be simple and concise avoiding the need for complex testing suites, so we can iterate the project quickly.

### Testing strategy

To keep the testing suite simple, we will test the functionality objects with functional testing. This project considers functional testing as the definition from [Atlassian](https://www.atlassian.com/continuous-delivery/software-testing/types-of-software-testing):
> Functional tests focus on the business requirements of an application. They only verify the output of an action and do not check the intermediate states of the system when performing that action.

#### Testing cases (functional tests)

- OpenCrossMarginPosition
    - Open a position with a trade that meets the margin requirements for the account.
    - Open a position with a trade that doesn't meet the margin requirements for the account.
- SettleFundingRateCosts
    - Settle funding rate costs with no positions.
    - Settle positive funding rate costs with one long position.
    - Settle negative funding rate costs with one long position.
- UpdatePositionUnrealizedPnl
    - Get the unrealized PnL of a long position where the market price is equals to the avg price.
    - Get the unrealized PnL of a long position where the market price is greater than the avg price.
    - Get the unrealized PnL of a long position where the market price is less than the avg price.
- UpdatePositionInitialMargin
    - Get the initial margin of a long position.
- UpdatePositionMaintenanceMargin
    - Get the maintenance margin of a long position.
- UpdatePositionEffectiveLeverage
    - Get the effective leverage of a long position.
- UpdatePositionLiquidationPrice
    - Get the liquidation price of a long position.
- LiquidatePositions
    - Liquidate positions with no positions.
    - Liquidate positions with one position not to liquidate.
    - Liquidate positions with one position to liquidate.
- MakeAccountSnapshot
    - Make a snapshot of an account with no positions.
    - Make a snapshot of an account with one position.
- RunSimulation
    - Run a simulation with five bars of data, open position.
    - Run a simulation with five bars of data, open position, liquidate position.
    - Run a simulation with five bars of data, open position, settle funding rate costs.
    - Run a simulation with five bars of data, open position, settle funding rate costs, liquidate position.
- HistoricalFeatherRepository
    - Get historical OHLCV, 1min, five bars of data.
    - Get historical funding rate, 1min, two bars of data.
