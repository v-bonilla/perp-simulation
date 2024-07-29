from dataclasses import dataclass
from typing import List, Optional

from perp_simulation.entity.position import Position


@dataclass
class Account:
    """
    Represents an account in the trading system.
    """

    balance: float
    positions: Optional[List[Position]] = None

    def update_balance(self, amount: float) -> None:
        """
        Updates the balance of the account.
        """
        self.balance += amount

    def add_position(self, position: Position) -> None:
        """
        Adds a position to the account.
        """
        if self.positions is None:
            self.positions = []
        self.positions.append(position)

    def remove_position(self, position: Position) -> None:
        """
        Removes a position from the account.
        """
        if self.positions is not None:
            self.positions.remove(position)

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """
        Creates a new account from a dictionary.
        """
        positions = None
        if data["positions"]:
            positions = [Position.from_dict(p) for p in data["positions"]]
        return cls(balance=data["balance"], positions=positions)
