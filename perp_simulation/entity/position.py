from dataclasses import dataclass
from typing import List, Literal, Optional

from perp_simulation.entity.trade import Trade


@dataclass
class Position:
    """
    Represents a position in the trading system.
    """

    LONG = 1
    SHORT = -1

    open_ts: int
    symbol: str
    side: Literal[
        1, -1
    ]  # LONG or SHORT. TODO: make enum so it's accepted in the Literal exp
    quantity: float
    entry_price: float
    avg_price: float
    trade: Trade
    unrealized_pnl: Optional[float] = None
    funding_rate_costs: Optional[List[float]] = None
    initial_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    effective_leverage: Optional[float] = None
    liquidation_price: Optional[float] = None

    def add_funding_rate_cost(self, funding_rate_cost: float) -> None:
        """
        Adds a funding rate cost to the position.
        """
        if self.funding_rate_costs is None:
            self.funding_rate_costs = []
        self.funding_rate_costs.append(funding_rate_cost)

    @classmethod
    def from_trade(cls, trade: Trade) -> "Position":
        """
        Creates a new position from a trade.
        """
        side = cls.LONG if trade.type == Trade.BUY else cls.SHORT
        return cls(
            open_ts=trade.ts,
            symbol=trade.symbol,
            side=side,
            quantity=trade.quantity,
            entry_price=trade.price,
            avg_price=trade.price,
            trade=trade,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """
        Creates a new position from a dictionary.
        """
        funding_rate_costs = None
        if data["funding_rate_costs"]:
            funding_rate_costs = data["funding_rate_costs"]
        return cls(
            open_ts=data["open_ts"],
            symbol=data["symbol"],
            side=data["side"],
            quantity=data["quantity"],
            entry_price=data["entry_price"],
            avg_price=data["avg_price"],
            trade=Trade.from_dict(data["trade"]),
            unrealized_pnl=data["unrealized_pnl"],
            funding_rate_costs=funding_rate_costs,
            initial_margin=data["initial_margin"],
            maintenance_margin=data["maintenance_margin"],
            effective_leverage=data["effective_leverage"],
            liquidation_price=data["liquidation_price"],
        )
